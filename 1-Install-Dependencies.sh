#!/bin/bash
# Este script instala las dependencias del proyecto en un entorno virtual
# para sistemas Linux y macOS.

# Detener el script si un comando falla
set -e

VENV_DIR="./.venv"

echo "[INFO] Eliminando entorno virtual antiguo (si existe) para una instalacion limpia..."
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
fi

echo "[INFO] Creando nuevo entorno virtual en $VENV_DIR..."
# Usamos python3, que es el estándar en la mayoría de sistemas Linux/macOS modernos
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el entorno virtual. Asegúrate de que 'python3' y el paquete 'python3-venv' estén instalados."
    exit 1
fi

echo "[INFO] Instalando/actualizando dependencias de Python..."
"$VENV_DIR/bin/pip" install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar las dependencias de Python (pip)."
    exit 1
fi

echo "[INFO] Instalando navegadores para Playwright (esto puede tardar)..."
# El flag --with-deps intenta instalar dependencias del sistema operativo. Es útil en Ubuntu.
"$VENV_DIR/bin/playwright" install --with-deps
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar los navegadores de Playwright."
    exit 1
fi

echo ""
echo "[OK] Proceso de instalacion finalizado correctamente."
echo "El entorno esta listo. Revisa README.md para instrucciones sobre cómo lanzar la aplicación."
echo ""
