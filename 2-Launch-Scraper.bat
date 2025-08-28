@echo off
cd /d "%~dp0"

REM [INFO] Activando entorno virtual...
REM call .\.venv\Scripts\activate

echo [INFO] Lanzando Scraper PRO...
.\.venv\Scripts\python.exe src/main.py --tui

pause
