# Snapshot: PRE Instalador (PyInstaller/Inno Setup)

Este snapshot contiene el estado del proyecto ANTES de convertirlo en una app instalable de escritorio.

Archivo principal del snapshot:

- `PythonWebScraper_PRE_Installer.zip`: comprimido con todo el árbol del repositorio en ese momento.

Cómo restaurar este estado:

1. Haz una copia de seguridad de tu carpeta actual si tienes cambios recientes.
2. Descomprime `PythonWebScraper_PRE_Installer.zip` directamente sobre la raíz del repositorio (o en una carpeta separada si quieres comparar primero).
3. Verifica que los scripts y la GUI funcionen como antes de la preparación del instalador.

Qué se agregó/modificó DESPUÉS de este snapshot para convertirlo en app instalable (ahora revertido):

- Archivos que se añadieron originalmente para la instalación pero que se han eliminado tras revertir la operación:
  - `launch_gui.py` (punto de entrada para PyInstaller) — ELIMINADO
  - `scripts/build_windows_app.ps1` — ELIMINADO
  - `scripts/create_desktop_shortcut.ps1` — ELIMINADO
  - `installer/WebScraperPRO.iss` — ELIMINADO
  - `docs/INSTALL_WINDOWS.md` — ELIMINADO

- Archivo que fue modificado y ya fue revertido:
  - `src/gui/app.py` — RESTAURADO a su versión previa (carga de estilos en modo desarrollo)

Notas:

- Si solo deseas revertir la “instalabilización”, elimina los archivos mencionados en “Agregados” y revierte los cambios de `src/gui/app.py` a su versión previa (incluida en el zip).
- Si usas control de versiones (git), también puedes comparar y hacer rollback a los commits previos.
