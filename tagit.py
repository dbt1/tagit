#!/usr/bin/env python3
"""
Automatic Git Tagging and Version Update with custom placeholders and additional parameters for major, micro, and patch,
with fallback logic if the primary scheme does not match the file format as expected.

This script automates tagging in Git and updates version numbers in various files based on defined versioning schemes.
It supports custom placeholders and allows overriding version parts. If the format in the specified file does not match
the expected scheme, the script attempts to find a fallback scheme. If a fallback is found, it logs an info message and
uses it. Otherwise, it warns that the format does not match.

Key Features:
- Determines version from latest Git tag or initial-version.
- Supports {micro} when using four-part versions.
- Overrides with --major, --micro, --patch.
- Attempts to update files based on versioning schemes.
- If the primary scheme does not match the file content as expected, tries to find an alternative scheme.
- Logs warnings and infos accordingly.

Date/time placeholders: {YYYY}, {YY}, {MM}, {DD}, {hh}, {mm}, {ss}
Version placeholders: {major}, {minor}, {micro}, {patch}
"""

import subprocess
import re
import os
import sys
import argparse
import logging
import json
from datetime import datetime
from git import Repo, GitCommandError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

VERSION_SCHEMES = [
    {
        "name": "ac_init",
        "patterns": {
            "version": r'(AC_INIT\(\[.*?\],\s*\[)\d+(\.\d+)+(\],\s*\[.*?\]\))'
        },
        "replacements": {
            "version": r'\g<1>{major}.{minor}.{patch}\g<3>'
        }
    },
    {
        "name": "version_assignment",
        "patterns": {
            "version": r'(VERSION|version)\s*=\s*"\d+(\.\d+)+"'
        },
        "replacements": {
            "version": r'\1="{major}.{minor}.{patch}"'
        }
    },
    {
        "name": "define_ver",
        "patterns": {
            "ver_major": r'define\(ver_major,\s*\d+\)',
            "ver_minor": r'define\(ver_minor,\s*\d+\)',
            "ver_micro": r'define\(ver_micro,\s*\d+\)',
            "ver_patch": r'define\(ver_patch,\s*\d+\)'
        },
        "replacements": {
            "ver_major": 'define(ver_major, {major})',
            "ver_minor": 'define(ver_minor, {minor})',
            "ver_micro": 'define(ver_micro, {micro})',
            "ver_patch": 'define(ver_patch, {patch})'
        }
    },
    {
        "name": "env_version",
        "patterns": {
            "VERSION_MAJOR": r'VERSION_MAJOR="\d+"',
            "VERSION_MINOR": r'VERSION_MINOR="\d+"',
            "VERSION_PATCH": r'VERSION_PATCH="\d+"'
        },
        "replacements": {
            "VERSION_MAJOR": 'VERSION_MAJOR="{major}"',
            "VERSION_MINOR": 'VERSION_MINOR="{minor}"',
            "VERSION_PATCH": 'VERSION_PATCH="{patch}"'
        }
    }
]

def get_placeholder_values(major, minor, patch, micro='0'):
    now = datetime.now()
    placeholders = {
        'YYYY': now.strftime('%Y'),
        'YY': now.strftime('%y'),
        'MM': now.strftime('%m'),
        'DD': now.strftime('%d'),
        'hh': now.strftime('%H'),
        'mm': now.strftime('%M'),
        'ss': now.strftime('%S'),
        'major': major,
        'minor': minor,
        'micro': micro,
        'patch': patch,
    }
    return placeholders

def format_tag(tag_format, placeholders):
    try:
        return tag_format.format(**placeholders)
    except KeyError as e:
        missing_key = e.args[0]
        logger.error(f"Placeholder {{{missing_key}}} is not defined. Please provide a valid placeholder.")
        sys.exit(1)

def tag_format_uses_micro(tag_format):
    return '{micro}' in tag_format

def get_latest_tag(repo):
    try:
        full_tag_name = repo.git.describe('--tags', '--abbrev=0').strip()
    except GitCommandError:
        return None, None, None, None, None

    version_str = full_tag_name
    if version_str.lower().startswith('v'):
        version_str = version_str[1:]

    parts = version_str.split('.')
    if len(parts) == 1:
        major = parts[0]
        minor = '0'
        patch = '0'
    elif len(parts) == 2:
        major, minor = parts
        patch = '0'
    else:
        major, minor, patch = parts[0], parts[1], parts[2]

    if not (major.isdigit() and minor.isdigit() and patch.isdigit()):
        logger.error(f"The version in tag '{version_str}' is not numeric.")
        return None, None, None, None, None

    return full_tag_name, version_str, major, minor, patch

def get_commits_since_tag(repo, full_tag_name):
    try:
        commits_since_tag = repo.git.rev_list(f"{full_tag_name}..HEAD", '--count')
        return int(commits_since_tag.strip())
    except GitCommandError:
        return 0

def increment_patch(patch_str, increment):
    if patch_str.isdigit():
        return str(int(patch_str) + increment)
    else:
        logger.error(f"Patch part '{patch_str}' is not numeric.")
        sys.exit(1)

def apply_scheme_to_file(content, scheme, ver_major, ver_minor, ver_patch, ver_micro='0'):
    new_content = content
    changed = False
    for key, pattern in scheme["patterns"].items():
        replacement = scheme["replacements"][key].format(
            major=ver_major,
            minor=ver_minor,
            micro=ver_micro,
            patch=ver_patch
        )
        updated_content = re.sub(pattern, replacement, new_content)
        if updated_content != new_content:
            changed = True
        new_content = updated_content
    return new_content, changed

def scheme_supports_micro(scheme):
    """
    Check if a scheme can handle micro.
    A rough heuristic: if in the 'version' replacement (if it exists) {micro} is used, assume it supports micro.
    Or if at least one replacement line uses {micro}, we can assume it supports micro.
    """
    for repl in scheme["replacements"].values():
        if '{micro}' in repl:
            return True
    return False

def scheme_has_4part_pattern(scheme):
    """
    Check if scheme pattern for "version" can handle 4 parts.
    A simple heuristic: the pattern for "version" should match something like four numeric groups.
    For example "Version:\\s*\\d+(\\.\\d+){3}" indicates 4 numeric parts.
    This is heuristic; you can adapt as needed.
    """
    if "version" in scheme["patterns"]:
        pattern = scheme["patterns"]["version"]
        # Heuristic: if pattern has (\\.\\d+){3}, we assume 4 parts
        if re.search(r'\(\\.\\d+\)\{3}', pattern):
            return True
    # If no explicit version pattern, we cannot confirm
    return False

def filter_schemes_for_micro(schemes, micro_used):
    """
    If micro_used, prefer schemes that support micro and have a 4-part pattern.
    Otherwise, return as is.
    """
    if not micro_used:
        return schemes  # no special filtering needed

    # Filter schemes that support micro and ideally have a 4-part pattern
    micro_schemes = []
    for s in schemes:
        if scheme_supports_micro(s):
            # If it supports micro, good. If it also has 4part pattern even better.
            # prioritize those with 4-part pattern
            micro_schemes.append((scheme_has_4part_pattern(s), s))
    # Sort by whether they have a 4-part pattern first (True first)
    micro_schemes.sort(key=lambda x: x[0], reverse=True)

    return [s for (_, s) in micro_schemes] if micro_schemes else schemes

def find_all_matching_schemes(content):
    matched_schemes = []
    for scheme in VERSION_SCHEMES:
        for pattern in scheme["patterns"].values():
            if re.search(pattern, content):
                matched_schemes.append(scheme)
                break
    return matched_schemes

def find_primary_scheme_for_file(file_path):
    """
    Find one scheme that matches the file. If multiple match, return the first.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"{file_path} not found.")
        return None
    matched = find_all_matching_schemes(content)
    if matched:
        return matched[0]
    return None

def try_schemes_on_file(file_path, schemes, major, minor, patch, micro):
    """
    Try each scheme in order until one updates the file. Return True if updated, False otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"{file_path} not found. Operation aborted.")
        sys.exit(1)

    for idx, scheme in enumerate(schemes):
        new_content, changed = apply_scheme_to_file(content, scheme, major, minor, patch, micro)
        if changed:
            with open(file_path, 'w') as file:
                file.write(new_content)

            version_pattern = scheme["patterns"].get("version")
            if version_pattern:
                match = re.search(version_pattern, new_content)
                if match:
                    matched_line = match.group(0)
                    logger.info(f"{file_path} was updated to {matched_line}. Using scheme '{scheme['name']}'.")
                else:
                    logger.warning(f"{file_path}: Version updated, but no 'version' line found after update. Scheme: '{scheme['name']}'")
            else:
                logger.info(f"{file_path} updated to version {major}.{minor}.{patch} using scheme '{scheme['name']}' (no explicit version pattern).")

            if idx > 0:
                # Means the first tried scheme didn't match well, we used a fallback
                logger.info(f"Primary scheme did not fit the file {file_path}'s format. Falling back to scheme '{scheme['name']}' as a workaround.")
            return True
    return False

def update_version_in_file(file_path, ver_major, ver_minor, ver_patch, ver_micro='0', primary_scheme=None, micro_used=False):
    """
    Updates the file. If primary_scheme is given, try it first. If it fails, find alternatives.
    If micro_used is True, prefer schemes that support micro and have a 4-part pattern.
    If no suitable scheme is found, log a warning.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"{file_path} not found. Operation aborted.")
        sys.exit(1)

    if primary_scheme:
        # Try primary scheme
        new_content, changed = apply_scheme_to_file(content, primary_scheme, ver_major, ver_minor, ver_patch, ver_micro)
        if changed:
            with open(file_path, 'w') as file:
                file.write(new_content)

            version_pattern = primary_scheme["patterns"].get("version")
            if version_pattern:
                match = re.search(version_pattern, new_content)
                if match:
                    matched_line = match.group(0)
                    logger.info(f"{file_path} was updated to {matched_line}. Using scheme '{primary_scheme['name']}'.")
                else:
                    logger.warning(f"{file_path}: Version updated using primary scheme '{primary_scheme['name']}', but no 'version' line found.")
            else:
                logger.info(f"{file_path} updated to version {ver_major}.{ver_minor}.{ver_patch} using scheme '{primary_scheme['name']}'.")
            return True
        else:
            # Primary scheme did not apply changes. Try fallback.
            logger.warning(f"Primary scheme '{primary_scheme['name']}' did not change {file_path}. Trying fallback schemes...")
    # If we reach here, we need fallback schemes
    all_matches = find_all_matching_schemes(content)
    if primary_scheme in all_matches:
        all_matches.remove(primary_scheme)
    if not all_matches:
        logger.warning(f"No fallback schemes match {file_path}'s format. Cannot update.")
        return False

    # If micro is used, filter schemes that support micro
    fallback_schemes = filter_schemes_for_micro(all_matches, micro_used=micro_used)

    updated = try_schemes_on_file(file_path, fallback_schemes, ver_major, ver_minor, ver_patch, ver_micro)
    if not updated:
        # No fallback worked
        logger.warning(f"No suitable fallback scheme could update {file_path} to the new version format.")
    return updated

def create_git_tag(repo, version, tag_format, major, minor, patch, micro='0'):
    placeholders = get_placeholder_values(major, minor, patch, micro=micro)
    tag_name = format_tag(tag_format, placeholders)

    if tag_name in [str(tag) for tag in repo.tags]:
        logger.info(f"Tag {tag_name} already exists. No new tag will be created.")
        return False
    try:
        repo.create_tag(tag_name)
        logger.info(f"New Git tag created: {tag_name}")
        return True
    except GitCommandError as e:
        logger.error(f"Error while creating the tag: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Automated tagging and version updating with custom placeholders and parameters for major, micro, and patch.",
        epilog="You can override major, micro, and patch by specifying --major, --micro, and --patch.\n"
               "If the tag format includes {micro} but the old tag is only three-part, the old patch is interpreted as micro and patch=0.\n"
               "Date/time placeholders: {YYYY}, {YY}, {MM}, {DD}, {hh}, {mm}, {ss}\n"
               "Example:\n"
               "  python tagit.py --tag-format '{major}.{minor}.{micro}.{patch}' -f /path/to/file",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-f', '--file',
        dest='files',
        action='append',
        help='File to be updated (e.g., configure.ac). Can be used multiple times.'
    )
    parser.add_argument(
        '--scheme-file',
        dest='scheme_file',
        help='Path to a JSON file containing additional versioning schemes.'
    )
    parser.add_argument(
        '--tag-format',
        dest='tag_format',
        default='v{major}.{minor}.{patch}',
        help='Format for the Git tag. Use {major}, {minor}, {micro}, {patch}, and date/time placeholders.'
    )
    parser.add_argument(
        '--initial-version',
        dest='initial_version',
        default='0.1.0',
        help='Initial version to use when no tags are present (default: "0.1.0").'
    )
    parser.add_argument(
        '--version-mode',
        dest='version_mode',
        choices=['commits', 'increment'],
        default='commits',
        help='Method to determine the patch version: "commits" sets patch to the number of commits since last tag, "increment" increases patch by one.'
    )
    parser.add_argument(
        '--no-tag',
        dest='no_tag',
        action='store_true',
        help='Update files without creating a new Git tag.'
    )
    parser.add_argument(
        '--major',
        dest='override_major',
        help='Override the major version number with a numeric value.'
    )
    parser.add_argument(
        '--micro',
        dest='override_micro',
        default=None,
        help='Override the micro version number with a numeric value. If not specified and {micro} is used, micro is derived from the old patch if the old tag was three-part.'
    )
    parser.add_argument(
        '--patch',
        dest='override_patch',
        help='Override the patch version number with a numeric value.'
    )
    args = parser.parse_args()

    if args.no_tag and not args.files:
        logger.info("Option '--no-tag' specified but no files provided with '-f/--file'. There is nothing to do. Exiting.")
        sys.exit(0)

    tag_format = args.tag_format
    micro_used = tag_format_uses_micro(tag_format)

    initial_version = args.initial_version
    parts = initial_version.split('.')
    while len(parts) < 3:
        parts.append('0')
    initial_major, initial_minor, initial_patch = parts[0], parts[1], parts[2]

    if not (initial_major.isdigit() and initial_minor.isdigit() and initial_patch.isdigit()):
        logger.error(f"The initial version '{initial_version}' is not numeric.")
        sys.exit(1)

    # Check for automatic scheme-file if none provided
    if not args.scheme_file:
        config_path = os.path.join(os.getcwd(), 'tagit-config.json')
        if os.path.exists(config_path):
            args.scheme_file = config_path
            logger.info("No --scheme-file specified. Found 'tagit-config.json' in the repository directory, using it.")
        else:
            logger.info("No --scheme-file specified and no 'tagit-config.json' found in the repository directory.")

    if args.scheme_file:
        try:
            with open(args.scheme_file, 'r') as f:
                additional_schemes = json.load(f)
                if isinstance(additional_schemes, list):
                    VERSION_SCHEMES.extend(additional_schemes)
                    logger.info(f"{len(additional_schemes)} additional versioning schemes loaded.")
                else:
                    logger.error("The scheme file must contain a list of versioning schemes.")
                    sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading the scheme file: {e}")
            sys.exit(1)

    try:
        repo = Repo(os.getcwd())
    except Exception as e:
        logger.error(f"Error initializing the repository: {e}")
        sys.exit(1)

    if repo.is_dirty():
        logger.error("The working directory is not clean. Please commit or stash your changes.")
        sys.exit(1)

    result = get_latest_tag(repo)
    if result is None or result[0] is None:
        # No tags found
        major, minor, patch = initial_major, initial_minor, initial_patch
        old_version = f"{major}.{minor}.{patch}"
        micro = '0'
        logger.info(f"No existing tags found. Initializing version to {major}.{minor}.{patch}.")
    else:
        full_tag_name, version_str, major, minor, patch = result
        old_version = f"{major}.{minor}.{patch}"
        logger.info(f"Latest tag: {full_tag_name}")
        commits_since_tag = get_commits_since_tag(repo, full_tag_name)
        logger.info(f"Commits since tag: {commits_since_tag}")

        if micro_used and args.override_micro is None:
            micro = patch
            patch = '0'
            logger.info(f"Detected micro usage in tag format. Interpreting old patch '{micro}' as micro and patch=0.")
        else:
            micro = '0' if args.override_micro is None else args.override_micro

        if commits_since_tag > 0:
            if args.version_mode == 'commits':
                patch = increment_patch(patch, commits_since_tag)
            else:
                patch = increment_patch(patch, 1)
            logger.info(f"New commits found since the last tag. Base was {old_version}, now incremented patch to {patch}.")
        else:
            logger.info(f"No new commits since the tag. Current version is: {major}.{minor}.{patch}")

    # Override major, micro, and patch if specified
    if args.override_major is not None:
        if not args.override_major.isdigit():
            logger.error(f"Value '{args.override_major}' provided for --major is not numeric.")
            sys.exit(1)
        major = args.override_major

    if args.override_micro is not None:
        if not args.override_micro.isdigit():
            logger.error(f"Value '{args.override_micro}' provided for --micro is not numeric.")
            sys.exit(1)
        micro = args.override_micro

    if args.override_patch is not None:
        if not args.override_patch.isdigit():
            logger.error(f"Value '{args.override_patch}' provided for --patch is not numeric.")
            sys.exit(1)
        patch = args.override_patch

    if micro_used:
        new_version = f"{major}.{minor}.{micro}.{patch}"
    else:
        new_version = f"{major}.{minor}.{patch}"

    any_update = False
    if args.files:
        for file_path in args.files:
            primary_scheme = find_primary_scheme_for_file(file_path)
            updated = update_version_in_file(file_path, major, minor, patch, ver_micro=micro, primary_scheme=primary_scheme, micro_used=micro_used)
            if updated:
                any_update = True

        if any_update:
            commit_message = f"Version updated from {old_version} to {new_version} - Files updated."
            try:
                repo.index.add(args.files)
                repo.index.commit(commit_message)
                logger.info(f"Commit created: {commit_message}")
            except Exception as e:
                logger.error(f"Error while committing: {e}")
                sys.exit(1)
        else:
            logger.info("No files were updated.")
    else:
        logger.info("No files specified. Only a new tag will be created if --no-tag is not used.")

    if not args.no_tag:
        create_git_tag(repo, new_version, tag_format, major, minor, patch, micro=micro)
    else:
        logger.info("Option '--no-tag' is enabled. No Git tag will be created.")

    logger.info("Script executed successfully.")

if __name__ == "__main__":
    main()