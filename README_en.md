<!-- LANGUAGE_LINKS_START -->

[🇩🇪 German](README_de.md) | <span style="color: grey;">🇬🇧 English</span>

<!-- LANGUAGE_LINKS_END -->

# Tagit - Automatic Git Tagging and Version Management

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/dbt1/tagit)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-hardened-green.svg)](SECURITY.md)

`Tagit` is a secure and robust tool for automatic version management in Git repositories. It automates the update of version numbers in various project files and creates corresponding Git tags with enhanced security and error handling.

## New Features in Version 0.3.0

* **🔒 Enhanced Security**: Full protection against command injection and path traversal
* **🧪 Dry-Run Mode**: Safely test changes before applying them
* **📊 Improved Error Handling**: Detailed error messages and safe rollback mechanisms
* **⚡ Performance Optimizations**: LRU caching for repeated Git operations
* **🎯 Extended CLI**: New options for better control and debugging
* **🛡️ Input Validation**: Strict validation of all user inputs
* **📝 Better Logging**: Structured outputs with timestamps

## Table of Contents

* [Tagit - Automatic Git Tagging and Version Management](#tagit---automatic-git-tagging-and-version-management)

  * [New Features in Version 0.3.0](#new-features-in-version-030)
  * [Table of Contents](#table-of-contents)
  * [Features](#features)
  * [Requirements](#requirements)

    * [Use a Virtual Environment (recommended)](#use-a-virtual-environment-recommended)
    * [System-wide](#system-wide)
  * [Installation](#installation)

    * [Option 1: Direct Download](#option-1-direct-download)
    * [Option 2: Git Clone](#option-2-git-clone)
    * [Option 3: System-wide Installation](#option-3-system-wide-installation)
  * [Usage](#usage)

    * [Basic Commands](#basic-commands)
    * [Advanced Examples](#advanced-examples)

      * [1. Dry-Run Mode](#1-dry-run-mode)
      * [2. Version Control](#2-version-control)
      * [3. Custom Tag Formats](#3-custom-tag-formats)
      * [4. Micro Versioning](#4-micro-versioning)
    * [Command-Line Options](#command-line-options)
    * [Git Hook Integration](#git-hook-integration)
  * [Supported Versioning Schemes](#supported-versioning-schemes)
  * [Custom Versioning Schemes](#custom-versioning-schemes)

    * [Example JSON Configuration File](#example-json-configuration-file)
    * [Schema Structure](#schema-structure)
  * [Security](#security)

    * [Implemented Security Measures](#implemented-security-measures)
    * [Best Practices](#best-practices)
  * [Logging](#logging)
  * [Troubleshooting](#troubleshooting)

    * [Common Issues](#common-issues)
  * [Migration from Older Versions](#migration-from-older-versions)
  * [Development](#development)
  * [License](#license)
  * [Author](#author)

## Features

* **Automatic Git Tagging**: Creates Git tags based on the number of commits or manual increment
* **Version Updates in Project Files**: Updates version numbers in various file formats
* **Custom Versioning Schemes**: Extendable via JSON configuration files
* **Flexible Tag Format**: Supports placeholders for date, time, and version components
* **Dry-Run Mode**: Preview changes without execution
* **Secure Operations**: Automatic backups and rollback on errors
* **Comprehensive Validation**: Checks all inputs for safety and correctness

## Requirements

* Python 3.6 or higher
* GitPython
* Git (installed and configured)

### Use a Virtual Environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install GitPython
```

### System-wide

```bash
pip install GitPython
```

## Installation

### Option 1: Direct Download

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/v0.3.0/tagit.py
chmod +x tagit.py
```

### Option 2: Git Clone

```bash
git clone https://github.com/dbt1/tagit.git
cd tagit
chmod +x tagit.py
```

### Option 3: System-wide Installation

```bash
sudo curl -o /usr/local/bin/tagit https://raw.githubusercontent.com/dbt1/tagit/v0.3.0/tagit.py
sudo chmod +x /usr/local/bin/tagit
```

## Usage

### Basic Commands

```bash
# Show help
./tagit.py --help

# Show version
./tagit.py --version

# Automatic tagging (based on commits)
./tagit.py

# Update files and tag
./tagit.py -f version.txt -f configure.ac

# Only update files, no tag
./tagit.py -f package.json --no-tag
```

### Advanced Examples

#### 1. Dry-Run Mode

Test changes before applying:

```bash
# Show what would be changed
./tagit.py -f version.txt --dry-run

# With verbose output
./tagit.py -f configure.ac --dry-run -v
```

#### 2. Version Control

```bash
# Override major version
./tagit.py --major 2

# Set complete version
./tagit.py --major 1 --minor 5 --patch 0

# Set initial version
./tagit.py --initial-version 1.0.0
```

#### 3. Custom Tag Formats

```bash
# With date in tag
./tagit.py --tag-format 'v{major}.{minor}.{patch}-{YYYY}{MM}{DD}'

# With time
./tagit.py --tag-format 'release-{major}.{minor}.{patch}-{hh}{mm}{ss}'

# Year and month only
./tagit.py --tag-format '{YYYY}.{MM}.{patch}'
```

#### 4. Micro Versioning

For 4-part version numbers:

```bash
./tagit.py --tag-format '{major}.{minor}.{micro}.{patch}' --micro 1
```

### Command-Line Options

| Option              | Short | Description                                               |
| ------------------- | ----- | --------------------------------------------------------- |
| `--file`            | `-f`  | File to update (can be used multiple times)               |
| `--scheme-file`     |       | JSON file with custom schemes                             |
| `--tag-format`      |       | Format for Git tags (default: `v{major}.{minor}.{patch}`) |
| `--initial-version` |       | Initial version if no tags exist (default: `0.1.0`)       |
| `--version-mode`    |       | `commits` or `increment` for patch calculation            |
| `--no-tag`          |       | Only update files, do not create tag                      |
| `--dry-run`         |       | Show changes without executing                            |
| `--major`           |       | Override major version                                    |
| `--minor`           |       | Override minor version                                    |
| `--micro`           |       | Override micro version                                    |
| `--patch`           |       | Override patch version                                    |
| `--verbose`         | `-v`  | Verbose output                                            |
| `--version`         |       | Show program version                                      |

### Git Hook Integration

Automate Tagit with Git Hooks:

1. **Create hook directory**:

   ```bash
   mkdir -p .git/hooks
   ```

2. **Create pre-push hook**:

   ```bash
   cat > .git/hooks/pre-push << 'EOF'
   #!/bin/sh
   # Run Tagit before push

   python3 path/to/tagit.py -f version.txt --dry-run || {
       echo "Version check failed. Run without --dry-run to update."
       exit 1
   }
   EOF

   chmod +x .git/hooks/pre-push
   ```

## Supported Versioning Schemes

Tagit supports the following formats by default:

* **ac\_init**: Autoconf `configure.ac` files (`AC_INIT([name], [version], [email])`)
* **version\_assignment**: Version assignments (`VERSION = "X.X.X"`)
* **define\_ver**: Define macros (`define(ver_major, X)`)
* **env\_version**: Environment variables (`VERSION_MAJOR="X"`)

## Custom Versioning Schemes

Create a `tagit-config.json` in the repository root or load it with `--scheme-file`:

### Example JSON Configuration File

```json
[
  {
    "name": "package_json",
    "patterns": {
      "version": "\"version\":\\s*\"\\d+\\.\\d+\\.\\d+\""
    },
    "replacements": {
      "version": "\"version\": \"{major}.{minor}.{patch}\""
    }
  },
  {
    "name": "cmake_project",
    "patterns": {
      "version": "project\\(\\w+\\s+VERSION\\s+\\d+\\.\\d+\\.\\d+\\)"
    },
    "replacements": {
      "version": "project(${PROJECT_NAME} VERSION {major}.{minor}.{patch})"
    }
  }
]
```

### Schema Structure

Each schema requires:

* `name`: Unique name of the scheme
* `patterns`: Dictionary with regex patterns for finding
* `replacements`: Dictionary with replacement strings (with placeholders)

Available placeholders:

* `{major}`, `{minor}`, `{patch}`, `{micro}`: Version components
* `{YYYY}`, `{YY}`, `{MM}`, `{DD}`: Date
* `{hh}`, `{mm}`, `{ss}`: Time

## Security

### Implemented Security Measures

1. **Command Injection Protection**:

   * All Git commands run without `shell=True`
   * No interpretation of shell metacharacters

2. **Path Traversal Protection**:

   * Validation of all file paths
   * Access only within the repository directory

3. **Input Validation**:

   * Strict regex checking for version strings
   * Validation of tag formats for dangerous patterns

4. **Safe File Operations**:

   * Automatic backups before changes
   * Rollback on errors

### Best Practices

1. **Always use dry-run** for critical files
2. **Commit changes** before using Tagit
3. **Check the logs** with `--verbose` when problems occur
4. **Keep Tagit up to date** for the latest security updates

## Logging

Tagit provides structured logs with:

* Timestamps for all operations
* Log levels (INFO, WARNING, ERROR)
* Detailed error messages
* Verbose mode for debug information

```bash
# Normal output
2024-01-15 10:30:45 [INFO] Latest tag: v0.2.8
2024-01-15 10:30:45 [INFO] New version: 0.3.0

# Verbose mode
2024-01-15 10:30:45 [DEBUG] Running Git command: git describe --tags --abbrev=0
```

## Troubleshooting

### Common Issues

**"Not a Git repository"**:

```bash
cd /path/to/repository
./tagit.py -f version.txt
```

**"Working directory not clean"**:

```bash
# Option 1: Commit changes
git add . && git commit -m "Save changes"

# Option 2: Stash changes
git stash
```

**"No matching scheme found"**:

```bash
# Create a matching schema file
./tagit.py -f myfile --scheme-file custom-schemas.json
```

**Enable debug mode**:

```bash
./tagit.py -v -f problematic-file.txt
```

## Migration from Older Versions

From version 0.2.x to 0.3.0:

1. **No breaking changes**: Core functionality remains the same
2. **New features**: Use `--dry-run` to test safely
3. **Improved security**: No changes needed
4. **Schema compatibility**: Existing `tagit-config.json` still works

## Development

Contributions are welcome! Please note:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure code follows security guidelines
5. Create a pull request

## License

Tagit is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Created by **Thilo Graf**

---

**Version 0.3.0** - Focused on security, reliability, and usability.
