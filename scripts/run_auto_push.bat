:: filepath: c:\Users\DELL\Desktop\PythonWebScraper\scripts\run_auto_push.bat
@echo off
rem If no arguments are provided, enable auto-push by default for convenience.
if "%~1"=="" (
	set AUTO_PUSH_ENABLE=1
)
python "%~dp0auto_push_manager.py" %*
