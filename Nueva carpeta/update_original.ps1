<#
    Update the original scraper file in your repository with the refactored version.

    This script is designed for one‑time use. It backs up the existing
    ``src\scraper.py`` file, extracts the refactored version from a ZIP
    archive and overwrites the original. Adjust the parameters below to
    match your repository location and the path to the downloaded zip
    archive.

    Usage:
        .\update_original.ps1 -RepoPath "C:\Path\To\PythonWebScraper" -RefactorZip "C:\Downloads\webscraper_refactor.zip"

    Parameters:
        -RepoPath:     The root directory of your PythonWebScraper repository.
        -RefactorZip:  Path to the ``webscraper_refactor.zip`` archive you downloaded from ChatGPT.
#>


param(
    [string]$RepoPath = '.',
    [string]$RefactorZip = 'webscraper_refactor.zip'
)

Push-Location $RepoPath

# Ensure the archive exists before proceeding
if (-not (Test-Path -LiteralPath $RefactorZip)) {
    Write-Error "El archivo de mejoras `$RefactorZip` no existe en este directorio."
    Pop-Location
    exit 1
}

# Backup the existing src and tests directories to a timestamped folder.
$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$backupDir = "backup_$timestamp"
if (Test-Path -LiteralPath 'src') {
    Copy-Item -Path 'src' -Destination $backupDir -Recurse -Force
    Write-Host "Directorio 'src' respaldado en $backupDir"
} else {
    Write-Warning "Directorio 'src' no encontrado en el repositorio. No se realizó respaldo."
}
if (Test-Path -LiteralPath 'tests') {
    Copy-Item -Path 'tests' -Destination $backupDir\tests -Recurse -Force
    Write-Host "Directorio 'tests' respaldado en $backupDir\tests"
} else {
    Write-Warning "Directorio 'tests' no encontrado."
}

# Extract the refactored files to a temporary directory
$tempDir = Join-Path -Path $env:TEMP -ChildPath "webscraper_refactor_$timestamp"
Expand-Archive -LiteralPath $RefactorZip -DestinationPath $tempDir -Force

# Paths to refactored src and tests within the extracted archive
$refactoredSrcPath = Join-Path -Path $tempDir -ChildPath 'webscraper_refactor\src'
$refactoredTestsPath = Join-Path -Path $tempDir -ChildPath 'webscraper_refactor\tests'

# Verify required directories exist
if (-not (Test-Path -LiteralPath $refactoredSrcPath)) {
    Write-Error "No se encontró el directorio 'src' refactorizado en el zip."
    Pop-Location
    exit 1
}

# Copy refactored src files over the existing src directory
Copy-Item -Path (Join-Path $refactoredSrcPath '*') -Destination 'src' -Recurse -Force
Write-Host "Se han actualizado los archivos en el directorio 'src'."

# Copy refactored tests if present
if (Test-Path -LiteralPath $refactoredTestsPath) {
    # Ensure tests directory exists
    if (-not (Test-Path -LiteralPath 'tests')) {
        New-Item -ItemType Directory -Path 'tests' | Out-Null
    }
    Copy-Item -Path (Join-Path $refactoredTestsPath '*') -Destination 'tests' -Recurse -Force
    Write-Host "Se han actualizado los archivos en el directorio 'tests'."
}

Pop-Location
Write-Host "Actualización completada. Los archivos originales se encuentran respaldados en $backupDir. Ejecuta tus pruebas para confirmar que todo funciona correctamente."