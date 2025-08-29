@echo off
setlocal enabledelayedexpansion

REM --- Verificaciones Previas ---
echo [INFO] Verificando que el script se ejecute desde la raiz del proyecto...
if not exist "requirements.txt" (
    echo [ERROR] Este script debe ejecutarse desde la carpeta raiz del proyecto.
    pause
    exit /b 1
)

REM --- Verificacion de Python ---
echo [INFO] Verificando la version de Python...
set "PYTHON_EXE="
where python >nul 2>&1 && set "PYTHON_EXE=python"
if not defined PYTHON_EXE (
    where py >nul 2>&1 && set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
    echo [ERROR] No se pudo encontrar el comando 'python' o 'py'.
    echo [ERROR] Asegurate de que Python 3.10+ este instalado y en tu PATH.
    pause
    exit /b 1
)
echo [INFO] Usando ejecutable de Python: %PYTHON_EXE%

set "PYTHON_VERSION="
for /f "tokens=2" %%i in ('%PYTHON_EXE% --version 2^>^&1') do set "PYTHON_VERSION=%%i"

echo [INFO] Version de Python detectada: !PYTHON_VERSION!
if not defined PYTHON_VERSION (
    echo [ERROR] No se pudo determinar la version de Python.
    pause
    exit /b 1
)

for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    if "%%a" NEQ "3" (
        echo [ERROR] Se requiere Python 3. Version encontrada: !PYTHON_VERSION!
        pause
        exit /b 1
    )
    if "%%b" LSS "10" (
        echo [ERROR] Se requiere Python 3.10 o superior. Version detectada: !PYTHON_VERSION!
        pause
        exit /b 1
    )
)

REM --- Configuracion del Entorno Virtual ---
set "VENV_DIR=.venv"
echo [INFO] Configurando el entorno virtual en "%VENV_DIR%"...

if exist "%VENV_DIR%" (
    echo [INFO] Eliminando entorno virtual anterior...
    rmdir /s /q "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] No se pudo eliminar el entorno virtual anterior.
        echo [ERROR] Asegurate de que no este en uso por otra aplicacion.
        pause
        exit /b 1
    )
)

echo [INFO] Creando nuevo entorno virtual...
%PYTHON_EXE% -m venv %VENV_DIR%
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

REM --- Instalacion de Dependencias ---
echo [INFO] Instalando dependencias...

set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"
set "VENV_PLAYWRIGHT=%VENV_DIR%\Scripts\playwright.exe"

echo [INFO] Actualizando pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] No se pudo actualizar pip, se continuara con la version actual.
)

echo [INFO] Instalando dependencias de requirements.txt...
"%VENV_PIP%" install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias de Python (pip).
    pause
    exit /b 1
)

echo [INFO] Instalando navegadores para Playwright...
"%VENV_PLAYWRIGHT%" install
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar los navegadores de Playwright.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] La instalacion se ha completado correctamente.
echo [SUCCESS] Ya puedes lanzar la aplicacion con '2-Launch-Scraper.bat'.
pause
exit /b 0