@echo off
setlocal enabledelayedexpansion

@echo off
echo [INFO] Creando entorno virtual en .venv...
python -m venv .venv

echo [INFO] Activando el entorno virtual...
call .venv\Scripts\activate.bat

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt

echo [INFO] Instalando navegadores para Playwright...
playwright install

echo.
echo [SUCCESS] La instalacion ha finalizado.
pause
