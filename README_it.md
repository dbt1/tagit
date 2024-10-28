<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | [🇫🇷 French](README_fr.md) | <span style="color: grey;">🇮🇹 Italian</span>
<!-- LANGUAGE_LINKS_END -->

# Tagit: tagging Git automatico e aggiornamento della versione

## Sommario

- [Tagit - Tagging Git automatico e aggiornamento della versione](#tagit-tagging-git-automatico-e-aggiornamento-della-versione)
  - [Sommario](#sommario)
  - [Funzioni](#caratteristiche)
  - [Requisiti](#requisiti)
  - [Installazione](#installazione)
  - [Utilizzo](#utilizzo)
    - [Esempi](#esempi)
  - [Schemi di controllo delle versioni supportati](#schemi-di-controllo-delle-versioni-supportati)
    - [Schemi di controllo delle versioni personalizzati](#schemi-di-versione-personalizzati)
  - [Registrazione](#registrazione)

`Tagit` è uno script che automatizza il tagging della versione nei repository Git e aggiorna i numeri di versione in file di progetto specifici. Lo script fornisce la gestione automatica degli schemi di controllo delle versioni, semplificando il mantenimento di numeri di versione coerenti su più file nel progetto.

## Caratteristiche

- **Tagging Git automatico**: crea tag Git per i tuoi commit per consentire un facile monitoraggio della versione.
- **Aggiornamento versione nei file di progetto**: aggiorna i numeri di versione nei file specificati in base a schemi di controllo delle versioni predefiniti.
- **Schemi di controllo delle versioni personalizzati**: supporta schemi di controllo delle versioni aggiuntivi tramite un file di configurazione `json` ​​​​.

## Requisiti

- Pitone 3
-GitPython

Per installare le dipendenze utilizzare:

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

> **Nota**: se nel repository non è stato ancora assegnato alcun tag, verrà creato automaticamente un tag.

Esegui senza specificare i file per taggare l'ultima versione:
  ```sh
  python tagit.py
  ```

o con opzioni

  ```sh
  python tagit.py [Options]
  ```

### Esempi

- Aggiorna tag e numeri di versione in più file:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Specifica schemi di versione aggiuntivi con un file di configurazione `JSON`:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```

## Schemi di controllo delle versioni supportati

`Tagit` viene fornito con schemi di versione predefiniti, che possono essere estesi con un file di configurazione JSON, se necessario:

- **ac_init**: trova e aggiorna la versione nelle macro `AC_INIT()` utilizzate nei file `configure.ac`.
- **version_assignment**: trova le istruzioni di assegnazione `VERSION = "X.X.X"`.
- **define_ver**: aggiorna le macro della versione come `define(ver_major, X)`.
- **env_version**: aggiorna le variabili di ambiente come `VERSION_MAJOR="X"`.

### Schemi di versione personalizzati

Puoi aggiungere ulteriori schemi di controllo delle versioni specificando un file di configurazione JSON con l'opzione `--scheme-file`. Ciò consente di definire modelli personalizzati e stringhe sostitutive per gli aggiornamenti di versione in qualsiasi file.

## Registrazione

`Tagit` fornisce una registrazione dettagliata per ogni azione intrapresa. Le voci di registro includono:

- Aggiornamenti della versione nei file
- Azioni di tagging di Git
- Avvisi ed errori in caso di problemi
