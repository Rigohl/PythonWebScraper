#!/bin/bash
# Este script lanza la aplicación Web Scraper PRO en macOS y Linux.

# Detener el script si un comando falla
set -e

VENV_DIR="./.venv"

echo "[INFO] Verificando si el entorno virtual existe..."
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[ERROR] El entorno virtual no se encuentra en '$VENV_DIR'."
    echo "[ERROR] Por favor, ejecuta primero el script '1-install-dependencies.sh'."
    exit 1
fi

echo "[INFO] Lanzando la interfaz de usuario (TUI)..."
"$VENV_DIR/bin/python" src/main.py --tui
