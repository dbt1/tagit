<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | <span style="color: grey;">🇬🇧 English</span> | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Automatic Git tagging and version updating

## Table of contents

- [Tagit - Automatic Git tagging and version updating](#tagit---automatic-git-tagging-and-version-updating)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#use)
    - [Examples](#examples)
  - [Supported versioning schemes](#supported-versioning-schemes)
    - [Custom versioning schemes](#custom-versioning-schemes)
  - [Logging](#logging)

`Tagit` is a script that automates version tagging in Git repositories and updates version numbers in specific project files. The script provides automatic management of versioning schemes, making it easier to maintain consistent version numbers across multiple files in your project.

## Features

- **Automatic Git Tagging**: Creates Git tags for your commits to enable easy version tracking.
- **Version Update in Project Files**: Updates version numbers in specified files based on predefined versioning schemes.
- **Custom versioning schemes**: Supports additional versioning schemes via an `json` ​​configuration file.

## Requirements

- Python 3
- GitPython

To install the dependencies use:

```sh
pip install GitPython
```
## installation

Use `curl` to download the script directly to a location of your choice:

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/master/tagit.py
```

**or**

Use `git clone` to clone the entire source to a location of your choice:

```bash
git clone https://github.com/dbt1/tagit.git
```

You can run `Tagit` from a location of your choice, either directly where it is after cloning or in the same directory where `Tagit` is located. If `Tagit` is to be executed directly, the script must be made executable by changing the permission depending on the system.

```bash
chmod +x dateiname.py
```

## use

> **Note**: If no tag has yet been assigned in the repository, a tag will be created automatically.

Run without specifying files to tag the latest version:
  ```sh
  python tagit.py
  ```

or with options

  ```sh
  python tagit.py [Options]
  ```

### Examples

- Update tagging and version numbers in multiple files:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Specify additional versioning schemes with an `JSON` configuration file:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```

## Supported versioning schemes

`Tagit` comes with predefined versioning schemes, which can be extended with a JSON configuration file if necessary:

- **ac_init**: Finds and updates the version in `AC_INIT()` macros used in `configure.ac` files.
- **version_assignment**: Finds `VERSION = "X.X.X"` assignment instructions.
- **define_ver**: Updates version macros like `define(ver_major, X)`.
- **env_version**: Updates environment variables like `VERSION_MAJOR="X"`.

### Custom versioning schemes

You can add additional versioning schemes by specifying a JSON configuration file with the `--scheme-file` option. This allows you to define custom patterns and replacement strings for version updates in any files.

## Logging

`Tagit` provides detailed logging for every action taken. Log entries include:

- Version updates in files
- Git tagging actions
- Warnings and errors if problems occur
