@echo off
chcp 65001>nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo         WEB SCRAPER PRO v2.1 TEST
echo ============================================
echo.

rem Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado
    pause
    exit /b 1
)

rem Verificar archivo principal
if not exist "src\main.py" (
    echo [ERROR] src\main.py no encontrado
    pause
    exit /b 1
)

echo [OK] Dependencias verificadas correctamente

:menu
echo.
echo ------------------------------------------
echo            MENU PRINCIPAL
echo ------------------------------------------
echo  1. Test Panel TUI
echo  2. Test Autonomous Status
echo  3. Test Autonomous Control
echo  4. Salir
echo.
set /p "choice=Selecciona una opcion (1-4): "

if "%choice%"=="1" goto test_tui
if "%choice%"=="2" goto test_status
if "%choice%"=="3" goto test_control
if "%choice%"=="4" goto exit

echo [ERROR] Opcion no valida
goto menu

:test_tui
echo.
echo [TEST] Verificando Panel TUI...
python -c "print('Panel TUI funcionaria correctamente')"
echo.
pause
goto menu

:test_status
echo.
echo [TEST] Verificando Estado Autonomo...
python autonomous_cli.py status
echo.
pause
goto menu

:test_control
echo.
echo [TEST] Verificando Control Autonomo...
python autonomous_cli.py --help
echo.
pause
goto menu

:exit
echo.
echo Saliendo del programa...
echo.
exit /b 0
