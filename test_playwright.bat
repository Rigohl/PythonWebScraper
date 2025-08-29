@echo off
setlocal enabledelayedexpansion
set "VENV_DIR=.venv"
set "VENV_PLAYWRIGHT=%VENV_DIR%\Scripts\playwright.exe"

echo [INFO] Instalando navegadores para Playwright...
"%VENV_PLAYWRIGHT%" install
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar los navegadores de Playwright.
    pause
    exit /b 1
)

echo [SUCCESS] Playwright install command finished.
pause
