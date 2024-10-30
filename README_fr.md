<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | <span style="color: grey;">🇫🇷 French</span> | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Balisage Git automatique et mise à jour de version

## Table des matières

- [Tagit - Balisage Git automatique et mise à jour de version](#tagit---balisage-git-automatique-et-mise-à-jour-de-version)
  - [Table des matières](#table-des-matières)
  - [Fonctionnalités](#caractéristiques)
  - [Exigences](#exigences)
    - [Utiliser un environnement virtuel (recommandé)](#utiliser-un-environnement-virtuel-recommandé)
    - [À l'échelle du système](#à-léchelle-du-système)
  - [Installation](#installation)
  - [Utilisation](#utiliser)
    - [Exemples](#exemples)
  - [Schémas de version pris en charge](#schémas-de-version-pris-en-charge)
  - [Schémas de gestion de versions personnalisés](#schémas-de-version-personnalisés)
    - [Exemple de fichier de configuration JSON](#exemple-de-fichier-de-configuration-json)
    - [Explication de chaque schéma](#explication-de-chaque-schéma)
      - [ac\_init](#ac_init)
      - [version\_assignment](#version_assignment)
      - [définir\_ver](#définir_ver)
      - [env\_version](#env_version)
      - [python\_setup](#python_setup)
      - [paquet\_json](#paquet-json)
      - [cpp\_header](#cpp_header)
      - [xml\_version](#version_xml)
      - [ini\_version](#ini_version)
      - [markdown\_badge](#markdown_badge)
      - [rubis\_gemspec](#rubis-gemmespec)
  - [Journalisation](#enregistrement)
  - [Licence](#licence)
  - [Auteur](#auteur)

`Tagit` est un script qui automatise le balisage des versions dans les référentiels Git et met à jour les numéros de version dans des fichiers de projet spécifiques. Le script permet une gestion automatique des schémas de version, ce qui facilite le maintien de numéros de version cohérents sur plusieurs fichiers de votre projet.

## Caractéristiques

- **Marquage Git automatique** : crée des balises Git pour vos commits afin de permettre un suivi facile des versions.
- **Mise à jour de version dans les fichiers de projet** : met à jour les numéros de version dans les fichiers spécifiés en fonction de schémas de version prédéfinis.
- **Schémas de version personnalisés** : prend en charge des schémas de version supplémentaires via un fichier de configuration `json` ​​​​​​.
- **Format de balise flexible** : définissez un format de balise personnalisé avec des espaces réservés pour les versions majeures, mineures et de correctifs.
- **Version initiale et mode version** : Permet de définir une version initiale et de choisir entre différentes méthodes de détermination des correctifs (nombre de commits ou incrémentation).

## Exigences

-Python3
-GitPython

Pour installer les dépendances, utilisez :

### Utiliser un environnement virtuel (recommandé)

```sh
python3 -m venv venv && source venv/bin/activate && pip install GitPython
```

### À l'échelle du système

```sh
pip install GitPython
```

## installation

Utilisez `curl` pour télécharger le script directement à l'emplacement de votre choix :

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/master/tagit.py
```

**ou**

Utilisez `git clone` pour cloner l'intégralité de la source vers un emplacement de votre choix :

```bash
git clone https://github.com/dbt1/tagit.git
```

Vous pouvez exécuter `Tagit` à partir d'un emplacement de votre choix, soit directement là où il se trouve après le clonage, soit dans le même répertoire où se trouve `Tagit`. Si `Tagit` doit être exécuté directement, le script doit être rendu exécutable en modifiant l'autorisation en fonction du système.

```bash
chmod +x dateiname.py
```

## utiliser

> **Remarque** : Si aucune balise n'a encore été attribuée dans le référentiel, une balise sera créée automatiquement.

Exécuter sans spécifier de fichiers pour marquer la dernière version :
```sh
python tagit.py
```

ou avec options :
```sh
python tagit.py [Optionen]
```

### Exemples

- Mettre à jour le balisage et les numéros de version dans plusieurs fichiers :
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Spécifiez des schémas de version supplémentaires avec un fichier de configuration `JSON` :
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```
- Spécifiez le format de balise personnalisé :
  ```sh
  python tagit.py --file configure.ac --tag-format release-{major}.{minor}.{patch}
  ```
- Définir la version initiale et incrémenter la version du correctif :
  ```sh
  python tagit.py --tag-format none --initial-version 1.0.0 --version-mode increment
  ```

## Schémas de version pris en charge

`Tagit` est livré avec des schémas de versioning prédéfinis, qui peuvent être étendus avec un fichier de configuration JSON si nécessaire :

- **ac_init** : recherche et met à jour la version dans les macros `AC_INIT()` utilisées dans les fichiers `configure.ac`.
- **version_assignment** : recherche les instructions d'affectation `VERSION = "X.X.X"`.
- **define_ver** : met à jour les macros de version comme `define(ver_major, X)`.
- **env_version** : met à jour les variables d'environnement comme `VERSION_MAJOR="X"`.

## Schémas de version personnalisés

Vous pouvez ajouter des schémas de version supplémentaires en spécifiant un fichier de configuration JSON avec l'option `--scheme-file`. Cela vous permet de définir des modèles personnalisés et des chaînes de remplacement pour les mises à jour de version dans n'importe quel fichier.

### Exemple de fichier de configuration JSON

Voici un exemple de fichier de configuration JSON qui définit des schémas de gestion de versions personnalisés :

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
        "_comment": "Updates version assignments in scripts or configuration files.",
        "patterns": {
            "version": "VERSION\\s*=\\s*\"\\d+\\.\\d+\\.\\d+\""
        },
        "replacements": {
            "version": "VERSION = \"{major}.{minor}.{micro}\""
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

### Explication de chaque schéma

#### ac_init
- **Objectif** : Met à jour la version dans les fichiers `configure.ac` à l'aide de la macro `AC_INIT`.
- **Exemple**:
  ```m4
  AC_INIT([MyProject], [0.1.0], [support@example.com])
  ```
- **Description** : recherche la macro `AC_INIT` et met à jour le numéro de version.

#### version_assignment
- **Objectif** : affectation générale de version dans les scripts ou les fichiers de configuration.
- **Exemple**:
  ```bash
  VERSION = "0.1.0"
  ```
- **Description** : Recherche les lignes contenant `VERSION = "..."` et remplace la version.

#### définir_ver
- **Objectif** : Définitions de versions dans des fichiers à l'aide de macros.
- **Exemple**:
  ```m4
  define(ver_major, 0)
  define(ver_minor, 1)
  define(ver_micro, 0)
  ```
- **Description** : remplace les versions majeures, mineures et les correctifs dans les macros.

#### env_version
- **Objectif** : définit les numéros de version pour les variables d'environnement.
- **Exemple**:
  ```bash
  VERSION_MAJOR="0"
  VERSION_MINOR="1"
  VERSION_PATCH="0"
  ```
- **Description** : Met à jour les variables d'environnement avec la nouvelle version.

#### python_setup
- **Objectif** : met à jour la version dans `setup.py` pour les packages Python.
- **Exemple**:
  ```python
  setup(
      name='mypackage',
      version="0.1.0",
      ...
  )
  ```
- **Description** : recherche la version dans `setup.py` et la remplace.

#### paquet json
- **Objectif** : met à jour la version dans `package.json` pour les projets Node.js.
- **Exemple**:
  ```json
  {
    "name": "myproject",
    "version": "0.1.0",
    ...
  }
  ```
- **Description** : recherche et met à jour le champ de version dans `package.json`.

#### cpp_header
- **Objectif** : met à jour les numéros de version dans les fichiers d'en-tête C/C++.
- **Exemple**:
  ```cpp
  #define VERSION_MAJOR 0
  #define VERSION_MINOR 1
  #define VERSION_PATCH 0
  ```
- **Description** : remplace les numéros de version dans les directives `#define`.

#### version_xml
- **Objectif** : Met à jour les numéros de version dans les fichiers XML.
- **Exemple**:
  ```xml
  <version>0.1.0</version>
  ```
- **Description** : recherche la balise `<version>` et met à jour le numéro de version.

#### ini_version
- **Objectif** : Met à jour les numéros de version dans les fichiers INI.
- **Exemple**:
  ```ini
  version=0.1.0
  ```
- **Description** : recherche le paramètre de version et le remplace.

#### markdown_badge
- **Objectif** : Met à jour les badges de version dans les fichiers `README.md`.
- **Exemple**:
  ```markdown
  [![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/username/repository)
  ```
- **Description** : Remplace le numéro de version dans le lien du badge.

#### rubis gemmespec
- **Objectif** : met à jour le numéro de version dans les fichiers `.gemspec` pour Ruby.
- **Exemple**:
  ```ruby
  Gem::Specification.new do |spec|
    spec.name        = 'mygem'
    spec.version     = "0.1.0"
    ...
  end
  ```
- **Description** : recherche `.version` dans les fichiers `.gemspec` et les met à jour.

## Enregistrement

`Tagit` fournit une journalisation détaillée de chaque action entreprise. Les entrées du journal incluent :

- Mises à jour de versions dans les fichiers
- Actions de marquage Git
- Avertissements et erreurs en cas de problèmes

## Licence

`Tagit` est sous licence MIT.

## auteur

Créé par Thilo Graf.
