@echo off
REM WebScraperPRO.bat - Script mejorado con nueva interfaz profesional
setlocal enabledelayedexpansion

echo ===============================================
echo    🕷️  Web Scraper PRO - Professional Edition
echo ===============================================
echo.

REM Configurar variables de entorno para máximo rendimiento
set HYBRID_BRAIN=1
set IA_SYNC_EVERY=50
set PYTHONPATH=%CD%

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo    Descarga Python desde: https://python.org
    pause
    exit /b 1
)

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo 🔧 Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:MENU
cls
echo ===============================================
echo    🕷️  Web Scraper PRO - Professional Edition
echo ===============================================
echo.
echo Selecciona una opción:
echo.
echo  [1] 🚀 Dashboard Profesional (NUEVO)
echo  [2] 📱 Interfaz TUI Clásica
echo  [3] 🕷️  Crawling Directo
echo  [4] 🎮 Modo Demo
echo  [5] 📊 Brain Snapshot
echo  [6] 📤 Exportar Datos
echo  [7] 🔧 Configuración
echo  [8] ❓ Ayuda
echo  [9] 🚪 Salir
echo.
set /p choice="👉 Opción: "

if "%choice%"=="1" goto PROFESSIONAL_TUI
if "%choice%"=="2" goto CLASSIC_TUI
if "%choice%"=="3" goto DIRECT_CRAWL
if "%choice%"=="4" goto DEMO_MODE
if "%choice%"=="5" goto BRAIN_SNAPSHOT
if "%choice%"=="6" goto EXPORT_DATA
if "%choice%"=="7" goto CONFIGURATION
if "%choice%"=="8" goto HELP
if "%choice%"=="9" goto EXIT

echo ❌ Opción inválida. Por favor selecciona 1-9.
timeout /t 2 >nul
goto MENU

:PROFESSIONAL_TUI
cls
echo 🚀 Iniciando Dashboard Profesional...
echo ===============================================
echo  • Interfaz moderna y profesional
echo  • Todas las capacidades integradas
echo  • Monitoreo en tiempo real
echo  • Control completo de IA
echo ===============================================
echo.
python -m src.main --tui-pro
goto END

:CLASSIC_TUI
cls
echo 📱 Iniciando Interfaz TUI Clásica...
echo ===============================================
echo  • Interfaz TUI original
echo  • Funcionalidad completa
echo  • Compatible con versiones anteriores
echo ===============================================
echo.
python -m src.main --tui
goto END

:DIRECT_CRAWL
cls
echo 🕷️ Modo Crawling Directo
echo ===============================================
echo.
set /p url="👉 Ingresa URL para scraping: "
if "%url%"=="" (
    echo ❌ URL requerida
    timeout /t 2 >nul
    goto MENU
)
echo.
echo 🚀 Iniciando crawling de: %url%
echo 🧠 HybridBrain: ACTIVO
echo ⚡ Modo: Máximo rendimiento
echo.
python -m src.main --crawl "%url%"
goto END

:DEMO_MODE
cls
echo 🎮 Modo Demo
echo ===============================================
echo  • Demostración sin scraping real
echo  • Perfecto para pruebas
echo  • Sin dependencias de navegador
echo ===============================================
echo.
python -m src.main --demo
goto END

:BRAIN_SNAPSHOT
cls
echo 📊 Brain Snapshot
echo ===============================================
echo  • Estado actual del HybridBrain
echo  • Métricas de inteligencia
echo  • Datos de aprendizaje
echo ===============================================
echo.
python -m src.main --brain-snapshot
echo.
echo 💾 Snapshot generado
pause
goto MENU

:EXPORT_DATA
cls
echo 📤 Exportar Datos
echo ===============================================
echo.
echo Selecciona formato:
echo  [1] CSV
echo  [2] JSON
echo  [3] Markdown
echo  [4] Volver al menú
echo.
set /p export_choice="👉 Formato: "

if "%export_choice%"=="1" (
    set /p filename="👉 Nombre archivo CSV: "
    if "!filename!"=="" set filename=export_data.csv
    python -m src.main --export-csv "exports/!filename!"
    echo ✅ Datos exportados a exports/!filename!
)
if "%export_choice%"=="2" (
    set /p filename="👉 Nombre archivo JSON: "
    if "!filename!"=="" set filename=export_data.json
    python -m src.main --export-json "exports/!filename!"
    echo ✅ Datos exportados a exports/!filename!
)
if "%export_choice%"=="3" (
    set /p filename="👉 Nombre archivo MD: "
    if "!filename!"=="" set filename=export_report.md
    python -m src.main --export-md "exports/!filename!"
    echo ✅ Reporte exportado a exports/!filename!
)
if "%export_choice%"=="4" goto MENU

pause
goto MENU

:CONFIGURATION
cls
echo 🔧 Configuración del Sistema
echo ===============================================
echo.
echo Variables de entorno actuales:
echo  • HYBRID_BRAIN: %HYBRID_BRAIN%
echo  • IA_SYNC_EVERY: %IA_SYNC_EVERY%
echo  • PYTHONPATH: %PYTHONPATH%
echo.
echo Configuraciones disponibles:
echo  [1] Activar/Desactivar HybridBrain
echo  [2] Ajustar frecuencia sync IA
echo  [3] Ver configuración completa
echo  [4] Volver al menú
echo.
set /p config_choice="👉 Opción: "

if "%config_choice%"=="1" (
    if "%HYBRID_BRAIN%"=="1" (
        set HYBRID_BRAIN=0
        echo ❌ HybridBrain DESACTIVADO
    ) else (
        set HYBRID_BRAIN=1
        echo ✅ HybridBrain ACTIVADO
    )
    timeout /t 2 >nul
)
if "%config_choice%"=="2" (
    set /p new_sync="👉 Nueva frecuencia sync (actual: %IA_SYNC_EVERY%): "
    if not "!new_sync!"=="" (
        set IA_SYNC_EVERY=!new_sync!
        echo ✅ Frecuencia actualizada a !new_sync!
    )
    timeout /t 2 >nul
)
if "%config_choice%"=="3" (
    echo.
    echo 📋 Configuración completa:
    python -m src.main --help
    pause
)
if "%config_choice%"=="4" goto MENU

goto CONFIGURATION

:HELP
cls
echo ❓ Ayuda - Web Scraper PRO
echo ===============================================
echo.
echo 🚀 DASHBOARD PROFESIONAL (NUEVO):
echo    • Interfaz moderna tipo dashboard
echo    • Control completo de todas las funciones
echo    • Monitoreo en tiempo real
echo    • Gestión avanzada de IA
echo    • Exportación integrada
echo.
echo 📱 INTERFAZ TUI CLÁSICA:
echo    • Interfaz de texto original
echo    • Todas las funciones disponibles
echo    • Compatible con scripts existentes
echo.
echo 🕷️ CRAWLING DIRECTO:
echo    • Scraping inmediato de una URL
echo    • Máximo rendimiento
echo    • HybridBrain automático
echo.
echo 🎮 MODO DEMO:
echo    • Demostración sin scraping real
echo    • Ideal para pruebas y training
echo.
echo 📊 BRAIN SNAPSHOT:
echo    • Estado actual del sistema IA
echo    • Métricas de aprendizaje
echo    • Análisis de rendimiento
echo.
echo 📤 EXPORTACIÓN:
echo    • CSV: Datos estructurados
echo    • JSON: Formato universal
echo    • Markdown: Reportes legibles
echo.
echo 🧠 CARACTERÍSTICAS IA:
echo    • HybridBrain (IA-A + IA-B)
echo    • Aprendizaje autónomo
echo    • Auto-reparación
echo    • Neural networks
echo    • LLM integration
echo    • RL Agent
echo.
echo Para más información consulta README.md
echo.
pause
goto MENU

:END
echo.
echo ✅ Proceso completado
pause

:EXIT
echo.
echo 👋 ¡Gracias por usar Web Scraper PRO!
echo    Desarrollado con ❤️ para máximo rendimiento
timeout /t 2 >nul
exit /b 0
