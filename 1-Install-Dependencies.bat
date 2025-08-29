@echo off
setlocal enabledelayedexpansion

REM --- Verificaciones Previas ---
echo [INFO] Verificando que el script se ejecute desde la raiz del proyecto...
if not exist "requirements.txt" (
    echo [ERROR] Este script debe ejecutarse desde la carpeta raiz del proyecto (donde se encuentra 'requirements.txt').
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
        echo [ERROR] No se pudo eliminar el entorno virtual anterior en "%VENV_DIR%".
        echo [ERROR] Asegurate de que no este en uso por otra aplicacion (p.ej. tu editor de codigo o una terminal activa).
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
echo [INFO] Activando entorno virtual e instalando dependencias...
call "%VENV_DIR%\Scripts\activate.bat"

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] No se pudo actualizar pip, se continuara con la version actual.
)

echo [INFO] Instalando dependencias de 'requirements.txt'...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias de Python (pip).
    echo [ERROR] Revisa el archivo 'requirements.txt' y tu conexion a internet.
    pause
    exit /b 1
)

echo [INFO] Instalando navegadores para Playwright...
playwright install
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar los navegadores de Playwright.
    echo [ERROR] Intenta ejecutar 'playwright install' manualmente despues de activar el entorno virtual.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] La instalacion se ha completado correctamente.
echo [SUCCESS] Ya puedes lanzar la aplicacion con '2-Launch-Scraper.bat'.
pause
exit /b 0
