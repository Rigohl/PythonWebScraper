@echo off

echo.
echo ==========================================================
echo =                   WEB SCRAPER PRO v2.1                 =
echo =      Panel de Control de Inteligencia Artificial      =
echo ==========================================================
echo.

rem --- Verificacion de Dependencias Criticas ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'python' no se encuentra en el PATH. Asegurate de que Python este instalado y accesible.
    pause
    exit /b 1
)
echo [DEBUG] Python found in PATH.

if not exist "src\main.py" (
    echo [ERROR] No se encuentra src\main.py. Asegurate de ejecutar desde la raiz del proyecto.
    pause
    exit /b 1
)

rem --- Activacion del Entorno Virtual ---
echo [DEBUG] Current directory: %cd%
cd /d "%~dp0"
echo [DEBUG] Changed directory to: %cd%

if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Entorno virtual '.venv' detectado. Activando...
    call .venv\Scripts\activate.bat
    echo [DEBUG] Virtual environment activated.
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Entorno virtual 'venv' detectado. Activando...
    call venv\Scripts\activate.bat
    echo [DEBUG] Virtual environment activated.
) else if exist "venv_validation\Scripts\activate.bat" (
    echo [INFO] Entorno de validacion 'venv_validation' detectado. Activando...
    call venv_validation\Scripts\activate.bat
    echo [DEBUG] Virtual environment activated.
) else (
    echo [INFO] No se encontro un entorno virtual. Creando '.venv'...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Entorno virtual '.venv' creado y activado.
)

rem --- Auto instalacion de dependencias GUI (PyQt6) opcional ---

rem --- Instalacion de dependencias siempre antes de lanzar GUI/TUI ---
echo [INFO] Instalando/actualizando dependencias requeridas...
pip install --upgrade -r requirements.txt
echo [INFO] Dependencias instaladas.

:menu
echo.
echo ----------------------------------------------------------
echo                    MENU PRINCIPAL
echo ----------------------------------------------------------
echo  1. Iniciar Panel Profesional (TUI Pro)
echo  2. Lanzar Mision Autonoma (Crawl)
echo  3. CONTROL AUTONOMO TOTAL - IA Independiente
echo  4. Estado del Sistema Autonomo
echo  5. Scraping Autonomo Inteligente
echo  6. Diagnostico y Reparacion IA
echo  7. Dialogar con el Cerebro (Base de Conocimiento)
echo  8. Entrenar Modelos de IA
echo  9. Ver Estado de Conciencia (Snapshot)
echo  10. Exportar Datos (CSV/JSON/MD)
echo  11. Verificar Integridad del Sistema (Tests)
echo  12. Mantenimiento del Sistema
echo  13. Multi-Terminal: Ejecutar comandos en paralelo (NUEVO)
echo  14. Salir
echo  15. Ayuda
echo.
set /p "choice=Selecciona una opcion (1-15): "

if "%choice%"=="1" goto tui
if "%choice%"=="2" goto crawl
if "%choice%"=="3" goto autonomous_control
if "%choice%"=="4" goto autonomous_status
if "%choice%"=="5" goto autonomous_scraping
if "%choice%"=="6" goto repair
if "%choice%"=="7" goto knowledge
if "%choice%"=="8" goto train
if "%choice%"=="9" goto snapshot
if "%choice%"=="10" goto export
if "%choice%"=="11" goto test
if "%choice%"=="12" goto maintenance
if "%choice%"=="13" goto multi_terminal
if "%choice%"=="14" goto exit
if "%choice%"=="15" goto help
echo [ERROR] Opcion no valida. Intentalo de nuevo.
goto menu

:tui
echo.
echo [INFO] Iniciando Panel Profesional (TUI Pro)...
set "HYBRID_BRAIN=1"
set "IA_SYNC_EVERY=10"
echo [INFO] HybridBrain habilitado para inteligencia avanzada.
echo [DEBUG] Intentando iniciar GUI PyQt6 (interfaz de escritorio)...
python -c "import sys; import src.gui.app as g; g.run_gui()" 2>nul
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] GUI no disponible o fallo inicial. Probando TUI Pro textual...
    python -m src.main --tui-pro
    if %errorlevel% neq 0 (
        echo [ADVERTENCIA] Fallo TUI Pro, intentando version TUI clasica...
        python -m src.main --tui
    )
)
echo.
echo [INFO] Sesion TUI finalizada.
goto END_PAUSE

:crawl
echo.
set /p "url=Introduce la URL para la mision autonoma: "
if "%url%"=="" (
    echo [ERROR] URL no puede estar vacia.
    pause
    goto menu
)
echo [INFO] Iniciando crawleo de %url%...
python -m src.main --crawl "%url%"
goto END_PAUSE

:autonomous_control
echo.
echo ============================================================
echo              CONTROL AUTONOMO TOTAL - IA INDEPENDIENTE
echo ============================================================
echo.
echo Iniciando Control Autonomo Completo del Sistema...
echo La IA tomara control total con minima intervencion humana
echo.
python scripts/autonomous_cli.py full-autonomy
echo.
echo Presiona cualquier tecla para regresar al menu...
pause
goto END_PAUSE

:autonomous_status
echo.
echo ============================================================
echo              ESTADO DEL SISTEMA AUTONOMO
echo ============================================================
echo.
echo Consultando estado de la conciencia artificial...
python scripts/autonomous_cli.py status
echo.
echo Presiona cualquier tecla para regresar al menu...
pause
goto END_PAUSE

:autonomous_scraping
echo.
echo ============================================================
echo              SCRAPING AUTONOMO INTELIGENTE
echo ============================================================
echo.
echo Iniciando scraping completamente autonomo...
echo La IA decidira que, como y cuando hacer scraping
echo.
python scripts/autonomous_cli.py start
echo.
echo Presiona cualquier tecla para regresar al menu...
pause
goto END_PAUSE

:repair
echo.
echo [INFO] Solicitando Reporte de Auto-Reparacion y Diagnostico...
python -m src.main --repair-report
echo [INFO] Reporte generado en IA_SELF_REPAIR.md
goto END_PAUSE

:knowledge
echo.
set /p "query=Tu consulta para el Cerebro: "
if "%query%"=="" (
    echo [ERROR] La consulta no puede estar vacia.
    pause
    goto menu
)
python -m src.main --query-kb "%query%"
goto END_PAUSE

:train
echo.
echo [INFO] Iniciando ciclo de entrenamiento para los modelos de IA...
python -m src.train_frontier_classifier
echo [INFO] Entrenamiento completado.
goto END_PAUSE

:snapshot
echo.
echo [INFO] Exportando snapshot del cerebro inteligente...
if not exist "exports" mkdir exports
rem Genera un timestamp robusto (YYYYMMDD_HHMMSS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set "dt=%%I"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
set "snapshot_file=exports\brain_snapshot_%timestamp%.json"
python -m src.main --brain-snapshot > "%snapshot_file%"
echo [INFO] Snapshot guardado en: %snapshot_file%
goto END_PAUSE

:export
echo.
echo Selecciona el formato de exportacion:
echo   a. CSV
echo   b. JSON
echo   c. Markdown
set /p "format_choice=Formato (a, b, c): "
if not defined format_choice goto export

set /p "filename=Nombre del archivo (sin extension): "
if not defined filename (
    echo [ERROR] El nombre del archivo no puede estar vacia.
    pause
    goto export
)

if not exist "exports" mkdir exports
set "export_path=exports\%filename%"

if /i '%format_choice%'=='a' python -m src.main --export-csv "%export_path%.csv"
if /i '%format_choice%'=='b' python -m src.main --export-json "%export_path%.json"
if /i '%format_choice%'=='c' python -m src.main --export-md "%export_path%.md"

echo [INFO] Exportacion completada.
pause
goto menu

:test
echo.
echo [INFO] Ejecutando suite de tests para verificar la integridad del sistema...
cd /d "%~dp0"
if exist "config\pytest.ini" (
    echo [INFO] Usando configuracion de pytest 'config/pytest.ini'.
    python -m pytest -c config\pytest.ini tests\ -v
) else (
    python -m pytest tests\ -v
)
pause
goto menu

:maintenance
cls
echo.
echo ----------------------------------------------------------
echo                  MENU DE MANTENIMIENTO
echo ----------------------------------------------------------
echo  a. Instalar/Actualizar dependencias
echo  b. Limpiar cache y archivos temporales
echo  c. Ver estadisticas de la Base de Datos
echo  d. Volver al menu principal
echo.
set /p "maint_choice=Selecciona una opcion (a-d): "

if /i "%maint_choice%"=="a" goto install_deps
if /i "%maint_choice%"=="b" goto cleanup
if /i "%maint_choice%"=="c" goto stats
if /i "%maint_choice%"=="d" goto menu
echo [ERROR] Opcion no valida.
goto maintenance

:install_deps
echo.
echo [INFO] Instalando/actualizando dependencias...
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-dev.txt
echo [INFO] Instalando navegadores de Playwright...
python -m playwright install
echo [INFO] Instalacion completada.
pause
goto maintenance

:cleanup
echo.
echo [INFO] Limpiando archivos temporales y cache...
rem Elimina recursivamente todos los directorios __pycache__
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
rem Elimina el cache de pytest si existe
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
echo [INFO] Limpieza completada.
pause
goto maintenance

:stats
echo.
echo [INFO] Generando estadisticas de base de datos...
python scripts\check_data_quality.py
python scripts\generate_metrics.py
pause
goto maintenance

:multi_terminal
echo.
echo ============================================================
echo             EJECUCION MULTI-TERMINAL PARALELA
echo ============================================================
echo.
echo [INFO] Iniciando 5 terminales en paralelo para acelerar operaciones...

rem Crear y ejecutar scripts temporales para cada terminal
echo @echo off > "%TEMP%\terminal1.bat"
echo title Terminal 1: Verificacion del Sistema >> "%TEMP%\terminal1.bat"
echo color 0A >> "%TEMP%\terminal1.bat"
echo cd /d "%~dp0" >> "%TEMP%\terminal1.bat"
echo echo [INFO] Verificando archivos del proyecto... >> "%TEMP%\terminal1.bat"
echo dir /s /b *.py *.md *.txt *.bat *.sh ^| find /c "." >> "%TEMP%\terminal1.bat"
echo echo. >> "%TEMP%\terminal1.bat"
echo echo [INFO] Mostrando estructura del proyecto: >> "%TEMP%\terminal1.bat"
echo python -c "import os; print('\n'.join([d for d in os.listdir('.') if os.path.isdir(d)]))" >> "%TEMP%\terminal1.bat"
echo echo. >> "%TEMP%\terminal1.bat"
echo echo Presiona cualquier tecla para cerrar esta terminal... >> "%TEMP%\terminal1.bat"
echo pause >> "%TEMP%\terminal1.bat"

echo @echo off > "%TEMP%\terminal2.bat"
echo title Terminal 2: Analisis de Documentacion >> "%TEMP%\terminal2.bat"
echo color 0B >> "%TEMP%\terminal2.bat"
echo cd /d "%~dp0" >> "%TEMP%\terminal2.bat"
echo echo [INFO] Analizando documentacion del proyecto... >> "%TEMP%\terminal2.bat"
echo if exist README.md (type README.md ^| find "##" ^| sort) else (echo No se encontro README.md) >> "%TEMP%\terminal2.bat"
echo echo. >> "%TEMP%\terminal2.bat"
echo echo [INFO] Resumen de archivos de configuracion: >> "%TEMP%\terminal2.bat"
echo python -c "import glob; print('\n'.join(glob.glob('config/*.*') + glob.glob('*.toml') + glob.glob('*.yaml')))" >> "%TEMP%\terminal2.bat"
echo echo. >> "%TEMP%\terminal2.bat"
echo echo Presiona cualquier tecla para cerrar esta terminal... >> "%TEMP%\terminal2.bat"
echo pause >> "%TEMP%\terminal2.bat"

echo @echo off > "%TEMP%\terminal3.bat"
echo title Terminal 3: Ejecucion Demo Rapida >> "%TEMP%\terminal3.bat"
echo color 0E >> "%TEMP%\terminal3.bat"
echo cd /d "%~dp0" >> "%TEMP%\terminal3.bat"
echo echo [INFO] Ejecutando modo demo para validacion rapida... >> "%TEMP%\terminal3.bat"
echo echo. >> "%TEMP%\terminal3.bat"
echo if exist ".venv\Scripts\activate.bat" (call .venv\Scripts\activate.bat) else if exist "venv\Scripts\activate.bat" (call venv\Scripts\activate.bat) >> "%TEMP%\terminal3.bat"
echo python -m src.main --demo >> "%TEMP%\terminal3.bat"
echo echo. >> "%TEMP%\terminal3.bat"
echo echo Presiona cualquier tecla para cerrar esta terminal... >> "%TEMP%\terminal3.bat"
echo pause >> "%TEMP%\terminal3.bat"

rem Preparar archivo de log si no existe para tail en Terminal 4
if not exist "logs" mkdir "logs"
if not exist "logs\scraper_run.log" type nul > "logs\scraper_run.log"

rem Terminal 4: Monitoreo de logs en vivo (PowerShell Get-Content -Wait)
echo @echo off > "%TEMP%\terminal4.bat"
echo title Terminal 4: Monitoreo de Logs (live tail) >> "%TEMP%\terminal4.bat"
echo color 0C >> "%TEMP%\terminal4.bat"
echo cd /d "%~dp0" >> "%TEMP%\terminal4.bat"
echo echo [INFO] Monitoreando logs\scraper_run.log (Ctrl+C para salir)... >> "%TEMP%\terminal4.bat"
echo powershell -NoExit -Command "Get-Content -Path 'logs/scraper_run.log' -Tail 50 -Wait" >> "%TEMP%\terminal4.bat"

rem Terminal 5: Pruebas de rendimiento basicas
echo @echo off > "%TEMP%\terminal5.bat"
echo title Terminal 5: Tests de Rendimiento >> "%TEMP%\terminal5.bat"
echo color 0D >> "%TEMP%\terminal5.bat"
echo cd /d "%~dp0" >> "%TEMP%\terminal5.bat"
echo if exist ".venv\Scripts\activate.bat" (call .venv\Scripts\activate.bat) else if exist "venv\Scripts\activate.bat" (call venv\Scripts\activate.bat) >> "%TEMP%\terminal5.bat"
echo echo [INFO] Ejecutando tests de rendimiento en tests\performance\ ... >> "%TEMP%\terminal5.bat"
echo if exist "config\pytest.ini" (python -m pytest -c config\pytest.ini tests\performance\ -v) else (python -m pytest tests\performance\ -v) >> "%TEMP%\terminal5.bat"
echo echo. >> "%TEMP%\terminal5.bat"
echo echo Presiona cualquier tecla para cerrar esta terminal... >> "%TEMP%\terminal5.bat"
echo pause >> "%TEMP%\terminal5.bat"

rem Iniciar los terminales en paralelo
echo [INFO] Lanzando Terminal 1: Verificacion del Sistema...
start cmd /c "%TEMP%\terminal1.bat"

echo [INFO] Lanzando Terminal 2: Analisis de Documentacion...
start cmd /c "%TEMP%\terminal2.bat"

echo [INFO] Lanzando Terminal 3: Ejecucion Demo Rapida...
start cmd /c "%TEMP%\terminal3.bat"

echo [INFO] Lanzando Terminal 4: Monitoreo de Logs (live tail)...
start cmd /c "%TEMP%\terminal4.bat"

echo [INFO] Lanzando Terminal 5: Tests de Rendimiento...
start cmd /c "%TEMP%\terminal5.bat"

echo.
echo [INFO] 5 terminales lanzados en paralelo.
echo [INFO] Esto permite ejecutar comandos simultáneamente para acelerar el flujo de trabajo.
echo.
echo [CONSEJO] Puedes personalizar los comandos en los scripts temporales en el codigo fuente.
echo.
pause
goto menu

:help
cls
echo.
echo ----------------------------------------------------------
echo                       AYUDA
echo ----------------------------------------------------------
echo  1. Iniciar Panel Profesional (TUI Pro):
echo     Inicia la interfaz de usuario basada en texto (TUI) profesional.
echo     Permite interactuar con el sistema de scraping de forma avanzada.
echo.
echo  2. Lanzar Mision Autonoma (Crawl):
echo     Inicia un proceso de rastreo (crawling) de una URL especifica.
echo     El sistema intentara extraer informacion de la URL proporcionada.
echo.
echo  3. CONTROL AUTONOMO TOTAL - IA Independiente:
echo     Activa el modo de control autonomo completo. La IA tomara decisiones
echo     y ejecutara tareas de scraping de forma independiente.
echo.
echo  4. Estado del Sistema Autonomo:
echo     Muestra el estado actual y las metricas del sistema autonomo de IA.
echo.
echo  5. Scraping Autonomo Inteligente:
echo     Inicia un proceso de scraping donde la IA decide que, como y cuando
echo     realizar el scraping, optimizando la extraccion de datos.
echo.
echo  6. Diagnostico y Reparacion IA:
echo     Genera un reporte de diagnostico y auto-reparacion del sistema de IA.
echo     Ayuda a identificar y solucionar problemas.
echo.
echo  7. Dialogar con el Cerebro (Base de Conocimiento):
echo     Permite realizar consultas a la base de conocimiento del sistema (el "Cerebro").
echo     Puedes preguntar sobre datos, configuraciones o el funcionamiento interno.
echo.
echo  8. Entrenar Modelos de IA:
echo     Inicia el proceso de entrenamiento para los modelos de inteligencia artificial
echo     del sistema, mejorando su rendimiento y precision.
echo.
echo  9. Ver Estado de Conciencia (Snapshot):
echo     Exporta un "snapshot" (instantanea) del estado actual del cerebro inteligente.
echo     Esto incluye su configuracion, datos de aprendizaje y estado interno.
echo.
echo  10. Exportar Datos (CSV/JSON/MD):
echo      Permite exportar los datos extraidos en diferentes formatos:
echo      - CSV: Para hojas de calculo y analisis de datos.
echo      - JSON: Para integracion con otras aplicaciones y APIs.
echo      - Markdown: Para reportes legibles y documentacion.
echo.
echo  11. Verificar Integridad del Sistema (Tests):
echo      Ejecuta la suite de pruebas unitarias y de integracion para verificar
echo      que todos los componentes del sistema funcionan correctamente.
echo.
echo  12. Mantenimiento del Sistema:
echo      Accede a un sub-menu con opciones de mantenimiento, como:
echo      - Instalar/Actualizar dependencias.
echo      - Limpiar cache y archivos temporales.
echo      - Ver estadisticas de la base de datos.
echo.
echo  13. Multi-Terminal: Ejecutar comandos en paralelo:
echo      Abre 3 terminales simultáneos para ejecutar diferentes tareas:
echo      - Terminal 1: Verificacion del sistema y archivos
echo      - Terminal 2: Análisis de documentación y configuración
echo      - Terminal 3: Ejecución demo para validación rápida
echo      Esta opción acelera el flujo de trabajo al permitir operaciones paralelas.
echo.
echo  14. Salir:
echo      Finaliza la ejecucion del script y cierra la conexion con la IA.
echo.
echo  15. Ayuda:
echo      Muestra esta pantalla de ayuda con la descripcion de cada opcion.
echo.
pause
goto menu

:exit
echo.
echo [INFO] Conexion con la IA finalizada.
goto END_PAUSE

:END_PAUSE
echo.
echo [INFO] Presiona cualquier tecla para continuar...
pause
exit /b 0
