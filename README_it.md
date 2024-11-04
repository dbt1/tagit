<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | <span style="color: grey;">🇮🇹 Italian</span>
<!-- LANGUAGE_LINKS_END -->

# Tagit: tagging Git automatico e aggiornamento della versione

Versione: 0.2.8

## Sommario

- [Tagit - Tagging Git automatico e aggiornamento della versione](#tagit-tagging-git-automatico-e-aggiornamento-della-versione)
  - [Sommario](#sommario)
  - [Funzioni](#caratteristiche)
  - [Requisiti](#requisiti)
    - [Utilizza l'ambiente virtuale (consigliato)](#utilizza-lambiente-virtuale-consigliato)
    - [A livello di sistema](#a-livello-di-sistema)
  - [Installazione](#installazione)
  - [Utilizzo](#utilizzo)
    - [Esempi](#esempi)
    - [Integrazione Git Hook](#integrazione-dellhook-git)
  - [Schemi di controllo delle versioni supportati](#schemi-di-controllo-delle-versioni-supportati)
  - [Schemi di controllo delle versioni personalizzati](#schemi-di-versione-personalizzati)
    - [Esempio di file di configurazione JSON](#file-di-configurazione-json-di-esempio)
    - [Spiegazione di ogni schema](#spiegazione-di-ogni-schema)
      - [ac\_init](#ac_init)
      - [versione\_assegnazione](#assegnazione_versione)
      - [versione\_colon\_formato](#versione_colon_format)
      - [definisci\_ver](#define_ver)
      - [env\_versione](#env_version)
      - [python\_setup](#python_setup)
      - [pacchetto\_json](#pacchetto-json)
      - [cpp\_header](#cpp_header)
      - [xml\_versione](#xml_versione)
      - [ini\_versione](#ini_version)
      - [ribasso\_badge](#markdown_badge)
      - [rubino\_gemspec](#rubino-gemspec)
  - [Registrazione](#registrazione)
  - [Licenza](#licenza)
  - [Autore](#autore)

`Tagit` è uno script che automatizza il tagging della versione nei repository Git e aggiorna i numeri di versione in file di progetto specifici. Lo script fornisce la gestione automatica degli schemi di controllo delle versioni, semplificando il mantenimento di numeri di versione coerenti su più file nel progetto.

## Caratteristiche

- **Tagging Git automatico**: genera tag Git in base a diversi metodi di determinazione delle patch (numero di commit o incremento).
- **Aggiornamento versione nei file di progetto**: aggiorna i numeri di versione nei file specificati in base a schemi di controllo delle versioni predefiniti. Supporta vari formati di versione (ad esempio AC_INIT, VERSION = "X.X.X", define(ver_major, X))
- **Schemi di controllo delle versioni personalizzati**: supporta schemi di controllo delle versioni aggiuntivi tramite un file di configurazione dello schema `json`.
- **Formato tag flessibile**: consente di definire formati di tag con caratteri jolly personalizzati per le versioni principali, secondarie e patch tramite formati con caratteri jolly personalizzabili come {AAAA}, {MM}, {DD}, {major}, {minor}, e {patch}, anche per data e ora: utilizzare {AAAA}, {MM}, {GG}, {hh}, {mm}, {ss} per integrare automaticamente la data e l'ora correnti.
- **Versione iniziale e modalità versione**: consente di impostare una versione iniziale.

## Requisiti

- Pitone 3
-GitPython

Per installare le dipendenze utilizzare:

### Utilizza l'ambiente virtuale (consigliato)

```sh
python3 -m venv venv && source venv/bin/activate && pip install GitPython
```

### A livello di sistema

```sh
pip install GitPython
```

## installazione

Utilizza `curl` per scaricare lo script direttamente in una posizione a tua scelta:

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/master/tagit.py
```

**O**

Utilizza `git clone` per clonare l'intera fonte in una posizione a tua scelta:

```bash
git clone https://github.com/dbt1/tagit.git
```

Puoi eseguire `Tagit` da una posizione a tua scelta, direttamente dove si trova dopo la clonazione o nella stessa directory in cui si trova `Tagit`. Se `Tagit` deve essere eseguito direttamente, lo script deve essere reso eseguibile modificando i permessi a seconda del sistema.

```bash
chmod +x dateiname.py
```

## utilizzo

Se nel repository non è stato ancora assegnato alcun tag, verrà creato automaticamente un tag. Puoi anche impostare tu stesso il tag iniziale.

```sh
python tagit.py --initial-version 1.0.0
```

Esegui senza specificare i file per taggare l'ultima versione:
```sh
python tagit.py
```

o con opzioni:
```sh
python tagit.py [Optionen]
```

### Esempi

- Aggiorna tag e numeri di versione in più file:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Schemi di controllo delle versioni aggiuntivi con un file di configurazione dello schema `JSON`:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```
- Tagging con schemi di controllo delle versioni da un file di configurazione dello schema `JSON`
  ```sh
  python tagit.py --scheme-file custom_schemes.json --tag-format '{major}.{minor}.{patch}'
  ```
- Formato tag personalizzato:
  ```sh
  python tagit.py --file configure.ac --tag-format release-{major}.{minor}.{patch}
  ```
- Imposta la versione iniziale e incrementa la versione della patch:
  ```sh
  python tagit.py --tag-format none --initial-version 1.0.0 --version-mode increment
  ```
- Tagging con segnaposto anno e mese
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}'
  ```
- Etichettatura con data e ora
  ```sh
  python tagit.py --tag-format 'v{major}.{minor}.{patch}-{YY}{MM}{DD}-{hh}{mm}{ss}'
  ```
- Etichettatura con anno, mese
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}' -f configure.ac
  ```
- Aggiorna i file senza creare un tag:

  ```sh
  python tagit.py -f configure.ac --no-tag
  ```
### Integrazione dell'hook Git

Puoi integrare `Tagit` nel tuo flusso di lavoro Git utilizzandolo come hook pre-push. Ciò garantisce che i numeri di versione e i tag vengano aggiornati automaticamente prima di inviare modifiche al repository remoto.

Ecco una guida per utilizzare lo script come hook pre-push:

1. Crea la cartella hook Git se non esiste:

   ```sh
   mkdir -p .git/hooks
   ```

2. Crea un file denominato `pre-push` nella directory `.git/hooks/` e rendilo eseguibile:

   ```sh
   touch .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

3. Modifica il file `.git/hooks/pre-push` e aggiungi il seguente contenuto:

   ```sh
   #!/bin/sh
   # Pre-Push Hook to run Tagit before pushing
   
   python3 path/to/tagit.py -f configure.ac -f version.txt || {
       echo "Tagit failed. Push aborted."
       exit 1
   }
   ```

   Sostituisci `path/to/tagit.py` con il percorso effettivo dello script Tagit e `configure.ac`, `version.txt` con i file che desideri aggiornare.

4. Salva le modifiche e chiudi il file.

Ora ogni volta che provi a inviare modifiche, verrà eseguito lo script Tagit. Se Tagit fallisce, il push verrà annullato in modo da poter garantire che le versioni rimangano coerenti.


## Schemi di controllo delle versioni supportati

`Tagit` viene fornito con schemi di versione predefiniti, che possono essere estesi con un file di configurazione JSON, se necessario:

- **ac_init**: trova e aggiorna la versione nelle macro `AC_INIT()` utilizzate nei file `configure.ac`.
- **version_assignment**: trova le istruzioni di assegnazione `VERSION = "X.X.X"`.
- **define_ver**: aggiorna le macro della versione come `define(ver_major, X)`.
- **env_version**: aggiorna le variabili di ambiente come `VERSION_MAJOR="X"`.

## Schemi di versione personalizzati

Puoi aggiungere ulteriori schemi di controllo delle versioni specificando un file di configurazione JSON con l'opzione `--scheme-file`. Ciò consente di definire modelli personalizzati e stringhe sostitutive per gli aggiornamenti di versione in qualsiasi file.

### File di configurazione JSON di esempio

Ecco un esempio di file di configurazione JSON che definisce schemi di controllo delle versioni personalizzati:

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

### Spiegazione di ogni schema

#### ac_init
- **Scopo**: aggiorna la versione nei file `configure.ac` utilizzando la macro `AC_INIT`.
- **Esempio**:
  ```m4
  AC_INIT([MyProject], [0.2.9], [support@example.com])
  ```
- **Descrizione**: cerca la macro `AC_INIT` e aggiorna il numero di versione.

#### assegnazione_versione
- **Scopo**: assegnazione generale del controllo delle versioni negli script o nei file di configurazione.
- **Esempio**:
  ```bash
  VERSION = "0.1.0"
  ```
- **Descrizione**: cerca le righe contenenti `VERSION = "..."` e sostituisce la versione.

#### versione_colon_format

- **Scopo**: aggiorna i numeri di versione nei file con versione: formato X.X.X.
- **Esempio**:
  ```txt
  Version: 0.0.0
  ``` 
**Descrizione**: Cerca le righe che iniziano con versione: e contengono un numero di versione e le aggiorna.

#### define_ver
- **Scopo**: definizioni di versione nei file che utilizzano macro.
- **Esempio**:
  ```m4
  define(ver_major, 0)
  define(ver_minor, 1)
  define(ver_micro, 0)
  ```
- **Descrizione**: Sostituisce le versioni principali, secondarie e patch nelle macro.

#### env_version
- **Scopo**: imposta i numeri di versione per le variabili di ambiente.
- **Esempio**:
  ```bash
  VERSION_MAJOR="0"
  VERSION_MINOR="1"
  VERSION_PATCH="0"
  ```
- **Descrizione**: Aggiorna le variabili d'ambiente con la nuova versione.

#### python_setup
- **Scopo**: aggiorna la versione in `setup.py` per i pacchetti Python.
- **Esempio**:
  ```python
  setup(
      name='mypackage',
      version="0.1.0",
      ...
  )
  ```
- **Descrizione**: cerca la versione in `setup.py` e la sostituisce.

#### pacchetto json
- **Scopo**: aggiorna la versione in `package.json` per i progetti Node.js.
- **Esempio**:
  ```json
  {
    "name": "myproject",
    "version": "0.1.0",
    ...
  }
  ```
- **Descrizione**: cerca e aggiorna il campo della versione in `package.json`.

#### cpp_header
- **Scopo**: aggiorna i numeri di versione nei file di intestazione C/C++.
- **Esempio**:
  ```cpp
  #define VERSION_MAJOR 0
  #define VERSION_MINOR 1
  #define VERSION_PATCH 0
  ```
- **Descrizione**: sostituisce i numeri di versione nelle direttive `#define`.

#### xml_versione
- **Scopo**: aggiorna i numeri di versione nei file XML.
- **Esempio**:
  ```xml
  <version>0.1.0</version>
  ```
- **Descrizione**: Trova il tag `<version>` e aggiorna il numero di versione.

#### ini_version
- **Scopo**: aggiorna i numeri di versione nei file INI.
- **Esempio**:
  ```ini
  version=0.1.0
  ```
- **Descrizione**: Trova l'impostazione della versione e la sostituisce.

#### markdown_badge
- **Scopo**: aggiorna i badge della versione nei file `README.md`.
- **Esempio**:
  ```markdown
  [![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/username/repository)
  ```
- **Descrizione**: Sostituisce il numero di versione nel collegamento del badge.

#### rubino gemspec
- **Scopo**: aggiorna il numero di versione nei file `.gemspec` per Ruby.
- **Esempio**:
  ```ruby
  Gem::Specification.new do |spec|
    spec.name        = 'mygem'
    spec.version     = "0.1.0"
    ...
  end
  ```
- **Descrizione**: cerca `.version` nei file `.gemspec` e li aggiorna.

## Registrazione

`Tagit` fornisce una registrazione dettagliata per ogni azione eseguita. Le voci del registro includono:

- Aggiornamenti della versione nei file
- Azioni di tagging di Git
- Avvisi ed errori in caso di problemi

## Licenza

`Tagit` è concesso in licenza con la licenza MIT.

## autore

Creato da Thilo Graf.
