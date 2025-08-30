@echo off
echo [DEBUG] Iniciando el script de instalacion...
pause

setlocal enabledelayedexpansion

REM --- Verificaciones Previas ---
echo [INFO] Verificando que el script se ejecute desde la raiz del proyecto...
if not exist "requirements.txt" (
    echo [ERROR] Missing requirements.txt
    pause
    exit /b 1
)
echo [DEBUG] Verificacion de raiz del proyecto superada.

REM --- Verificacion de Python ---
echo [INFO] Verificando la version de Python...
set "PYTHON_EXE="
where python >nul 2>&1 && set "PYTHON_EXE=python"
if not defined PYTHON_EXE (
    where py >nul 2>&1 && set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
    echo [ERROR] No se pudo encontrar el comando 'python' o 'py'.
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
        echo [ERROR] Se requiere Python 3
        pause
        exit /b 1
    )
    if "%%b" LSS "10" (
        echo [ERROR] Se requiere Python 3.10+
        pause
        exit /b 1
    )
)
echo [DEBUG] Verificacion de version de Python superada.

pause
exit /b 0