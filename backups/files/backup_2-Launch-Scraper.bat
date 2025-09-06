@echo off

echo [INFO] Verificando que el script se ejecute desde la raiz del proyecto...
if not exist ".venv" (
    echo [ERROR] Entorno virtual no encontrado. Ejecuta 1-Install-Dependencies.bat primero.
    pause
    exit /b 1
)

echo [INFO] Activando el entorno virtual...
call .\.venv\Scripts\activate.bat

echo [INFO] Lanzando la aplicacion TUI...
:: La clave es usar "python -m src.main" en lugar de "python src\main.py"
:: Esto le dice a Python que ejecute el módulo 'main' dentro del paquete 'src'.
python -m src.main --tui

echo [INFO] La aplicacion se ha cerrado. Presiona cualquier tecla para salir.
pause

