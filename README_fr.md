<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | [🇪🇸 Spanish](README_es.md) | <span style="color: grey;">🇫🇷 French</span> | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit - Balisage Git automatique et mise à jour de version

## Table des matières

- [Tagit - Balisage Git automatique et mise à jour de version](#tagit---balisage-git-automatique-et-mise-à-jour-de-version)
  - [Table des matières](#table-des-matières)
  - [Fonctionnalités](#caractéristiques)
  - [Exigences](#exigences)
  - [Installation](#installation)
  - [Utilisation](#utiliser)
    - [Exemples](#exemples)
  - [Schémas de version pris en charge](#schémas-de-version-pris-en-charge)
    - [Schémas de version personnalisés](#schémas-de-version-personnalisés)
  - [Journalisation](#enregistrement)

`Tagit` est un script qui automatise le balisage des versions dans les référentiels Git et met à jour les numéros de version dans des fichiers de projet spécifiques. Le script permet une gestion automatique des schémas de version, ce qui facilite le maintien de numéros de version cohérents sur plusieurs fichiers de votre projet.

## Caractéristiques

- **Marquage Git automatique** : crée des balises Git pour vos commits afin de permettre un suivi facile des versions.
- **Mise à jour de version dans les fichiers de projet** : met à jour les numéros de version dans les fichiers spécifiés en fonction de schémas de version prédéfinis.
- **Schémas de version personnalisés** : prend en charge des schémas de version supplémentaires via un fichier de configuration `json` ​​​​​​.

## Exigences

-Python3
-GitPython

Pour installer les dépendances, utilisez :

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

ou avec options

  ```sh
  python tagit.py [Options]
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

## Schémas de version pris en charge

`Tagit` est livré avec des schémas de versioning prédéfinis, qui peuvent être étendus avec un fichier de configuration JSON si nécessaire :

- **ac_init** : recherche et met à jour la version dans les macros `AC_INIT()` utilisées dans les fichiers `configure.ac`.
- **version_assignment** : recherche les instructions d'affectation `VERSION = "X.X.X"`.
- **define_ver** : met à jour les macros de version comme `define(ver_major, X)`.
- **env_version** : met à jour les variables d'environnement comme `VERSION_MAJOR="X"`.

### Schémas de version personnalisés

Vous pouvez ajouter des schémas de version supplémentaires en spécifiant un fichier de configuration JSON avec l'option `--scheme-file`. Cela vous permet de définir des modèles personnalisés et des chaînes de remplacement pour les mises à jour de version dans n'importe quel fichier.

## Enregistrement

`Tagit` fournit une journalisation détaillée de chaque action entreprise. Les entrées du journal incluent :

- Mises à jour de versions dans les fichiers
- Actions de marquage Git
- Avertissements et erreurs en cas de problèmes
