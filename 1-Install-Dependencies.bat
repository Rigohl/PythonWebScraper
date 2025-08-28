@echo off
setlocal

set VENV_DIR=.\.venv

echo [INFO] Eliminando entorno virtual antiguo (si existe) para una instalacion limpia...
if exist "%VENV_DIR%\" (
    rmdir /s /q "%VENV_DIR%"
)

echo [INFO] Creando nuevo entorno virtual en %VENV_DIR%...
python -m venv --upgrade-deps "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual. Asegurate que Python este en el PATH.
    pause
    goto :eof
)

echo [INFO] Instalando/actualizando dependencias de Python...
"%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias de Python (pip).
    pause
    goto :eof
)

echo [INFO] Instalando navegadores para Playwright (esto puede tardar)...
"%VENV_DIR%\Scripts\playwright.exe" install
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar los navegadores de Playwright.
    pause
    goto :eof
)

echo.
echo [OK] Proceso de instalacion finalizado correctamente.
echo.
echo El entorno esta listo. Puedes ejecutar el scraper con el archivo:
echo 2-Launch-Scraper.bat
echo.

REM Delete log file
del "%~dp0install_log.txt" 2>nul

pause
goto :eof
