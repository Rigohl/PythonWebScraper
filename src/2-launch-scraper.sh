#!/bin/bash
# Activa el entorno virtual y lanza la aplicación en modo TUI.
echo "[INFO] Activando entorno virtual y lanzando la TUI..."
source .venv/bin/activate
python3 src/main.py --tui
