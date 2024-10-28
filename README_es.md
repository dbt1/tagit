<!-- LANGUAGE_LINKS_START -->
[🇩🇪 German](README_de.md) | [🇬🇧 English](README_en.md) | <span style="color: grey;">🇪🇸 Spanish</span> | [🇫🇷 French](README_fr.md) | [🇮🇹 Italian](README_it.md)
<!-- LANGUAGE_LINKS_END -->

# Tagit: etiquetado automático de Git y actualización de versiones

## Tabla de contenido

- [Tagit - Etiquetado automático de Git y actualización de versión](#tagit-etiquetado-automático-de-git-y-actualización-de-versiones)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Características](#características)
  - [Requisitos](#requisitos)
  - [Instalación](#instalación)
  - [Uso](#usar)
    - [Ejemplos](#ejemplos)
  - [Esquemas de versiones compatibles](#esquemas-de-versiones-soportados)
    - [Esquemas de versiones personalizados](#esquemas-de-versiones-personalizados)
  - [Registro](#explotación-florestal)

`Tagit` es un script que automatiza el etiquetado de versiones en repositorios Git y actualiza los números de versión en archivos de proyectos específicos. El script proporciona administración automática de esquemas de versiones, lo que facilita mantener números de versión consistentes en varios archivos de su proyecto.

## Características

- **Etiquetado Git automático**: crea etiquetas Git para sus confirmaciones para permitir un seguimiento sencillo de la versión.
- **Actualización de versión en archivos de proyecto**: actualiza los números de versión en archivos específicos según esquemas de control de versiones predefinidos.
- **Esquemas de versiones personalizados**: admite esquemas de versiones adicionales a través de un archivo de configuración `json`.

## Requisitos

- Pitón 3
-GitPython

Para instalar las dependencias utilice:

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

> **Nota**: Si aún no se ha asignado ninguna etiqueta en el repositorio, se creará una etiqueta automáticamente.

Ejecute sin especificar archivos para etiquetar la última versión:
  ```sh
  python tagit.py
  ```

o con opciones

  ```sh
  python tagit.py [Options]
  ```

### Ejemplos

- Actualizar etiquetas y números de versión en varios archivos:
  ```sh
  python tagit.py -f configure.ac -f version.txt
  ```
- Especifique esquemas de versiones adicionales con un archivo de configuración `JSON`:
  ```sh
  python tagit.py --file configure.ac --file version.txt --scheme-file custom_schemes.json
  ```

## Esquemas de versiones soportados

`Tagit` viene con esquemas de versiones predefinidos, que se pueden ampliar con un archivo de configuración JSON si es necesario:

- **ac_init**: busca y actualiza la versión en las macros `AC_INIT()` utilizadas en los archivos `configure.ac`.
- **version_assignment**: busca instrucciones de asignación `VERSION = "X.X.X"`.
- **define_ver**: Actualiza macros de versión como `define(ver_major, X)`.
- **env_version**: Actualiza variables de entorno como `VERSION_MAJOR="X"`.

### Esquemas de versiones personalizados

Puede agregar esquemas de control de versiones adicionales especificando un archivo de configuración JSON con la opción `--scheme-file`. Esto le permite definir patrones personalizados y cadenas de reemplazo para actualizaciones de versión en cualquier archivo.

## Explotación florestal

`Tagit` proporciona un registro detallado de cada acción realizada. Las entradas de registro incluyen:

- Actualizaciones de versiones en archivos.
- Acciones de etiquetado de Git
- Advertencias y errores si ocurren problemas.
