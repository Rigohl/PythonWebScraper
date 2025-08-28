#!/bin/bash
echo "Creando entorno virtual en ./.venv..."
python -m venv .venv

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Instalando dependencias de Python desde requirements.txt..."
pip install -r requirements.txt

echo "Instalando navegadores de Playwright..."
playwright install

echo "¡Instalación completada!"
