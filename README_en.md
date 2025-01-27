<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | <span style="color: grey;">🇬🇧 English</span> | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Automatic Git tagging and version updating

Version: 0.2.8

## Table of contents

- [Tagit - Automatic Git tagging and version updating](#tagit---automatic-git-tagging-and-version-updating)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
    - [Use virtual environment (recommended)](#use-virtual-environment-recommended)
    - [Systemwide](#system-wide)
  - [Installation](#installation)
  - [Usage](#use)
    - [Examples](#examples)
    - [Git Hook Integration](#git-hook-integration)
  - [Supported versioning schemes](#supported-versioning-schemes)
  - [Custom Versioning Schemes](#custom-versioning-schemes)
    - [Example JSON configuration file](#example-json-configuration-file)
    - [Explanation of each scheme](#explanation-of-each-scheme)
      - [ac\_init](#ac_init)
      - [version\_assignment](#version_assignment)
      - [version\_colon\_format](#version_colon_format)
      - [define\_ver](#define_ver)
      - [env\_version](#env_version)
      - [python\_setup](#python_setup)
      - [package\_json](#package-json)
      - [cpp\_header](#cpp_header)
      - [xml\_version](#xml_version)
      - [ini\_version](#ini_version)
      - [markdown\_badge](#markdown_badge)
      - [ruby\_gemspec](#ruby-gemspec)
  - [Logging](#logging)
  - [License](#license)
  - [Author](#author)

`Tagit` is a script that automates version tagging in Git repositories and updates version numbers in specific project files. The script provides automatic management of versioning schemes, making it easier to maintain consistent version numbers across multiple files in your project.

## Features

- **Automatic Git Tagging**: Generates Git tags based on different patch determination methods (number of commits or incrementation).
- **Version Update in Project Files**: Updates version numbers in specified files based on predefined versioning schemes. Supports various versioning formats (e.g. AC_INIT, VERSION = "X.X.X", define(ver_major, X))
- **Custom versioning schemes**: Supports additional versioning schemes via an `json` ​​scheme configuration file.
- **Flexible Tag Format**: Allows you to define custom wildcard tag formats for major, minor and patch versions through customizable wildcard formats such as {YYYY}, {MM}, {DD}, {major} , {minor}, and {patch}, also for date and time: Use {YYYY}, {MM}, {DD}, {hh}, {mm}, {ss} to automatically integrate the current date and time.
- **Initial version and version mode**: Allows you to set an initial version.

## Requirements

- Python 3
- GitPython

To install the dependencies use:

### Use virtual environment (recommended)

```sh
python3 -m venv venv && source venv/bin/activate && pip install GitPython
```

### System-wide

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

If no tag has yet been assigned in the repository, a tag will be created automatically. You can also set the initial tag yourself.

```sh
python tagit.py --initial-version 1.0.0
```

Run without specifying files to tag the latest version:
```sh
python tagit.py
```

or with options:
```sh
python tagit.py [Optionen]
```

### Examples

- Update tagging and version numbers in multiple files:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Additional versioning schemes with an `JSON` scheme configuration file:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```
- Tagging with versioning schemes from an `JSON` scheme configuration file
  ```sh
  python tagit.py --scheme-file custom_schemes.json --tag-format '{major}.{minor}.{patch}'
  ```
- Custom Tag Format:
  ```sh
  python tagit.py --file configure.ac --tag-format release-{major}.{minor}.{patch}
  ```
- Set initial version and increment patch version:
  ```sh
  python tagit.py --tag-format none --initial-version 1.0.0 --version-mode increment
  ```
- Tagging with year and month placeholders
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}'
  ```
- Tagging with date and time
  ```sh
  python tagit.py --tag-format 'v{major}.{minor}.{patch}-{YY}{MM}{DD}-{hh}{mm}{ss}'
  ```
- Tagging with year, month
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}' -f configure.ac
  ```
- Update files without creating a tag:

  ```sh
  python tagit.py -f configure.ac --no-tag
  ```
### Git hook integration

You can integrate `Tagit` into your Git workflow by using it as a pre-push hook. This ensures that version numbers and tags are automatically updated before you push changes to the remote repository.

Here is a guide to use the script as a pre-push hook:

1. Create the Git hook folder if it does not exist:

   ```sh
   mkdir -p .git/hooks
   ```

2. Create a file named `pre-push` in the `.git/hooks/` directory and make it executable:

   ```sh
   touch .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

3. Edit the `.git/hooks/pre-push` file and add the following content:

   ```sh
   #!/bin/sh
   # Pre-Push Hook to run Tagit before pushing
   
   python3 path/to/tagit.py -f configure.ac -f version.txt || {
       echo "Tagit failed. Push aborted."
       exit 1
   }
   ```

   Replace `path/to/tagit.py` with the actual path to your Tagit script and `configure.ac`, `version.txt` with the files you want to update.

4. Save the changes and close the file.

Now every time you try to push changes, the Tagit script will be executed. If Tagit fails, the push will be canceled so you can ensure versions remain consistent.


## Supported versioning schemes

`Tagit` comes with predefined versioning schemes, which can be extended with a JSON configuration file if necessary:

- **ac_init**: Finds and updates the version in `AC_INIT()` macros used in `configure.ac` files.
- **version_assignment**: Finds `VERSION = "X.X.X"` assignment instructions.
- **define_ver**: Updates version macros like `define(ver_major, X)`.
- **env_version**: Updates environment variables like `VERSION_MAJOR="X"`.

## Custom versioning schemes

You can add additional versioning schemes by specifying a JSON configuration file with the `--scheme-file` option. This allows you to define custom patterns and replacement strings for version updates in any files.

### Example JSON configuration file

Here is an example JSON configuration file that defines custom versioning schemes:

```json
[
    {
        "name": "ac_init",
        "_comment": "Updates the version number in Autoconf 'configure.ac' files using the AC_INIT macro.",
        "patterns": {
            "version": "(AC_INIT\\(\\[.*?\\],\\s*\\[)\\d+\\.\\d+\\.\\d+(\\],\\s*\\[.*?\\]\\))"
        },
        "replacements": {
            "version": "\\g<1>{major}.{minor}.{micro}\\g<2>"
        }
    },
    {
        "name": "version_assignment",
        "_comment": "Updates versions in scripts or configuration files. Supports both 'VERSION' and 'version'.",
        "patterns": {
            "version": "(VERSION|version)\\s*=\\s*\"\\d+\\.\\d+\\.\\d+\""
        },
        "replacements": {
            "version": "\\1 = \"{major}.{minor}.{patch}\""
        }
    },
    {
        "name": "define_ver",
        "_comment": "Updates version definitions in files using 'define' macros.",
        "patterns": {
            "ver_major": "define\\(ver_major,\\s*\\d+\\)",
            "ver_minor": "define\\(ver_minor,\\s*\\d+\\)",
            "ver_micro": "define\\(ver_micro,\\s*\\d+\\)"
        },
        "replacements": {
            "ver_major": "define(ver_major, {major})",
            "ver_minor": "define(ver_minor, {minor})",
            "ver_micro": "define(ver_micro, {micro})"
        }
    },
    {
        "name": "env_version",
        "_comment": "Updates environment variable assignments for version numbers.",
        "patterns": {
            "VERSION_MAJOR": "VERSION_MAJOR=\"\\d+\"",
            "VERSION_MINOR": "VERSION_MINOR=\"\\d+\"",
            "VERSION_PATCH": "VERSION_PATCH=\"\\d+\""
        },
        "replacements": {
            "VERSION_MAJOR": "VERSION_MAJOR=\"{major}\"",
            "VERSION_MINOR": "VERSION_MINOR=\"{minor}\"",
            "VERSION_PATCH": "VERSION_PATCH=\"{patch}\""
        }
    },
    {
        "name": "version_colon_format",
        "_comment": "Updates version numbers in files with the format 'Version: X.X.X'.",
        "patterns": {
            "version": "Version:\\s*\\d+(\\.\\d+)+"
        },
        "replacements": {
            "version": "Version: {major}.{minor}.{patch}"
        }
    },
    {
        "name": "python_setup",
        "_comment": "Updates the version number in Python 'setup.py' files.",
        "patterns": {
            "version": "version=\\\"\\d+\\.\\d+\\.\\d+\\\""
        },
        "replacements": {
            "version": "version=\"{major}.{minor}.{patch}\""
        }
    },
    {
        "name": "package_json",
        "_comment": "Updates the version number in 'package.json' files for Node.js projects.",
        "patterns": {
            "version": "\"version\":\\s*\"\\d+\\.\\d+\\.\\d+\""
        },
        "replacements": {
            "version": "\"version\": \"{major}.{minor}.{patch}\""
        }
    },
    {
        "name": "cpp_header",
        "_comment": "Updates version numbers in C++ header files.",
        "patterns": {
            "VERSION_MAJOR": "#define\\s+VERSION_MAJOR\\s+\\d+",
            "VERSION_MINOR": "#define\\s+VERSION_MINOR\\s+\\d+",
            "VERSION_PATCH": "#define\\s+VERSION_PATCH\\s+\\d+"
        },
        "replacements": {
            "VERSION_MAJOR": "#define VERSION_MAJOR {major}",
            "VERSION_MINOR": "#define VERSION_MINOR {minor}",
            "VERSION_PATCH": "#define VERSION_PATCH {patch}"
        }
    },
    {
        "name": "xml_version",
        "_comment": "Updates version numbers in XML files.",
        "patterns": {
            "version": "<version>\\d+\\.\\d+\\.\\d+</version>"
        },
        "replacements": {
            "version": "<version>{major}.{minor}.{patch}</version>"
        }
    },
    {
        "name": "ini_version",
        "_comment": "Updates version numbers in INI configuration files.",
        "patterns": {
            "version": "version=\\d+\\.\\d+\\.\\d+"
        },
        "replacements": {
            "version": "version={major}.{minor}.{patch}"
        }
    },
    {
        "name": "markdown_badge",
        "_comment": "Updates version badges in 'README.md' files.",
        "patterns": {
            "version": "\\[!\\[Version\\]\\(https://img\\.shields\\.io/badge/version-\\d+\\.\\d+\\.\\d+-blue\\.svg\\)\\]\\(.*?\\)"
        },
        "replacements": {
            "version": "[![Version](https://img.shields.io/badge/version-{major}.{minor}.{patch}-blue.svg)](URL_TO_PROJECT)"
        }
    },
    {
        "name": "ruby_gemspec",
        "_comment": "Updates the version number in Ruby '.gemspec' files.",
        "patterns": {
            "version": "\\.version\\s*=\\s*\"\\d+\\.\\d+\\.\\d+\""
        },
        "replacements": {
            "version": ".version = \"{major}.{minor}.{patch}\""
        }
    }
]

```

### Explanation of each scheme

#### ac_init
- **Purpose**: Updates the version in `configure.ac` files using the `AC_INIT` macro.
- **Example**:
  ```m4
  AC_INIT([MyProject], [0.2.9], [support@example.com])
  ```
- **Description**: Searches for the `AC_INIT` macro and updates the version number.

#### version_assignment
- **Purpose**: General versioning assignment in scripts or configuration files.
- **Example**:
  ```bash
  VERSION = "0.1.0"
  ```
- **Description**: Searches for lines containing `VERSION = "..."` and replaces the version.

#### version_colon_format

- **Purpose**: Updates version numbers in files with version: X.X.X format.
- **Example**:
  ```txt
  Version: 0.0.0
  ``` 
**Description**: Searches for lines that start with version: and contain a version number and updates them.

#### define_ver
- **Purpose**: Version definitions in files using macros.
- **Example**:
  ```m4
  define(ver_major, 0)
  define(ver_minor, 1)
  define(ver_micro, 0)
  ```
- **Description**: Replaces major, minor and patch versions in macros.

#### env_version
- **Purpose**: Sets version numbers for environment variables.
- **Example**:
  ```bash
  VERSION_MAJOR="0"
  VERSION_MINOR="1"
  VERSION_PATCH="0"
  ```
- **Description**: Updates the environment variables with the new version.

#### python_setup
- **Purpose**: Updates the version in `setup.py` for Python packages.
- **Example**:
  ```python
  setup(
      name='mypackage',
      version="0.1.0",
      ...
  )
  ```
- **Description**: Searches for the version in `setup.py` and replaces it.

#### package json
- **Purpose**: Updates the version in `package.json` for Node.js projects.
- **Example**:
  ```json
  {
    "name": "myproject",
    "version": "0.1.0",
    ...
  }
  ```
- **Description**: Searches for and updates the version field in `package.json`.

#### cpp_header
- **Purpose**: Updates version numbers in C/C++ header files.
- **Example**:
  ```cpp
  #define VERSION_MAJOR 0
  #define VERSION_MINOR 1
  #define VERSION_PATCH 0
  ```
- **Description**: Replaces version numbers in `#define` directives.

#### xml_version
- **Purpose**: Updates version numbers in XML files.
- **Example**:
  ```xml
  <version>0.1.0</version>
  ```
- **Description**: Finds the `<version>` tag and updates the version number.

#### ini_version
- **Purpose**: Updates version numbers in INI files.
- **Example**:
  ```ini
  version=0.1.0
  ```
- **Description**: Finds the version setting and replaces it.

#### markdown_badge
- **Purpose**: Updates version badges in `README.md` files.
- **Example**:
  ```markdown
  [![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/username/repository)
  ```
- **Description**: Replaces the version number in the badge link.

#### ruby gemspec
- **Purpose**: Updates the version number in `.gemspec` files for Ruby.
- **Example**:
  ```ruby
  Gem::Specification.new do |spec|
    spec.name        = 'mygem'
    spec.version     = "0.1.0"
    ...
  end
  ```
- **Description**: Searches for `.version` in `.gemspec` files and updates them.

## Logging

`Tagit` provides detailed logging for every action performed. Log entries include:

- Version updates in files
- Git tagging actions
- Warnings and errors if problems occur

## License

`Tagit` is licensed under the MIT License.

## author

Created by Thilo Graf.
