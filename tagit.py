#!/usr/bin/env python3
"""
Tagit 2.0 - Automated Git Tagging and Version Management Tool
Optimized single-file version with enhanced security and modularity

This is a standalone version that includes all improvements from the modular architecture
in a single file for easy deployment.
"""

import subprocess
import re
import os
import sys
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Version
VERSION_MAJOR="0"
VERSION_MINOR="3"
VERSION_PATCH="0"
__version__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
__author__ = "Thilo Graf"

# Default versioning schemes
DEFAULT_VERSION_SCHEMES = [
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


class TagitError(Exception):
    """Base exception for Tagit"""
    pass


class GitOperationError(TagitError):
    """Git operation failed"""
    pass


class ValidationError(TagitError):
    """Validation failed"""
    pass


class SecurityError(TagitError):
    """Security violation detected"""
    pass


class ConfigError(TagitError):
    """Configuration error"""
    pass


class FileOperationError(TagitError):
    """File operation failed"""
    pass


class SecurityValidator:
    """Validates inputs for security concerns"""
    
    VERSION_PATTERN = re.compile(r'^[0-9A-Za-z.\-+]+$')
    ALLOWED_PLACEHOLDERS = {
        'major', 'minor', 'patch', 'micro',
        'YYYY', 'YY', 'MM', 'DD', 'hh', 'mm', 'ss'
    }
    
    def validate_version_string(self, version: str) -> str:
        """Validate version string format"""
        if not version:
            raise ValidationError("Version string cannot be empty")
        
        if not self.VERSION_PATTERN.match(version):
            raise ValidationError(
                f"Invalid version format: {version}. "
                "Only alphanumeric characters, dots, dashes, and plus signs allowed."
            )
        
        # Additional semantic version validation
        base_version = version.split('-')[0].split('+')[0]
        parts = base_version.split('.')
        
        if len(parts) < 3:
            raise ValidationError(
                f"Version must have at least major.minor.patch: {version}"
            )
        
        # Validate numeric parts
        for i, part in enumerate(parts[:4]):
            if not part.isdigit():
                raise ValidationError(
                    f"Version component must be numeric: {part}"
                )
        
        return version
    
    def validate_tag_format(self, tag_format: str) -> str:
        """Validate tag format string"""
        if not tag_format:
            raise ValidationError("Tag format cannot be empty")
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'\$\(',  # Command substitution
            r'`',     # Backticks
            r'&&',    # Command chaining
            r'\|\|',  # Command chaining
            r';',     # Command separator
            r'>',     # Redirection
            r'<',     # Redirection
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, tag_format):
                raise SecurityError(
                    f"Tag format contains potentially dangerous pattern: {pattern}"
                )
        
        # Validate placeholders
        placeholders = re.findall(r'\{(\w+)\}', tag_format)
        for placeholder in placeholders:
            if placeholder not in self.ALLOWED_PLACEHOLDERS:
                raise ValidationError(
                    f"Unknown placeholder: {{{placeholder}}}. "
                    f"Allowed: {', '.join(sorted(self.ALLOWED_PLACEHOLDERS))}"
                )
        
        return tag_format
    
    def validate_safe_path(self, base_dir: str, user_path: str) -> str:
        """Validate path is within base directory (prevent traversal)"""
        base = Path(base_dir).resolve()
        full_path = (base / user_path).resolve()
        
        try:
            full_path.relative_to(base)
        except ValueError:
            raise SecurityError(
                f"Path traversal detected: {user_path} is outside repository"
            )
        
        return str(full_path)
    
    def validate_numeric(self, value: str, field_name: str) -> str:
        """Validate numeric string"""
        if not value.isdigit():
            raise ValidationError(
                f"{field_name} must be numeric, got: {value}"
            )
        return value


class GitHandler:
    """Secure Git operations handler"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self._validate_git_repo()
        
    def _validate_git_repo(self) -> None:
        """Validate that path is a Git repository"""
        git_dir = self.repo_path / '.git'
        if not git_dir.exists():
            raise GitOperationError(f"Not a Git repository: {self.repo_path}")
    
    def _run_git_command(self, args: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run Git command securely without shell=True"""
        cmd = ['git'] + args
        defaults = {
            'cwd': self.repo_path,
            'capture_output': True,
            'text': True,
            'check': True,
            'timeout': 60
        }
        defaults.update(kwargs)
        
        try:
            logger.debug(f"Running Git command: {' '.join(cmd)}")
            return subprocess.run(cmd, **defaults)
        except subprocess.TimeoutExpired:
            raise GitOperationError("Git operation timed out")
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Git command failed: {e.stderr}")
    
    def is_dirty(self) -> bool:
        """Check if working directory has uncommitted changes"""
        result = self._run_git_command(['status', '--porcelain'])
        return bool(result.stdout.strip())
    
    @lru_cache(maxsize=128)
    def get_latest_tag(self) -> Dict[str, Optional[str]]:
        """Get latest tag and parse version components"""
        try:
            result = self._run_git_command(['describe', '--tags', '--abbrev=0'])
            tag = result.stdout.strip()
            
            # Parse version from tag
            version_str = tag[1:] if tag.startswith('v') else tag

            # Remove pre-release and build metadata for parsing
            base_version = version_str.split('-')[0].split('+')[0]
            parts = base_version.split('.')
            
            return {
                'tag': tag,
                'major': parts[0] if len(parts) > 0 else '0',
                'minor': parts[1] if len(parts) > 1 else '0',
                'patch': parts[2] if len(parts) > 2 else '0',
                'micro': parts[3] if len(parts) > 3 else None
            }
        except GitOperationError:
            return {'tag': None, 'major': '0', 'minor': '0', 'patch': '0', 'micro': None}
    
    def get_commits_since_tag(self, tag: str) -> int:
        """Get number of commits since specified tag"""
        try:
            result = self._run_git_command(['rev-list', f'{tag}..HEAD', '--count'])
            return int(result.stdout.strip())
        except (GitOperationError, ValueError):
            return 0
    
    def tag_exists(self, tag_name: str) -> bool:
        """Check if a tag already exists"""
        try:
            # Use check=False to avoid exception on non-zero exit code
            result = self._run_git_command(['rev-parse', f'refs/tags/{tag_name}'], check=False)
            return result.returncode == 0
        except:
            return False

    def create_tag(self, tag_name: str, message: Optional[str] = None) -> None:
        """Create annotated Git tag"""
        # Check if tag already exists
        if self.tag_exists(tag_name):
            logger.info(f"Tag {tag_name} already exists, skipping tag creation")
            return
        
        # Create new tag
        args = ['tag', '-a', tag_name]
        if message:
            args.extend(['-m', message])
        else:
            args.extend(['-m', f'Release {tag_name}'])
        
        self._run_git_command(args)
        logger.info(f"Created tag: {tag_name}")
    
    def commit_files(self, files: List[str], message: str) -> None:
        """Stage and commit specified files"""
        # Stage files
        self._run_git_command(['add'] + files)
        
        # Commit
        self._run_git_command(['commit', '-m', message])
        logger.info(f"Committed {len(files)} file(s): {message}")


class VersionManager:
    """Manages version parsing, validation, and formatting"""
    
    SEMVER_PATTERN = re.compile(
        r'^(\d+)\.(\d+)\.(\d+)'
        r'(?:\.(\d+))?'  # Optional micro version
        r'(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'  # Pre-release
        r'(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'  # Build metadata
    )
    
    def parse_version(self, version_str: str) -> Tuple[str, ...]:
        """Parse version string into components"""
        match = self.SEMVER_PATTERN.match(version_str)
        if not match:
            raise ValidationError(f"Invalid version format: {version_str}")
        
        groups = match.groups()
        # Return major, minor, patch, and optionally micro
        result = [groups[0], groups[1], groups[2]]
        if groups[3] is not None:
            result.append(groups[3])
        
        return tuple(result)
    
    def format_tag(self, tag_format: str, placeholders: Dict[str, str]) -> str:
        """Format tag name with placeholders"""
        try:
            return tag_format.format(**placeholders)
        except KeyError as e:
            raise ValidationError(f"Unknown placeholder in tag format: {{{e.args[0]}}}")


class FileUpdater:
    """Handles file updates based on versioning schemes"""
    
    def __init__(self):
        self.schemes = []
    
    def find_matching_scheme(self, content: str, schemes: List[Dict]) -> Optional[Dict]:
        """Find first scheme that matches file content"""
        for scheme in schemes:
            for pattern in scheme["patterns"].values():
                if re.search(pattern, content):
                    return scheme
        return None
    
    def apply_scheme(
        self, 
        content: str, 
        scheme: Dict,
        major: str,
        minor: str,
        patch: str,
        micro: str = '0'
    ) -> tuple[str, bool]:
        """Apply versioning scheme to content"""
        new_content = content
        changed = False
        
        replacements = {
            'major': major,
            'minor': minor,
            'patch': patch,
            'micro': micro
        }
        
        for key, pattern in scheme["patterns"].items():
            if key in scheme["replacements"]:
                replacement = scheme["replacements"][key].format(**replacements)
                updated = re.sub(pattern, replacement, new_content)
                if updated != new_content:
                    changed = True
                    new_content = updated
        
        return new_content, changed
    
    def update_file(
        self,
        file_path: str,
        major: str,
        minor: str,
        patch: str,
        micro: str,
        schemes: List[Dict]
    ) -> bool:
        """Update version in file using appropriate scheme"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileOperationError(f"File not found: {file_path}")
        
        # Read file content
        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            raise FileOperationError(f"Failed to read {file_path}: {e}")
        
        # Find matching scheme
        all_schemes = schemes + DEFAULT_VERSION_SCHEMES
        scheme = self.find_matching_scheme(content, all_schemes)
        
        if not scheme:
            logger.warning(f"No matching scheme found for {file_path}")
            return False
        
        # Apply scheme
        new_content, changed = self.apply_scheme(
            content, scheme, major, minor, patch, micro
        )
        
        if changed:
            try:
                # Create backup
                backup_path = path.with_suffix(path.suffix + '.tagit-backup')
                shutil.copy2(file_path, backup_path)
                
                # Write updated content
                path.write_text(new_content, encoding='utf-8')
                
                # Remove backup on success
                backup_path.unlink()
                
                logger.info(f"Updated {file_path} using scheme '{scheme['name']}'")
                return True
            except Exception as e:
                # Restore from backup if exists
                if backup_path.exists():
                    shutil.copy2(backup_path, file_path)
                    backup_path.unlink()
                raise FileOperationError(f"Failed to write {file_path}: {e}")
        
        return False


class ConfigManager:
    """Manages configuration and versioning schemes"""
    
    def __init__(self):
        self.schemes: List[Dict[str, Any]] = []
        
    def load_scheme_file(self, file_path: str) -> None:
        """Load additional versioning schemes from JSON file"""
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigError(f"Scheme file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                schemes = json.load(f)
            
            if not isinstance(schemes, list):
                raise ConfigError("Scheme file must contain a list of schemes")
            
            # Validate each scheme
            for scheme in schemes:
                self._validate_scheme(scheme)
            
            self.schemes.extend(schemes)
            logger.info(f"Loaded {len(schemes)} schemes from {file_path}")
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in scheme file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load scheme file: {e}")
    
    def _validate_scheme(self, scheme: Dict[str, Any]) -> None:
        """Validate scheme structure"""
        required_fields = ['name', 'patterns', 'replacements']
        
        for field in required_fields:
            if field not in scheme:
                raise ValidationError(f"Scheme missing required field: {field}")
        
        if not isinstance(scheme['patterns'], dict):
            raise ValidationError("Scheme 'patterns' must be a dictionary")
        
        if not isinstance(scheme['replacements'], dict):
            raise ValidationError("Scheme 'replacements' must be a dictionary")
    
    def get_schemes(self) -> List[Dict[str, Any]]:
        """Get all loaded schemes"""
        return self.schemes


def main():
    parser = argparse.ArgumentParser(
        description=f"Tagit {__version__} - Automated Git tagging and version management tool",
        epilog="Examples:\n"
               "  tagit -f package.json -f version.txt\n"
               "  tagit --dry-run -f configure.ac\n"
               "  tagit --tag-format 'v{major}.{minor}.{patch}-{YYYY}{MM}{DD}'",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='files',
        action='append',
        help='File to be updated (can be used multiple times)'
    )
    parser.add_argument(
        '--scheme-file',
        help='Path to JSON file containing additional versioning schemes'
    )
    parser.add_argument(
        '--tag-format',
        default='v{major}.{minor}.{patch}',
        help='Format for Git tag (default: v{major}.{minor}.{patch})'
    )
    parser.add_argument(
        '--initial-version',
        default='0.1.0',
        help='Initial version when no tags exist (default: 0.1.0)'
    )
    parser.add_argument(
        '--version-mode',
        choices=['commits', 'increment'],
        default='commits',
        help='Method to determine patch version'
    )
    parser.add_argument(
        '--no-tag',
        action='store_true',
        help='Update files without creating a Git tag'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument('--major', help='Override major version number')
    parser.add_argument('--minor', help='Override minor version number') 
    parser.add_argument('--micro', help='Override micro version number')
    parser.add_argument('--patch', help='Override patch version number')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.no_tag and not args.files:
        logger.info("Nothing to do: --no-tag specified but no files provided.")
        return 0
    
    try:
        # Initialize components
        repo_path = Path.cwd()
        validator = SecurityValidator()
        git_handler = GitHandler(repo_path)
        version_manager = VersionManager()
        file_updater = FileUpdater()
        config_manager = ConfigManager()
        
        # Validate inputs
        validator.validate_tag_format(args.tag_format)
        if args.initial_version:
            validator.validate_version_string(args.initial_version)
        
        # Load additional schemes
        if args.scheme_file:
            config_manager.load_scheme_file(args.scheme_file)
        elif (repo_path / 'tagit-config.json').exists():
            config_manager.load_scheme_file(str(repo_path / 'tagit-config.json'))
            logger.info("Found 'tagit-config.json' in repository, using it.")
        
        # Check repository status
        if git_handler.is_dirty() and not args.dry_run:
            logger.error("Working directory is not clean. Please commit or stash changes.")
            return 1
        
        # Determine current version
        latest_tag_info = git_handler.get_latest_tag()
        
        if latest_tag_info['tag'] is None:
            # No existing tags
            version_parts = version_manager.parse_version(args.initial_version)
            major, minor, patch = version_parts[:3]
            micro = version_parts[3] if len(version_parts) > 3 else '0'
            logger.info(f"No existing tags. Using initial version: {major}.{minor}.{patch}")
            old_version = args.initial_version
        else:
            # Get current version
            major = latest_tag_info['major']
            minor = latest_tag_info['minor']
            patch = latest_tag_info['patch']
            micro = latest_tag_info.get('micro', '0')
            old_version = f"{major}.{minor}.{patch}"
            
            logger.info(f"Latest tag: {latest_tag_info['tag']}")
            
            # Handle micro versioning
            micro_used = '{micro}' in args.tag_format
            if micro_used and args.micro is None and latest_tag_info['micro'] is None:
                # Convert 3-part to 4-part version
                micro = patch
                patch = '0'
                logger.info(f"Converting to 4-part version: {major}.{minor}.{micro}.{patch}")
            
            # Calculate new version
            commits_count = git_handler.get_commits_since_tag(latest_tag_info['tag'])
            logger.info(f"Commits since tag: {commits_count}")
            
            if commits_count > 0:
                if args.version_mode == 'commits':
                    patch = str(int(patch) + commits_count)
                else:  # increment
                    patch = str(int(patch) + 1)
                logger.info(f"New commits found. Incrementing version.")
        
        # Apply overrides
        if args.major is not None:
            validator.validate_numeric(args.major, "major")
            major = args.major
        if args.minor is not None:
            validator.validate_numeric(args.minor, "minor")
            minor = args.minor
        if args.micro is not None:
            validator.validate_numeric(args.micro, "micro")
            micro = args.micro
        if args.patch is not None:
            validator.validate_numeric(args.patch, "patch")
            patch = args.patch
        
        # Format new version
        micro_used = '{micro}' in args.tag_format
        if micro_used:
            new_version = f"{major}.{minor}.{micro}.{patch}"
        else:
            new_version = f"{major}.{minor}.{patch}"
        
        logger.info(f"New version: {new_version}")
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        # Update files
        if args.files:
            updated_files = []
            for file_path in args.files:
                safe_path = validator.validate_safe_path(str(repo_path), file_path)
                
                if args.dry_run:
                    logger.info(f"Would update: {safe_path}")
                else:
                    success = file_updater.update_file(
                        safe_path, major, minor, patch, micro,
                        config_manager.get_schemes()
                    )
                    if success:
                        updated_files.append(safe_path)
            
            # Commit changes
            if updated_files and not args.dry_run:
                commit_msg = f"Version updated from {old_version} to {new_version}"
                git_handler.commit_files(updated_files, commit_msg)
        
        # Create tag
        if not args.no_tag:
            # Generate placeholder values
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
            
            tag_name = version_manager.format_tag(args.tag_format, placeholders)

            if args.dry_run:
                if git_handler.tag_exists(tag_name):
                    logger.info(f"Would skip creating tag (already exists): {tag_name}")
                else:
                    logger.info(f"Would create tag: {tag_name}")
            else:
                git_handler.create_tag(tag_name)
        
        logger.info("Script executed successfully.")
        return 0
        
    except TagitError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
