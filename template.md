# Tagit - Automatisches Git-Tagging und Versionsaktualisierung

## Inhaltsverzeichnis

- [Tagit - Automatisches Git-Tagging und Versionsaktualisierung](#tagit---automatisches-git-tagging-und-versionsaktualisierung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Funktionen](#funktionen)
  - [Anforderungen](#anforderungen)
  - [Installation](#installation)
  - [Verwendung](#verwendung)
    - [Beispiele](#beispiele)
  - [Unterstützte Versionierungsschemata](#unterstützte-versionierungsschemata)
    - [Benutzerdefinierte Versionierungsschemata](#benutzerdefinierte-versionierungsschemata)
  - [Protokollierung](#protokollierung)

`Tagit` ist ein Skript, dass das Versions-Tagging in Git-Repositories automatisiert und Versionsnummern in bestimmten Projektdateien aktualisiert. Das Skript bietet eine automatische Verwaltung von Versionierungsschemata, was es einfacher macht, konsistente Versionsnummern in mehreren Dateien deines Projekts beizubehalten.

## Funktionen

- **Automatisches Git-Tagging**: Erstellt Git-Tags für deine Commits, um eine einfache Versionsverfolgung zu ermöglichen.
- **Versionsaktualisierung in Projektdateien**: Aktualisiert Versionsnummern in angegebenen Dateien basierend auf vordefinierten Versionierungsschemata.
- **Benutzerdefinierte Versionierungsschemata**: Unterstützt zusätzliche Versionierungsschemata über eine `json`-Konfigurationsdatei.

## Anforderungen

- Python 3
- GitPython

Um die Abhängigkeiten zu installieren, verwende:

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

Ohne Angabe von Dateien ausführen, um die neueste Version zu taggen:
  ```sh
  python tagit.py
  ```

oder mit Optionen

  ```sh
  python tagit.py [Options]
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

## Unterstützte Versionierungsschemata

`Tagit` kommt mit vordefinierten Versionierungsschemata, die bei Bedarf mit einer JSON-Konfigurationsdatei erweitert werden können:

- **ac_init**: Findet und aktualisiert die Version in `AC_INIT()`-Makros, die in `configure.ac`-Dateien verwendet werden.
- **version_assignment**: Findet `VERSION = "X.X.X"` Zuweisungsanweisungen.
- **define_ver**: Aktualisiert Versionsmakros wie `define(ver_major, X)`.
- **env_version**: Aktualisiert Umgebungsvariablen wie `VERSION_MAJOR="X"`.

### Benutzerdefinierte Versionierungsschemata

Du kannst zusätzliche Versionierungsschemata hinzufügen, indem du eine JSON-Konfigurationsdatei mit der Option `--scheme-file` angibst. Dadurch kannst du benutzerdefinierte Muster und Ersetzungszeichenfolgen für Versionsaktualisierungen in beliebigen Dateien definieren.

## Protokollierung

`Tagit` bietet eine detaillierte Protokollierung für jede ausgeführte Aktion. Protokolleinträge beinhalten:

- Versionsaktualisierungen in Dateien
- Git-Tagging-Aktionen
- Warnungen und Fehler, falls Probleme auftreten
