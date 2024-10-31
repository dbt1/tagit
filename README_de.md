<!-- LANGUAGE_LINKS_START -->
<span style="color: grey;">🇩🇪 German</span> | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Automatisches Git-Tagging und Versionsaktualisierung

## Inhaltsverzeichnis

- [Tagit - Automatisches Git-Tagging und Versionsaktualisierung](#tagit---automatisches-git-tagging-und-versionsaktualisierung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Funktionen](#funktionen)
  - [Anforderungen](#anforderungen)
    - [Virtuelle Umgebung nutzen (empfohlen)](#virtuelle-umgebung-nutzen-empfohlen)
    - [Systemweit](#systemweit)
  - [Installation](#installation)
  - [Verwendung](#verwendung)
    - [Beispiele](#beispiele)
    - [Git Hook Integration](#git-hook-integration)
  - [Unterstützte Versionierungsschemata](#unterstützte-versionierungsschemata)
  - [Benutzerdefinierte Versionierungsschemata](#benutzerdefinierte-versionierungsschemata)
    - [Beispiel JSON-Konfigurationsdatei](#beispiel-json-konfigurationsdatei)
    - [Erklärung zu jedem Schema](#erklärung-zu-jedem-schema)
      - [ac\_init](#ac_init)
      - [version\_assignment](#version_assignment)
      - [define\_ver](#define_ver)
      - [env\_version](#env_version)
      - [python\_setup](#python_setup)
      - [package\_json](#package_json)
      - [cpp\_header](#cpp_header)
      - [xml\_version](#xml_version)
      - [ini\_version](#ini_version)
      - [markdown\_badge](#markdown_badge)
      - [ruby\_gemspec](#ruby_gemspec)
  - [Protokollierung](#protokollierung)
  - [Lizenz](#lizenz)
  - [Autor](#autor)

`Tagit` ist ein Skript, das das Versions-Tagging in Git-Repositories automatisiert und Versionsnummern in bestimmten Projektdateien aktualisiert. Das Skript bietet eine automatische Verwaltung von Versionierungsschemata, was es einfacher macht, konsistente Versionsnummern in mehreren Dateien deines Projekts beizubehalten.

## Funktionen

- **Automatisches Git-Tagging**: Erstellt Git-Tags für deine Commits, um eine einfache Versionsverfolgung zu ermöglichen.
- **Versionsaktualisierung in Projektdateien**: Aktualisiert Versionsnummern in angegebenen Dateien basierend auf vordefinierten Versionierungsschemata.
- **Benutzerdefinierte Versionierungsschemata**: Unterstützt zusätzliche Versionierungsschemata über eine `json`-Konfigurationsdatei.
- **Flexibles Tag-Format**: Definiere ein benutzerdefiniertes Tag-Format mit Platzhaltern für Major-, Minor- und Patch-Versionen.
- **Initialversion und Versionsmodus**: Ermöglicht das Setzen einer Initialversion und die Wahl zwischen unterschiedlichen Methoden zur Patch-Bestimmung (Anzahl der Commits oder Inkrementierung).

## Anforderungen

- Python 3
- GitPython

Um die Abhängigkeiten zu installieren, verwende:

### Virtuelle Umgebung nutzen (empfohlen)

```sh
python3 -m venv venv && source venv/bin/activate && pip install GitPython
```

### Systemweit

```sh
pip install GitPython
```

## Installation

Verwende `curl`, um das Skript direkt an einen Ort deiner Wahl herunterzuladen:

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/master/tagit.py
```

**oder**

Verwende `git clone`, um die gesamten Sourcen an einen Ort deiner Wahl zu klonen:

```bash
git clone https://github.com/dbt1/tagit.git
```

Du kannst `Tagit` von einem Ort deiner Wahl ausführen, entweder direkt dort, wo es sich nach dem Klonen befindet, oder im selben Verzeichnis, in dem sich `Tagit` befindet. Wenn `Tagit` direkt ausgeführt werden soll, muss das Skript je nach System ausführbar gemacht werden, indem du die Berechtigung änderst.

```bash
chmod +x dateiname.py
```

## Verwendung

> **Hinweis**: Wenn im Repository noch kein Tag vergeben wurde, wird automatisch ein Tag angelegt.

Ohne Angabe von Dateien ausführen, um die neueste Version zu taggen:
```sh
python tagit.py
```

oder mit Optionen:
```sh
python tagit.py [Optionen]
```

### Beispiele

- Taggen und Versionsnummern in mehreren Dateien aktualisieren:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Zusätzliche Versionierungsschemata mit einer `JSON`-Konfigurationsdatei angeben:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```
- Benutzerdefiniertes Tag-Format angeben:
  ```sh
  python tagit.py --file configure.ac --tag-format release-{major}.{minor}.{patch}
  ```
- Initialversion setzen und Patch-Version inkrementieren:
  ```sh
  python tagit.py --tag-format none --initial-version 1.0.0 --version-mode increment
  ```

### Git Hook Integration

Du kannst `Tagit` in deinen Git-Workflow integrieren, indem du es als Pre-Push Hook verwendest. Dies stellt sicher, dass die Versionsnummern und Tags automatisch aktualisiert werden, bevor du Änderungen ins Remote-Repository pushst.

Hier ist eine Anleitung, um das Skript als Pre-Push Hook zu verwenden:

1. Erstelle den Git-Hook-Ordner, falls er nicht existiert:

   ```sh
   mkdir -p .git/hooks
   ```

2. Erstelle eine Datei namens `pre-push` im Verzeichnis `.git/hooks/` und mache sie ausführbar:

   ```sh
   touch .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

3. Bearbeite die Datei `.git/hooks/pre-push` und füge folgenden Inhalt hinzu:

   ```sh
   #!/bin/sh
   # Pre-Push Hook to run Tagit before pushing
   
   # Ausführen von Tagit, um automatisch Versionen zu aktualisieren
   python3 path/to/tagit.py -f configure.ac -f version.txt || {
       echo "Tagit failed. Push aborted."
       exit 1
   }
   ```

   Ersetze `path/to/tagit.py` durch den tatsächlichen Pfad zu deinem Tagit-Skript und `configure.ac`, `version.txt` durch die Dateien, die du aktualisieren möchtest.

4. Speichere die Änderungen und schließe die Datei.

Jetzt wird jedes Mal, wenn du versuchst, Änderungen zu pushen, das Tagit-Skript ausgeführt. Wenn Tagit fehlschlägt, wird der Push abgebrochen, sodass du sicherstellen kannst, dass die Versionen konsistent bleiben.


## Unterstützte Versionierungsschemata

`Tagit` kommt mit vordefinierten Versionierungsschemata, die bei Bedarf mit einer JSON-Konfigurationsdatei erweitert werden können:

- **ac_init**: Findet und aktualisiert die Version in `AC_INIT()`-Makros, die in `configure.ac`-Dateien verwendet werden.
- **version_assignment**: Findet `VERSION = "X.X.X"` Zuweisungsanweisungen.
- **define_ver**: Aktualisiert Versionsmakros wie `define(ver_major, X)`.
- **env_version**: Aktualisiert Umgebungsvariablen wie `VERSION_MAJOR="X"`.

## Benutzerdefinierte Versionierungsschemata

Du kannst zusätzliche Versionierungsschemata hinzufügen, indem du eine JSON-Konfigurationsdatei mit der Option `--scheme-file` angibst. Dadurch kannst du benutzerdefinierte Muster und Ersetzungszeichenfolgen für Versionsaktualisierungen in beliebigen Dateien definieren.

### Beispiel JSON-Konfigurationsdatei

Hier ist ein Beispiel für eine JSON-Konfigurationsdatei, die benutzerdefinierte Versionierungsschemata definiert:

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

### Erklärung zu jedem Schema

#### ac_init
- **Zweck**: Aktualisiert die Version in `configure.ac`-Dateien unter Verwendung des `AC_INIT`-Makros.
- **Beispiel**:
  ```m4
  AC_INIT([MyProject], [0.1.0], [support@example.com])
  ```
- **Beschreibung**: Sucht nach dem `AC_INIT`-Makro und aktualisiert die Versionsnummer.

#### version_assignment
- **Zweck**: Allgemeine Versionierungszuweisung in Skripten oder Konfigurationsdateien.
- **Beispiel**:
  ```bash
  VERSION = "0.1.0"
  ```
- **Beschreibung**: Sucht nach Zeilen, die `VERSION = "..."` enthalten, und ersetzt die Version.

#### define_ver
- **Zweck**: Versionsdefinitionen in Dateien unter Verwendung von Makros.
- **Beispiel**:
  ```m4
  define(ver_major, 0)
  define(ver_minor, 1)
  define(ver_micro, 0)
  ```
- **Beschreibung**: Ersetzt die Haupt-, Neben- und Patch-Versionen in Makros.

#### env_version
- **Zweck**: Setzt Versionsnummern für Umgebungsvariablen.
- **Beispiel**:
  ```bash
  VERSION_MAJOR="0"
  VERSION_MINOR="1"
  VERSION_PATCH="0"
  ```
- **Beschreibung**: Aktualisiert die Umgebungsvariablen mit der neuen Version.

#### python_setup
- **Zweck**: Aktualisiert die Version in `setup.py` für Python-Pakete.
- **Beispiel**:
  ```python
  setup(
      name='mypackage',
      version="0.1.0",
      ...
  )
  ```
- **Beschreibung**: Sucht nach der Version in `setup.py` und ersetzt sie.

#### package_json
- **Zweck**: Aktualisiert die Version in `package.json` für Node.js-Projekte.
- **Beispiel**:
  ```json
  {
    "name": "myproject",
    "version": "0.1.0",
    ...
  }
  ```
- **Beschreibung**: Sucht nach dem Versionsfeld in `package.json` und aktualisiert es.

#### cpp_header
- **Zweck**: Aktualisiert Versionsnummern in C/C++-Headerdateien.
- **Beispiel**:
  ```cpp
  #define VERSION_MAJOR 0
  #define VERSION_MINOR 1
  #define VERSION_PATCH 0
  ```
- **Beschreibung**: Ersetzt Versionsnummern in `#define`-Direktiven.

#### xml_version
- **Zweck**: Aktualisiert Versionsnummern in XML-Dateien.
- **Beispiel**:
  ```xml
  <version>0.1.0</version>
  ```
- **Beschreibung**: Findet das `<version>`-Tag und aktualisiert die Versionsnummer.

#### ini_version
- **Zweck**: Aktualisiert Versionsnummern in INI-Dateien.
- **Beispiel**:
  ```ini
  version=0.1.0
  ```
- **Beschreibung**: Findet die Versionseinstellung und ersetzt sie.

#### markdown_badge
- **Zweck**: Aktualisiert Versions-Badges in `README.md`-Dateien.
- **Beispiel**:
  ```markdown
  [![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/username/repository)
  ```
- **Beschreibung**: Ersetzt die Versionsnummer im Badge-Link.

#### ruby_gemspec
- **Zweck**: Aktualisiert die Versionsnummer in `.gemspec`-Dateien für Ruby.
- **Beispiel**:
  ```ruby
  Gem::Specification.new do |spec|
    spec.name        = 'mygem'
    spec.version     = "0.1.0"
    ...
  end
  ```
- **Beschreibung**: Sucht nach `.version` in `.gemspec`-Dateien und aktualisiert sie.

## Protokollierung

`Tagit` bietet eine detaillierte Protokollierung für jede ausgeführte Aktion. Protokolleinträge beinhalten:

- Versionsaktualisierungen in Dateien
- Git-Tagging-Aktionen
- Warnungen und Fehler, falls Probleme auftreten

## Lizenz

`Tagit` ist unter der MIT-Lizenz lizenziert.

## Autor

Erstellt von Thilo Graf.

