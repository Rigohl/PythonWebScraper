# Script de respaldo de comunicaciones
# Ejecutar manualmente o programar como tarea

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "c:/Users/DELL/Desktop/PythonWebScraper/backups/collaboration/communication_$timestamp.md"
Copy-Item "c:/Users/DELL/Desktop/PythonWebScraper/ai/collaboration/reports/communication_log.md" $backupFile -Force

Write-Host "Respaldo creado: $backupFile" -ForegroundColor Green
