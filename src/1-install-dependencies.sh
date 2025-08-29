#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

VENV_DIR=".venv"

echo "[INFO] Eliminando entorno virtual antiguo (si existe) para una instalación limpia..."
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
fi

echo "[INFO] Creando nuevo entorno virtual en $VENV_DIR..."
python3 -m venv --upgrade-deps "$VENV_DIR"

echo "[INFO] Instalando/actualizando dependencias de Python..."
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "[INFO] Instalando navegadores para Playwright (esto puede tardar)..."
"$VENV_DIR/bin/playwright" install

echo ""
echo "[OK] Proceso de instalación finalizado correctamente."
echo ""
echo "El entorno está listo. Puedes ejecutar el scraper con el archivo:"
echo "src/2-launch-scraper.sh (o el .bat correspondiente en Windows)"
echo ""
