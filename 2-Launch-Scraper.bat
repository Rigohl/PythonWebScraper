@echo off
setlocal

REM --- Verificacion de la ubicacion ---
echo [INFO] Verificando que el script se ejecute desde la raiz del proyecto...
if not exist "src\main.py" (
    echo [ERROR] Este script debe ejecutarse desde la carpeta raiz del proyecto.
    echo [ERROR] No se pudo encontrar 'src\main.py'.
    pause
    exit /b 1
)

REM --- Verificacion del Entorno Virtual ---
echo [INFO] Verificando la existencia del entorno virtual...
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual en la carpeta '.venv'.
    echo [ERROR] Por favor, ejecuta '1-Install-Dependencies.bat' primero.
    pause
    exit /b 1
)

REM --- Activacion y Lanzamiento ---
echo [INFO] Activando el entorno virtual...
call .venv\Scripts\activate.bat

echo [INFO] Lanzando la aplicacion TUI...
python src/main.py --tui

echo.
echo [INFO] La aplicacion se ha cerrado. Presiona cualquier tecla para salir.
pause
exit /b 0
