@echo off
cd /d "%~dp0"

REM [INFO] Activando entorno virtual...
REM call .\.venv\Scripts\activate

REM Add project root to PYTHONPATH
set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo [INFO] Lanzando Scraper PRO...
.\.venv\Scripts\python.exe -m src.main --tui

pause
