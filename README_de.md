<!-- LANGUAGE_LINKS_START -->
<span style="color: grey;">🇩🇪 German</span> | [🇬🇧 English](README_en.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Automatisches Git-Tagging und Versionsverwaltung

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/dbt1/tagit)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-hardened-green.svg)](SECURITY.md)

`Tagit` ist ein sicheres und robustes Tool zur automatischen Versionsverwaltung in Git-Repositories. Es automatisiert die Aktualisierung von Versionsnummern in verschiedenen Projektdateien und erstellt entsprechende Git-Tags mit verbesserter Sicherheit und Fehlerbehandlung.

## Neue Features in Version 0.3.0

- **🔒 Erhöhte Sicherheit**: Vollständiger Schutz vor Command Injection und Path Traversal
- **🧪 Dry-Run Modus**: Teste Änderungen sicher, bevor sie angewendet werden
- **📊 Verbesserte Fehlerbehandlung**: Detaillierte Fehlermeldungen und sichere Rollback-Mechanismen
- **⚡ Performance-Optimierungen**: LRU-Caching für wiederholte Git-Operationen
- **🎯 Erweiterte CLI**: Neue Optionen für bessere Kontrolle und Debugging
- **🛡️ Input-Validierung**: Strikte Überprüfung aller Benutzereingaben
- **📝 Besseres Logging**: Strukturierte Ausgaben mit Zeitstempeln

## Inhaltsverzeichnis

- [Tagit - Automatisches Git-Tagging und Versionsverwaltung](#tagit---automatisches-git-tagging-und-versionsverwaltung)
  - [Neue Features in Version 0.3.0](#neue-features-in-version-030)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Funktionen](#funktionen)
  - [Anforderungen](#anforderungen)
    - [Virtuelle Umgebung nutzen (empfohlen)](#virtuelle-umgebung-nutzen-empfohlen)
    - [Systemweit](#systemweit)
  - [Installation](#installation)
    - [Option 1: Direkter Download](#option-1-direkter-download)
    - [Option 2: Git Clone](#option-2-git-clone)
    - [Option 3: Systemweite Installation](#option-3-systemweite-installation)
  - [Verwendung](#verwendung)
    - [Grundlegende Befehle](#grundlegende-befehle)
    - [Erweiterte Beispiele](#erweiterte-beispiele)
      - [1. Dry-Run Modus](#1-dry-run-modus)
      - [2. Versionskontrolle](#2-versionskontrolle)
      - [3. Benutzerdefinierte Tag-Formate](#3-benutzerdefinierte-tag-formate)
      - [4. Micro-Versionierung](#4-micro-versionierung)
    - [Kommandozeilen-Optionen](#kommandozeilen-optionen)
    - [Git Hook Integration](#git-hook-integration)
  - [Unterstützte Versionierungsschemata](#unterstützte-versionierungsschemata)
  - [Benutzerdefinierte Versionierungsschemata](#benutzerdefinierte-versionierungsschemata)
    - [Beispiel JSON-Konfigurationsdatei](#beispiel-json-konfigurationsdatei)
    - [Schema-Struktur](#schema-struktur)
  - [Sicherheit](#sicherheit)
    - [Implementierte Sicherheitsmaßnahmen](#implementierte-sicherheitsmaßnahmen)
    - [Best Practices](#best-practices)
  - [Protokollierung](#protokollierung)
  - [Fehlerbehebung](#fehlerbehebung)
    - [Häufige Probleme](#häufige-probleme)
  - [Migration von älteren Versionen](#migration-von-älteren-versionen)
  - [Entwicklung](#entwicklung)
  - [Lizenz](#lizenz)
  - [Autor](#autor)

## Funktionen

- **Automatisches Git-Tagging**: Erstellt Git-Tags basierend auf der Anzahl der Commits oder manueller Inkrementierung
- **Versionsaktualisierung in Projektdateien**: Aktualisiert Versionsnummern in verschiedenen Dateiformaten
- **Benutzerdefinierte Versionierungsschemata**: Erweiterbar durch JSON-Konfigurationsdateien
- **Flexibles Tag-Format**: Unterstützt Platzhalter für Datum, Zeit und Versionskomponenten
- **Dry-Run Modus**: Vorschau der Änderungen ohne tatsächliche Ausführung
- **Sichere Operationen**: Automatische Backups und Rollback bei Fehlern
- **Umfassende Validierung**: Prüfung aller Eingaben auf Sicherheit und Korrektheit

## Anforderungen

- Python 3.6 oder höher
- GitPython
- Git (installiert und konfiguriert)

### Virtuelle Umgebung nutzen (empfohlen)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install GitPython
```

### Systemweit

```bash
pip install GitPython
```

## Installation

### Option 1: Direkter Download

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

### Option 3: Systemweite Installation

```bash
sudo curl -o /usr/local/bin/tagit https://raw.githubusercontent.com/dbt1/tagit/v0.3.0/tagit.py
sudo chmod +x /usr/local/bin/tagit
```

## Verwendung

### Grundlegende Befehle

```bash
# Hilfe anzeigen
./tagit.py --help

# Version anzeigen
./tagit.py --version

# Automatisches Tagging (erstellt Tag basierend auf Commits)
./tagit.py

# Dateien aktualisieren und taggen
./tagit.py -f version.txt -f configure.ac

# Nur Dateien aktualisieren, kein Tag erstellen
./tagit.py -f package.json --no-tag
```

### Erweiterte Beispiele

#### 1. Dry-Run Modus

Teste Änderungen, bevor sie angewendet werden:

```bash
# Zeigt, was geändert würde
./tagit.py -f version.txt --dry-run

# Mit verbose Output für Details
./tagit.py -f configure.ac --dry-run -v
```

#### 2. Versionskontrolle

```bash
# Major Version überschreiben
./tagit.py --major 2

# Komplette Version setzen
./tagit.py --major 1 --minor 5 --patch 0

# Initial-Version festlegen
./tagit.py --initial-version 1.0.0
```

#### 3. Benutzerdefinierte Tag-Formate

```bash
# Mit Datum im Tag
./tagit.py --tag-format 'v{major}.{minor}.{patch}-{YYYY}{MM}{DD}'

# Mit Uhrzeit
./tagit.py --tag-format 'release-{major}.{minor}.{patch}-{hh}{mm}{ss}'

# Nur Jahr und Monat
./tagit.py --tag-format '{YYYY}.{MM}.{patch}'
```

#### 4. Micro-Versionierung

Für 4-teilige Versionsnummern:

```bash
./tagit.py --tag-format '{major}.{minor}.{micro}.{patch}' --micro 1
```

### Kommandozeilen-Optionen

| Option | Kurz | Beschreibung |
|--------|------|--------------|
| `--file` | `-f` | Datei zum Aktualisieren (mehrfach verwendbar) |
| `--scheme-file` | | JSON-Datei mit benutzerdefinierten Schemata |
| `--tag-format` | | Format für Git-Tags (Standard: `v{major}.{minor}.{patch}`) |
| `--initial-version` | | Initialversion bei fehlenden Tags (Standard: `0.1.0`) |
| `--version-mode` | | `commits` oder `increment` für Patch-Berechnung |
| `--no-tag` | | Nur Dateien aktualisieren, kein Tag erstellen |
| `--dry-run` | | Zeigt Änderungen ohne Ausführung |
| `--major` | | Major-Version überschreiben |
| `--minor` | | Minor-Version überschreiben |
| `--micro` | | Micro-Version überschreiben |
| `--patch` | | Patch-Version überschreiben |
| `--verbose` | `-v` | Ausführliche Ausgabe |
| `--version` | | Zeigt Programmversion |

### Git Hook Integration

Automatisiere Tagit mit Git Hooks:

1. **Hook-Verzeichnis erstellen**:
   ```bash
   mkdir -p .git/hooks
   ```

2. **Pre-Push Hook erstellen**:
   ```bash
   cat > .git/hooks/pre-push << 'EOF'
   #!/bin/sh
   # Tagit vor dem Push ausführen
   
   python3 path/to/tagit.py -f version.txt --dry-run || {
       echo "Version check failed. Run without --dry-run to update."
       exit 1
   }
   EOF
   
   chmod +x .git/hooks/pre-push
   ```

## Unterstützte Versionierungsschemata

Tagit unterstützt standardmäßig folgende Formate:

- **ac_init**: Autoconf `configure.ac` Dateien (`AC_INIT([name], [version], [email])`)
- **version_assignment**: Version-Zuweisungen (`VERSION = "X.X.X"`)
- **define_ver**: Define-Makros (`define(ver_major, X)`)
- **env_version**: Umgebungsvariablen (`VERSION_MAJOR="X"`)

## Benutzerdefinierte Versionierungsschemata

Erstelle eine `tagit-config.json` im Repository-Root oder lade sie mit `--scheme-file`:

### Beispiel JSON-Konfigurationsdatei

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

### Schema-Struktur

Jedes Schema benötigt:
- `name`: Eindeutiger Name des Schemas
- `patterns`: Dictionary mit Regex-Mustern zum Finden
- `replacements`: Dictionary mit Ersetzungsstrings (mit Platzhaltern)

Verfügbare Platzhalter:
- `{major}`, `{minor}`, `{patch}`, `{micro}`: Versionskomponenten
- `{YYYY}`, `{YY}`, `{MM}`, `{DD}`: Datum
- `{hh}`, `{mm}`, `{ss}`: Zeit

## Sicherheit

### Implementierte Sicherheitsmaßnahmen

1. **Command Injection Schutz**:
   - Alle Git-Befehle werden ohne `shell=True` ausgeführt
   - Keine Interpretation von Shell-Metazeichen

2. **Path Traversal Schutz**:
   - Validierung aller Dateipfade
   - Zugriff nur innerhalb des Repository-Verzeichnisses

3. **Input-Validierung**:
   - Strikte Regex-Prüfung für Versionsstrings
   - Validierung von Tag-Formaten auf gefährliche Muster

4. **Sichere Dateioperationen**:
   - Automatische Backups vor Änderungen
   - Rollback bei Fehlern

### Best Practices

1. **Verwende immer Dry-Run** für kritische Dateien
2. **Committe Änderungen** vor der Verwendung von Tagit
3. **Prüfe die Logs** mit `--verbose` bei Problemen
4. **Halte Tagit aktuell** für neueste Sicherheitsupdates

## Protokollierung

Tagit bietet strukturierte Logs mit:
- Zeitstempel für alle Operationen
- Log-Level (INFO, WARNING, ERROR)
- Detaillierte Fehlermeldungen
- Verbose-Modus für Debug-Informationen

```bash
# Normale Ausgabe
2024-01-15 10:30:45 [INFO] Latest tag: v0.2.8
2024-01-15 10:30:45 [INFO] New version: 0.3.0

# Verbose-Modus
2024-01-15 10:30:45 [DEBUG] Running Git command: git describe --tags --abbrev=0
```

## Fehlerbehebung

### Häufige Probleme

**"Not a Git repository"**:
```bash
cd /pfad/zum/repository
./tagit.py -f version.txt
```

**"Working directory not clean"**:
```bash
# Option 1: Änderungen committen
git add . && git commit -m "Save changes"

# Option 2: Änderungen stashen
git stash
```

**"No matching scheme found"**:
```bash
# Erstelle passende Schema-Datei
./tagit.py -f myfile --scheme-file custom-schemas.json
```

**Debug-Modus aktivieren**:
```bash
./tagit.py -v -f problematic-file.txt
```

## Migration von älteren Versionen

Von Version 0.2.x zu 0.3.0:

1. **Keine Breaking Changes**: Die Grundfunktionalität bleibt erhalten
2. **Neue Features**: Nutze `--dry-run` für sicheres Testen
3. **Verbesserte Sicherheit**: Keine Anpassungen erforderlich
4. **Schema-Kompatibilität**: Bestehende `tagit-config.json` funktionieren weiterhin

## Entwicklung

Beiträge sind willkommen! Bitte beachte:

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Füge Tests für neue Features hinzu
4. Stelle sicher, dass der Code den Sicherheitsrichtlinien entspricht
5. Erstelle einen Pull Request

## Lizenz

Tagit ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## Autor

Erstellt von **Thilo Graf**

---

**Version 0.3.0** - Mit Fokus auf Sicherheit, Zuverlässigkeit und Benutzerfreundlichkeit.