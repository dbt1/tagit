<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | <span style="color: grey;">🇪🇸 Spanish</span> | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit: etiquetado automático de Git y actualización de versiones

Versión: 0.2.8

## Tabla de contenido

- [Tagit - Etiquetado automático de Git y actualización de versión](#tagit-etiquetado-automático-de-git-y-actualización-de-versiones)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Características](#características)
  - [Requisitos](#requisitos)
    - [Usar entorno virtual (recomendado)](#usar-entorno-virtual-recomendado)
    - [En todo el sistema](#todo-el-sistema)
  - [Instalación](#instalación)
  - [Uso](#usar)
    - [Ejemplos](#ejemplos)
    - [Integración de Git Hook](#integración-de-gancho-git)
  - [Esquemas de versiones soportados](#esquemas-de-versiones-soportados)
  - [Esquemas de versiones personalizados](#esquemas-de-versiones-personalizados)
    - [Ejemplo de archivo de configuración JSON](#ejemplo-de-archivo-de-configuración-json)
    - [Explicación de cada esquema](#explicación-de-cada-esquema)
      - [ac\_init](#ac_init)
      - [versión\_asignación](#asignación_versión)
      - [versión\_dos puntos\_formato](#versión_dos-puntos_formato)
      - [definir\_ver](#definir_ver)
      - [entorno\_versión](#versión_env)
      - [python\_setup](#configuración_python)
      - [paquete\_json](#paquete-json)
      - [cpp\_encabezado](#encabezado_cpp)
      - [xml\_versión](#versión_xml)
      - [ini\_version](#versión_ini)
      - [rebaja\_badge](#insignia_de_rebaja)
      - [rubí\_gemspec](#rubí-gemspec)
  - [Registro](#explotación-florestal)
  - [Licencia](#licencia)
  - [Autor](#autor)

`Tagit` es un script que automatiza el etiquetado de versiones en repositorios Git y actualiza los números de versión en archivos de proyectos específicos. El script proporciona administración automática de esquemas de versiones, lo que facilita mantener números de versión consistentes en varios archivos de su proyecto.

## Características

- **Etiquetado Git automático**: Genera etiquetas Git basadas en diferentes métodos de determinación de parches (número de confirmaciones o incrementos).
- **Actualización de versión en archivos de proyecto**: actualiza los números de versión en archivos específicos según esquemas de control de versiones predefinidos. Admite varios formatos de versiones (por ejemplo, AC_INIT, VERSION = "X.X.X", define(ver_major, X))
- **Esquemas de control de versiones personalizados**: admite esquemas de control de versiones adicionales a través de un archivo de configuración de esquema `json`.
- **Formato de etiqueta flexible**: le permite definir formatos de etiquetas comodín personalizados para versiones principales, secundarias y de parche a través de formatos comodín personalizables como {AAAA}, {MM}, {DD}, {principal}, {menor}, y {patch}, también para fecha y hora: Utilice {AAAA}, {MM}, {DD}, {hh}, {mm}, {ss} para integrar automáticamente la fecha y hora actuales.
- **Versión inicial y modo de versión**: Le permite configurar una versión inicial.

## Requisitos

- Pitón 3
-GitPython

Para instalar las dependencias utilice:

### Usar entorno virtual (recomendado)

```sh
python3 -m venv venv && source venv/bin/activate && pip install GitPython
```

### Todo el sistema

```sh
pip install GitPython
```

## instalación

Utilice `curl` para descargar el script directamente a la ubicación que elija:

```bash
curl -o tagit.py https://raw.githubusercontent.com/dbt1/tagit/master/tagit.py
```

**o**

Utilice `git clone` para clonar toda la fuente en la ubicación que elija:

```bash
git clone https://github.com/dbt1/tagit.git
```

Puede ejecutar `Tagit` desde la ubicación que elija, ya sea directamente donde está después de la clonación o en el mismo directorio donde se encuentra `Tagit`. Si `Tagit` se va a ejecutar directamente, el script debe hacerse ejecutable cambiando el permiso según el sistema.

```bash
chmod +x dateiname.py
```

## usar

Si aún no se ha asignado ninguna etiqueta en el repositorio, se creará una etiqueta automáticamente. También puedes configurar la etiqueta inicial tú mismo.

```sh
python tagit.py --initial-version 1.0.0
```

Ejecute sin especificar archivos para etiquetar la última versión:
```sh
python tagit.py
```

o con opciones:
```sh
python tagit.py [Optionen]
```

### Ejemplos

- Actualizar etiquetas y números de versión en varios archivos:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Esquemas de versiones adicionales con un archivo de configuración de esquema `JSON`:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```
- Etiquetado con esquemas de versiones desde un archivo de configuración de esquema `JSON`
  ```sh
  python tagit.py --scheme-file custom_schemes.json --tag-format '{major}.{minor}.{patch}'
  ```
- Formato de etiqueta personalizado:
  ```sh
  python tagit.py --file configure.ac --tag-format release-{major}.{minor}.{patch}
  ```
- Establecer la versión inicial e incrementar la versión del parche:
  ```sh
  python tagit.py --tag-format none --initial-version 1.0.0 --version-mode increment
  ```
- Etiquetado con marcadores de posición de año y mes
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}'
  ```
- Etiquetado con fecha y hora.
  ```sh
  python tagit.py --tag-format 'v{major}.{minor}.{patch}-{YY}{MM}{DD}-{hh}{mm}{ss}'
  ```
- Etiquetado con año, mes.
  ```sh
  python tagit.py --tag-format '{YYYY}.{MM}.{patch}' -f configure.ac
  ```
- Actualizar archivos sin crear una etiqueta:

  ```sh
  python tagit.py -f configure.ac --no-tag
  ```
### Integración de gancho Git

Puedes integrar `Tagit` en tu flujo de trabajo de Git usándolo como un enlace previo al envío. Esto garantiza que los números de versión y las etiquetas se actualicen automáticamente antes de enviar cambios al repositorio remoto.

Aquí hay una guía para usar el script como gancho previo al envío:

1. Cree la carpeta de enlace de Git si no existe:

   ```sh
   mkdir -p .git/hooks
   ```

2. Cree un archivo llamado `pre-push` en el directorio `.git/hooks/` y hágalo ejecutable:

   ```sh
   touch .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

3. Edite el archivo `.git/hooks/pre-push` y agregue el siguiente contenido:

   ```sh
   #!/bin/sh
   # Pre-Push Hook to run Tagit before pushing
   
   python3 path/to/tagit.py -f configure.ac -f version.txt || {
       echo "Tagit failed. Push aborted."
       exit 1
   }
   ```

   Reemplace `path/to/tagit.py` con la ruta real a su script Tagit y `configure.ac`, `version.txt` con los archivos que desea actualizar.

4. Guarde los cambios y cierre el archivo.

Ahora, cada vez que intente realizar cambios, se ejecutará el script Tagit. Si Tagit falla, el envío se cancelará para que pueda garantizar que las versiones sigan siendo consistentes.


## Esquemas de versiones soportados

`Tagit` viene con esquemas de control de versiones predefinidos, que se pueden ampliar con un archivo de configuración JSON si es necesario:

- **ac_init**: busca y actualiza la versión en las macros `AC_INIT()` utilizadas en los archivos `configure.ac`.
- **version_assignment**: busca instrucciones de asignación `VERSION = "X.X.X"`.
- **define_ver**: Actualiza macros de versión como `define(ver_major, X)`.
- **env_version**: Actualiza variables de entorno como `VERSION_MAJOR="X"`.

## Esquemas de versiones personalizados

Puede agregar esquemas de control de versiones adicionales especificando un archivo de configuración JSON con la opción `--scheme-file`. Esto le permite definir patrones personalizados y cadenas de reemplazo para actualizaciones de versión en cualquier archivo.

### Ejemplo de archivo de configuración JSON

A continuación se muestra un archivo de configuración JSON de ejemplo que define esquemas de control de versiones personalizados:

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

### Explicación de cada esquema.

#### ac_init
- **Propósito**: Actualiza la versión en archivos `configure.ac` usando la macro `AC_INIT`.
- **Ejemplo**:
  ```m4
  AC_INIT([MyProject], [0.2.9], [support@example.com])
  ```
- **Descripción**: busca la macro `AC_INIT` y actualiza el número de versión.

#### asignación_versión
- **Propósito**: Asignación de versionado general en scripts o archivos de configuración.
- **Ejemplo**:
  ```bash
  VERSION = "0.1.0"
  ```
- **Descripción**: busca líneas que contengan `VERSION = "..."` y reemplaza la versión.

#### versión_dos puntos_formato

- **Propósito**: Actualiza los números de versión en archivos con versión: formato X.X.X.
- **Ejemplo**:
  ```txt
  Version: 0.0.0
  ``` 
**Descripción**: busca líneas que comienzan con versión: y contienen un número de versión y las actualiza.

#### definir_ver
- **Propósito**: Definiciones de versiones en archivos usando macros.
- **Ejemplo**:
  ```m4
  define(ver_major, 0)
  define(ver_minor, 1)
  define(ver_micro, 0)
  ```
- **Descripción**: Reemplaza las versiones principales, secundarias y de parche en macros.

#### versión_env
- **Propósito**: Establece números de versión para variables de entorno.
- **Ejemplo**:
  ```bash
  VERSION_MAJOR="0"
  VERSION_MINOR="1"
  VERSION_PATCH="0"
  ```
- **Descripción**: Actualiza las variables de entorno con la nueva versión.

#### configuración_python
- **Propósito**: Actualiza la versión en `setup.py` para paquetes de Python.
- **Ejemplo**:
  ```python
  setup(
      name='mypackage',
      version="0.1.0",
      ...
  )
  ```
- **Descripción**: Busca la versión en `setup.py` y la reemplaza.

#### paquete json
- **Propósito**: Actualiza la versión en `package.json` para proyectos Node.js.
- **Ejemplo**:
  ```json
  {
    "name": "myproject",
    "version": "0.1.0",
    ...
  }
  ```
- **Descripción**: busca y actualiza el campo de versión en `package.json`.

#### encabezado_cpp
- **Propósito**: Actualiza los números de versión en archivos de encabezado C/C++.
- **Ejemplo**:
  ```cpp
  #define VERSION_MAJOR 0
  #define VERSION_MINOR 1
  #define VERSION_PATCH 0
  ```
- **Descripción**: Reemplaza los números de versión en las directivas `#define`.

#### versión_xml
- **Propósito**: Actualiza los números de versión en archivos XML.
- **Ejemplo**:
  ```xml
  <version>0.1.0</version>
  ```
- **Descripción**: busca la etiqueta `<version>` y actualiza el número de versión.

#### versión_ini
- **Propósito**: Actualiza los números de versión en archivos INI.
- **Ejemplo**:
  ```ini
  version=0.1.0
  ```
- **Descripción**: busca la configuración de versión y la reemplaza.

#### insignia_de_rebaja
- **Propósito**: Actualiza las insignias de versión en archivos `README.md`.
- **Ejemplo**:
  ```markdown
  [![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/username/repository)
  ```
- **Descripción**: Reemplaza el número de versión en el enlace de la insignia.

#### rubí gemspec
- **Propósito**: Actualiza el número de versión en los archivos `.gemspec` para Ruby.
- **Ejemplo**:
  ```ruby
  Gem::Specification.new do |spec|
    spec.name        = 'mygem'
    spec.version     = "0.1.0"
    ...
  end
  ```
- **Descripción**: Busca `.version` en archivos `.gemspec` y los actualiza.

## Explotación florestal

`Tagit` proporciona un registro detallado de cada acción realizada. Las entradas de registro incluyen:

- Actualizaciones de versiones en archivos.
- Acciones de etiquetado de Git
- Advertencias y errores si ocurren problemas.

## Licencia

`Tagit` tiene la licencia MIT.

## autor

Creado por Thilo Graf.
