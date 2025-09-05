<#
cleanup_backups.ps1

Script seguro para limpiar backups antiguos en `backups/snapshots/`.
Por defecto muestra qué eliminaría y requiere confirmación interactiva.
#>

param(
    [int]$DaysToKeep = 30,
    [switch]$WhatIf
)

$cutoff = (Get-Date).AddDays(-$DaysToKeep)
Write-Host "Buscando backups anteriores a $cutoff (conservando $DaysToKeep días)"

$old = Get-ChildItem -Path "backups\snapshots" -Directory | Where-Object { $_.LastWriteTime -lt $cutoff }
if (-not $old) {
    Write-Host "No se encontraron backups antiguos para eliminar."
    exit 0
}

Write-Host "Se encontraron los siguientes backups antiguos:"
$old | ForEach-Object { Write-Host " - $($_.FullName) (última modificación: $($_.LastWriteTime))" }

if ($WhatIf.IsPresent) {
    Write-Host "Modo --WhatIf: no se eliminará nada."
    exit 0
}

$confirm = Read-Host "¿Deseas eliminar estos backups? (s/n)"
if ($confirm -ne 's') {
    Write-Host "Cancelado por el usuario. Ningún archivo fue eliminado."
    exit 0
}

$old | ForEach-Object { Remove-Item -Path $_.FullName -Recurse -Force }
Write-Host "Backups antiguos eliminados."
