@echo off
set VENV_DIR=.\.venv

echo [INFO] Verificando si el entorno virtual existe...
if not exist "%VENV_DIR%" (
    echo [INFO] Creando entorno virtual en %VENV_DIR%...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual. Asegurate que Python este en el PATH.
        pause
        exit /b 1
    )
)

echo [INFO] Instalando/actualizando dependencias de Python...
"%VENV_DIR%\Scripts\pip.exe" install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias de Python (pip).
    pause
    exit /b 1
)

echo [INFO] Instalando navegadores para Playwright (esto puede tardar)...
"%VENV_DIR%\Scripts\playwright.exe" install
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar los navegadores de Playwright.
    pause
    exit /b 1
)

echo.
echo [OK] Proceso de instalacion finalizado correctamente.
echo.
echo El entorno esta listo. Puedes ejecutar el scraper con el archivo:
echo 2-Launch-Scraper.bat
echo.
pause
