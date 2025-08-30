@echo off
setlocal

set VENV_DIR=.\.venv

echo [INFO] Verificando el entorno virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado en "%VENV_DIR%".
    echo [ERROR] Por favor, ejecuta primero '1-Install-Dependencies.bat'.
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual y lanzando la TUI...

REM Usamos cmd /k para lanzar un nuevo proceso cmd que active el venv y ejecute python.
REM Esto mantiene la ventana abierta después de que el script de python termine,
REM permitiendo ver cualquier salida o error.
cmd /k ""%VENV_DIR%\Scripts\activate.bat" && python src/main.py --tui"
@echo off
setlocal

set VENV_DIR=.\.venv

echo [INFO] Verificando el entorno virtual...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado en "%VENV_DIR%".
    echo [ERROR] Por favor, ejecuta primero '1-Install-Dependencies.bat'.
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual y lanzando la TUI...

REM Usamos cmd /k para lanzar un nuevo proceso cmd que active el venv y ejecute python.
REM Esto mantiene la ventana abierta después de que el script de python termine,
REM permitiendo ver cualquier salida o error.
cmd /k ""%VENV_DIR%\Scripts\activate.bat" && python src/main.py --tui"
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
