#!/usr/bin/env python3
"""
Automatic Git Tagging and Version Update

This script automates tagging in Git and updates version numbers in
various files based on defined versioning schemes. It supports
extending additional versioning schemes via a configuration file.

Author: Thilo Graf
License: MIT

Examples:
    python tagit.py -f configure.ac -f opkg-upgrade.sh
    python tagit.py --file configure.ac --file opkg-upgrade.sh --scheme-file custom_schemes.json
    python tagit.py
"""

import subprocess
import re
import os
import sys
import argparse
import logging
import json
from git import Repo, GitCommandError

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)
logger = logging.getLogger(__name__)

# Define the supported versioning schemes
VERSION_SCHEMES = [
    {
        "name": "ac_init",
        "patterns": {
            "version": r'(AC_INIT\(\[.*?\],\s*\[)\d+\.\d+\.\d+(\],\s*\[.*?\]\))'
        },
        "replacements": {
            "version": r'\g<1>{major}.{minor}.{micro}\g<2>'
        }
    },
    {
        "name": "version_assignment",
        "patterns": {
            "version": r'VERSION\s*=\s*"\d+\.\d+\.\d+"'
        },
        "replacements": {
            "version": 'VERSION = "{major}.{minor}.{micro}"'
        }
    },
    {
        "name": "define_ver",
        "patterns": {
            "ver_major": r'define\(ver_major,\s*\d+\)',
            "ver_minor": r'define\(ver_minor,\s*\d+\)',
            "ver_micro": r'define\(ver_micro,\s*\d+\)'
        },
        "replacements": {
            "ver_major": 'define(ver_major, {major})',
            "ver_minor": 'define(ver_minor, {minor})',
            "ver_micro": 'define(ver_micro, {micro})'
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


def get_latest_tag(repo):
    """
    Retrieves the latest Git tag and its components.

    Args:
        repo (git.Repo): The Git repository object.

    Returns:
        tuple: (tag_version, prefix, major, minor, patch)
            - tag_version (str): The latest tag (e.g., 'v0.1.6').
            - prefix (str): The prefix of the tag (e.g., 'v').
            - major (str): Major version number.
            - minor (str): Minor version number.
            - patch (str): Patch version number.
    """
    try:
        latest_tag = repo.git.describe('--tags', '--abbrev=0')
        latest_tag = latest_tag.strip()
        match_tag = re.match(r'^(?P<prefix>v?)(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$', latest_tag)
        if not match_tag:
            logger.error(f"The latest tag '{latest_tag}' does not match the expected format MAJOR.MINOR.PATCH.")
            return None, None, None, None, None

        prefix = match_tag.group('prefix')
        major = match_tag.group('major')
        minor = match_tag.group('minor')
        patch = match_tag.group('patch')

        return latest_tag, prefix, major, minor, patch

    except GitCommandError:
        return None, None, None, None, None


def get_commits_since_tag(repo, latest_tag):
    """
    Retrieves the number of commits since the latest tag.

    Args:
        repo (git.Repo): The Git repository object.
        latest_tag (str): The latest tag.

    Returns:
        int: Number of commits since the latest tag.
    """
    try:
        commits_since_tag = repo.git.rev_list(f"{latest_tag}..HEAD", '--count')
        commits_since_tag = int(commits_since_tag.strip())
        return commits_since_tag
    except GitCommandError:
        return 0


def update_version_in_file(file_path, scheme, ver_major, ver_minor, ver_micro):
    """
    Updates the given file with the new version based on the provided scheme.

    Args:
        file_path (str): Path to the file to be updated.
        scheme (dict): The versioning scheme to be used.
        ver_major (str): The major version number.
        ver_minor (str): The minor version number.
        ver_micro (str): The patch version.

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
            micro=ver_micro,
            patch=ver_micro  # Assuming patch is same as micro
        )
        new_content = re.sub(pattern, replacement, new_content)

    # Check if any changes were made
    if new_content != content:
        with open(file_path, 'w') as file:
            file.write(new_content)
        logger.info(f"{file_path} updated to version {ver_major}.{ver_minor}.{ver_micro}.")
        return True
    else:
        logger.info(f"{file_path} is already up to date: {ver_major}.{ver_minor}.{ver_micro}")
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


def create_git_tag(repo, version, prefix):
    """
    Creates a new Git tag with the given version and prefix.

    Args:
        repo (git.Repo): The Git repository object.
        version (str): The version number for the tag.
        prefix (str): The prefix for the tag.
    """
    tag_name = f"{prefix}{version}"
    # Check if tag already exists
    if tag_name in [str(tag) for tag in repo.tags]:
        logger.info(f"Tag {tag_name} already exists. No new tag will be created.")
        return False
    try:
        # Create the new tag with the prefix
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
        description="Automated tagging and version updating.",
        epilog="Examples:\n"
               "  python tagit.py -f configure.ac -f opkg-upgrade.sh --scheme-file custom_schemes.json\n"
               "  python tagit.py --file configure.ac --file opkg-upgrade.sh\n"
               "  python tagit.py",
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
    args = parser.parse_args()

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

    if repo.is_dirty(untracked_files=True):
        logger.error("The working directory is not clean. Please commit or stash your changes.")
        sys.exit(1)

    # Get the latest tag and its components
    latest_tag, prefix, major, minor, patch = get_latest_tag(repo)

    if not latest_tag:
        logger.warning("No existing tags found. Initializing version to 0.1.0.")
        latest_tag = "v0.1.0"
        prefix = "v"
        major = "0"
        minor = "1"
        patch = "0"
        # Update files with the initial version if files are specified
        if args.files:
            any_update = False
            for file_path in args.files:
                scheme = find_matching_scheme(file_path)
                if not scheme:
                    logger.error(f"No supported versioning scheme found in {file_path}. Operation aborted.")
                    sys.exit(1)
                updated = update_version_in_file(file_path, scheme, major, minor, patch)
                if updated:
                    any_update = True

            if any_update:
                # Commit changes
                commit_message = f"Version {major}.{minor}.{patch} - Initial version."
                try:
                    repo.index.add(args.files)
                    repo.index.commit(commit_message)
                    logger.info(f"Commit created: {commit_message}")
                except Exception as e:
                    logger.error(f"Error while committing: {e}")
                    sys.exit(1)
            else:
                logger.info("No files were updated.")
        # Create the initial tag
        create_git_tag(repo, f"{major}.{minor}.{patch}", prefix)
        logger.info(f"Latest tag: {latest_tag}, commits since tag: 0")
    else:
        logger.info(f"Latest tag: {latest_tag}, commits since tag: ...")
        # Count the number of commits since the latest tag
        commits_since_tag = get_commits_since_tag(repo, latest_tag)
        logger.info(f"Commits since tag: {commits_since_tag}")

        if commits_since_tag > 0:
            # There are commits since the last tag
            new_patch = int(patch) + 1
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
                    updated = update_version_in_file(file_path, scheme, major, minor, new_patch)
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
                logger.warning("No files specified with -f/--file. Only a new tag will be created without updating any files.")

            # Create new Git tag
            tag_created = create_git_tag(repo, version, prefix)

            if not tag_created:
                logger.warning(f"Tag {prefix}{version} already exists. Skipping tag creation.")
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
                    updated = update_version_in_file(file_path, scheme, major, minor, patch)
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
                else:
                    logger.info("No files were updated and the repository is up to date.")
            else:
                logger.info("No new commits and no files specified. The repository is up to date. No action is needed.")

    logger.info("Script executed successfully.")


if __name__ == "__main__":
    main()
