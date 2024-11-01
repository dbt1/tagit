#!/usr/bin/env python3
"""
Automatic Git Tagging and Version Update with custom placeholders.

This script automates tagging in Git and updates version numbers in
various files based on defined versioning schemes, with support for
custom placeholders in the --tag-format parameter.

Author: Thilo Graf
License: MIT

Available placeholders for --tag-format:
  {YYYY}, {YY}     - Year (four-digit, two-digit)
  {MM}             - Month (zero-padded)
  {DD}             - Day of the month (zero-padded)
  {hh}, {mm}, {ss} - Hour, minute, second (zero-padded)
  {major}, {minor}, {patch} - Version numbers

Examples:
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}'
  python tagit.py --tag-format 'v{major}.{minor}.{patch}-{YY}{MM}{DD}'
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Define supported versioning schemes
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
            "ver_micro": 'define(ver_micro, {patch})',  # Assuming 'patch' corresponds to 'micro'
            "ver_patch": 'define(ver_patch, {patch})'   # If both 'ver_micro' and 'ver_patch' exist
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
    # Additional schemes can be added here
]

def get_placeholder_values(major, minor, patch):
    """
    Generates a dictionary mapping placeholders to their actual values.

    Args:
        major (str): Major version number.
        minor (str): Minor version number.
        patch (str): Patch version number.

    Returns:
        dict: A dictionary of placeholders and their corresponding values.
    """
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
        'patch': patch,
    }
    return placeholders

def format_tag(tag_format, placeholders):
    """
    Replaces placeholders in the tag format string with actual values.

    Args:
        tag_format (str): The tag format string with placeholders.
        placeholders (dict): A dictionary of placeholder values.

    Returns:
        str: The formatted tag string.
    """
    try:
        return tag_format.format(**placeholders)
    except KeyError as e:
        missing_key = e.args[0]
        logger.error(f"Placeholder {{{missing_key}}} is not defined. Please provide a valid placeholder.")
        sys.exit(1)

def get_latest_tag(repo):
    """
    Retrieves the latest Git tag and its components.

    Args:
        repo (git.Repo): The Git repository object.

    Returns:
        tuple: (full_tag_name, version_str, major, minor, patch)
            - full_tag_name (str): The full tag name in Git (e.g., 'v0.4.1.0').
            - version_str (str): The tag name without the 'v' prefix (e.g., '0.4.1.0').
            - major (str): Major version number.
            - minor (str): Minor version number.
            - patch (str): Patch version number (may have multiple subparts).
    """
    try:
        full_tag_name = repo.git.describe('--tags', '--abbrev=0').strip()
        version_str = full_tag_name
        # Remove 'v' or 'V' prefix if present
        if version_str.lower().startswith('v'):
            version_str = version_str[1:]

        # Split the tag based on dots
        parts = version_str.split('.')

        if len(parts) < 2:
            logger.error(f"The latest tag '{version_str}' does not have at least MAJOR.MINOR parts.")
            return None, None, None, None, None

        major = parts[0]
        minor = parts[1]
        patch_parts = parts[2:]  # All remaining parts as patch components

        # Check if Major and Minor are numeric
        if not (major.isdigit() and minor.isdigit()):
            logger.error(f"The major or minor version in tag '{version_str}' is not numeric.")
            return None, None, None, None, None

        # Patch can have multiple parts
        patch = '.'.join(patch_parts) if patch_parts else '0'

        return full_tag_name, version_str, major, minor, patch

    except GitCommandError:
        return None, None, None, None, None

def get_commits_since_tag(repo, full_tag_name):
    """
    Retrieves the number of commits since the latest tag.

    Args:
        repo (git.Repo): The Git repository object.
        full_tag_name (str): The full tag name in Git.

    Returns:
        int: Number of commits since the latest tag.
    """
    try:
        commits_since_tag = repo.git.rev_list(f"{full_tag_name}..HEAD", '--count')
        commits_since_tag = int(commits_since_tag.strip())
        return commits_since_tag
    except GitCommandError:
        return 0

def increment_patch(patch_str, increment):
    """
    Increases the last numeric part of the patch string by the given increment.

    Args:
        patch_str (str): The patch string (e.g., '1.0' or '1').
        increment (int): The value to add to the last numeric part.

    Returns:
        str: The new patch string with the incremented last numeric part.
    """
    parts = patch_str.split('.')
    for i in range(len(parts)-1, -1, -1):
        if parts[i].isdigit():
            parts[i] = str(int(parts[i]) + increment)
            break
    else:
        # If no numeric part was found, append the increment
        parts.append(str(increment))
    return '.'.join(parts)

def update_version_in_file(file_path, scheme, ver_major, ver_minor, ver_patch):
    """
    Updates the given file with the new version based on the provided scheme.

    Args:
        file_path (str): Path to the file to be updated.
        scheme (dict): The versioning scheme to be used.
        ver_major (str): The major version number.
        ver_minor (str): The minor version number.
        ver_patch (str): The patch version number (may have multiple subparts).

    Returns:
        bool: True if the file was updated, False otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"{file_path} not found. Operation aborted.")
        sys.exit(1)

    # Replace version numbers in the file
    new_content = content
    for key, pattern in scheme["patterns"].items():
        replacement = scheme["replacements"][key].format(
            major=ver_major,
            minor=ver_minor,
            patch=ver_patch
        )
        new_content = re.sub(pattern, replacement, new_content)

    # Check if any changes were made
    if new_content != content:
        with open(file_path, 'w') as file:
            file.write(new_content)
        logger.info(f"{file_path} updated to version {ver_major}.{ver_minor}.{ver_patch}.")
        return True
    else:
        logger.info(f"{file_path} is already up to date: {ver_major}.{ver_minor}.{ver_patch}")
        return False

def find_matching_scheme(file_path):
    """
    Finds the matching versioning scheme for the given file.

    Args:
        file_path (str): Path to the file to be checked.

    Returns:
        dict or None: The matching scheme if found, otherwise None.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        logger.error(f"{file_path} not found.")
        return None

    for scheme in VERSION_SCHEMES:
        for pattern in scheme["patterns"].values():
            if re.search(pattern, content):
                return scheme
    return None

def create_git_tag(repo, version, tag_format, major, minor, patch):
    """
    Creates a new Git tag with the given version and tag format.

    Args:
        repo (git.Repo): The Git repository object.
        version (str): The version number for the tag.
        tag_format (str): The format string for the tag.

    Returns:
        bool: True if the tag was created, False otherwise.
    """
    # Generate placeholder values
    placeholders = get_placeholder_values(major, minor, patch)
    # Format the tag name
    tag_name = format_tag(tag_format, placeholders)

    # Check if tag already exists
    if tag_name in [str(tag) for tag in repo.tags]:
        logger.info(f"Tag {tag_name} already exists. No new tag will be created.")
        return False
    try:
        # Create the new tag with the specified format
        repo.create_tag(tag_name)
        logger.info(f"New Git tag created: {tag_name}")
        return True
    except GitCommandError as e:
        logger.error(f"Error while creating the tag: {e}")
        sys.exit(1)

def main():
    """
    Main function of the script. Performs argument parsing, version updating, and tagging.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Automated tagging and version updating with custom placeholders.",
        epilog="Available placeholders for --tag-format:\n"
               "  {YYYY}, {YY}     - Year (four-digit, two-digit)\n"
               "  {MM}             - Month (zero-padded)\n"
               "  {DD}             - Day of the month (zero-padded)\n"
               "  {hh}, {mm}, {ss} - Hour, minute, second (zero-padded)\n"
               "  {major}, {minor}, {patch} - Version numbers\n"
               "\nExamples:\n"
               "  python tagit.py --tag-format '{YYYY}.{MM}.{patch}'\n"
               "  python tagit.py --tag-format 'v{major}.{minor}.{patch}-{YY}{MM}{DD}'",
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
        help='Format for the Git tag. Use placeholders like {YYYY}, {MM}, {major}, {minor}, {patch}.'
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
        help='Method to determine the patch version: "commits" sets patch to number of commits since last tag, "increment" increases patch by one.'
    )
    parser.add_argument(
        '--no-tag',
        dest='no_tag',
        action='store_true',
        help='Update files without creating a new Git tag.'
    )
    args = parser.parse_args()

    # Check if --no-tag is used without specifying any files
    if args.no_tag and not args.files:
        logger.info("Option '--no-tag' specified but no files provided with '-f/--file'. There is nothing to do. Exiting.")
        sys.exit(0)

    # Handle tag_format argument
    tag_format = args.tag_format

    # Handle initial_version argument
    initial_version = args.initial_version
    initial_version_match = re.match(r'^(\d+)\.(\d+)(?:\.(.+))?$', initial_version)
    if not initial_version_match:
        logger.error(f"The initial version '{initial_version}' does not match the expected format MAJOR.MINOR[.PATCH].")
        sys.exit(1)
    initial_major = initial_version_match.group(1)
    initial_minor = initial_version_match.group(2)
    initial_patch = initial_version_match.group(3) if initial_version_match.group(3) else '0'

    # Load additional versioning schemes if specified
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

    # Initialize the Git repository
    try:
        repo = Repo(os.getcwd())
    except Exception as e:
        logger.error(f"Error initializing the repository: {e}")
        sys.exit(1)

    # Check if the working directory is clean (modified)
    if repo.is_dirty():
        logger.error("The working directory is not clean. Please commit or stash your changes.")
        sys.exit(1)

    # Get the latest tag and its components
    full_tag_name, version_str, major, minor, patch = get_latest_tag(repo)

    if not full_tag_name:
        # No existing tags found, use initial_version
        version = initial_version
        major, minor, patch = initial_major, initial_minor, initial_patch
        logger.info(f"No existing tags found. Initializing version to {version}.")

        if args.files:
            any_update = False
            for file_path in args.files:
                scheme = find_matching_scheme(file_path)
                if not scheme:
                    logger.error(f"No supported versioning scheme found in {file_path}. Operation aborted.")
                    sys.exit(1)
                updated = update_version_in_file(file_path, scheme,
                                                ver_major=major,
                                                ver_minor=minor,
                                                ver_patch=patch)
                if updated:
                    any_update = True

            if any_update:
                # Commit changes
                commit_message = f"Version {version} - Initial version."
                try:
                    repo.index.add(args.files)
                    repo.index.commit(commit_message)
                    logger.info(f"Commit created: {commit_message}")
                except Exception as e:
                    logger.error(f"Error while committing: {e}")
                    sys.exit(1)
            else:
                logger.info("No files were updated.")
        if not args.no_tag:
            # Create the initial tag
            tag_created = create_git_tag(repo, version, tag_format, major, minor, patch)
            logger.info(f"Latest tag: {format_tag(tag_format, get_placeholder_values(major, minor, patch))}, commits since tag: 0")
        else:
            logger.info("Option '--no-tag' is enabled. No Git tag will be created.")
    else:
        logger.info(f"Latest tag: {full_tag_name}")
        # Count the number of commits since the latest tag
        commits_since_tag = get_commits_since_tag(repo, full_tag_name)
        logger.info(f"Commits since tag: {commits_since_tag}")

        if commits_since_tag > 0:
            # Determine new patch based on version_mode
            if args.version_mode == 'commits':
                new_patch = increment_patch(patch, commits_since_tag)
            elif args.version_mode == 'increment':
                new_patch = increment_patch(patch, 1)
            version = f"{major}.{minor}.{new_patch}"
            logger.info(f"New commits found since the last tag: {version}")

            if args.files:
                # Update files
                any_update = False
                for file_path in args.files:
                    scheme = find_matching_scheme(file_path)
                    if not scheme:
                        logger.error(f"No supported versioning scheme found in {file_path}. Operation aborted.")
                        sys.exit(1)
                    updated = update_version_in_file(file_path, scheme,
                                                    ver_major=major,
                                                    ver_minor=minor,
                                                    ver_patch=new_patch)
                    if updated:
                        any_update = True

                if any_update:
                    # Commit changes
                    commit_message = f"Version {version} - Synchronized with the latest tag."
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
                logger.info("No files specified with -f/--file. Only a new tag will be created without updating any files.")

            if not args.no_tag:
                # Create new Git tag
                tag_created = create_git_tag(repo, version, tag_format, major, minor, new_patch)

                if not tag_created:
                    logger.warning(f"Tag {format_tag(tag_format, get_placeholder_values(major, minor, new_patch))} already exists. Skipping tag creation.")
            else:
                logger.info("Option '--no-tag' is enabled. No Git tag will be created.")
        else:
            # Exactly on the latest tag
            version = f"{major}.{minor}.{patch}"
            logger.info(f"No new commits since the tag. Current version is: {version}")

            if args.files:
                # Ensure files match the latest tag's version
                any_update = False
                for file_path in args.files:
                    scheme = find_matching_scheme(file_path)
                    if not scheme:
                        logger.error(f"No supported versioning scheme found in {file_path}. Operation aborted.")
                        sys.exit(1)
                    updated = update_version_in_file(file_path, scheme,
                                                    ver_major=major,
                                                    ver_minor=minor,
                                                    ver_patch=patch)
                    if updated:
                        any_update = True

                if any_update:
                    # Commit changes
                    commit_message = f"Version {version} - Files updated to match the latest tag."
                    try:
                        repo.index.add(args.files)
                        repo.index.commit(commit_message)
                        logger.info(f"Commit created: {commit_message}")
                    except Exception as e:
                        logger.error(f"Error while committing: {e}")
                        sys.exit(1)
                    if not args.no_tag:
                        # Optionally, create a new tag if desired
                        create_git_tag(repo, version, tag_format, major, minor, patch)
                    else:
                        logger.info("Option '--no-tag' is enabled. No Git tag will be created.")
                else:
                    logger.info("No files were updated and the repository is up to date.")
            else:
                logger.info("No new commits and no files specified. The repository is up to date. No action is needed.")

    logger.info("Script executed successfully.")

if __name__ == "__main__":
    main()
