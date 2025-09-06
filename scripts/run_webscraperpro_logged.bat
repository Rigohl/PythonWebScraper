@echo off
set LOG_FILE=webscraperpro_log.txt
echo Ejecutando webscraperpro.bat y registrando la salida en %LOG_FILE%
call webscraperpro.bat > %LOG_FILE% 2>&1
echo Ejecucion finalizada. Revisa %LOG_FILE% para ver la salida.