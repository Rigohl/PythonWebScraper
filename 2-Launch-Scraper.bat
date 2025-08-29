@echo off
setlocal

set VENV_DIR=.\.venv

echo [INFO] Verificando si el entorno virtual existe...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] El entorno virtual no se encuentra en "%VENV_DIR%".
    echo [ERROR] Por favor, ejecuta primero el script '1-Install-Dependencies.bat'.
    pause
    goto :eof
)

echo [INFO] Lanzando la interfaz de usuario (TUI)...
"%VENV_DIR%\Scripts\python.exe" src/main.py --tui

pause