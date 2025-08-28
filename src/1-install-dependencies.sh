#!/bin/bash
echo "Creando entorno virtual en ./.venv..."
python3 -m venv .venv

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Instalando dependencias de Python desde requirements.txt..."
.venv/bin/pip install -r requirements.txt

echo "Instalando navegadores de Playwright..."
.venv/bin/playwright install

echo "¡Instalación completada!"
