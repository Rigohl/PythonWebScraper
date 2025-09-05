<#!
.SYNOPSIS
  Setup workspace recommended extensions and profile for VS Code Insiders with Copilot optimization.
#>
param(
  [switch]$Force
)

Write-Host "== VS Code Insiders Copilot Setup ==" -ForegroundColor Cyan

# Detect code insiders cli
$code = (Get-Command code-insiders -ErrorAction SilentlyContinue)
if (-not $code) {
  Write-Warning "code-insiders CLI not found in PATH. Install VS Code Insiders and ensure 'Add to PATH' option was selected."
  exit 1
}

$extensions = @(
  'GitHub.copilot',
  'GitHub.copilot-chat',
  'ms-python.python',
  'ms-python.vscode-pylance',
  'eamodio.gitlens',
  'ms-vscode.powershell',
  'DavidAnson.vscode-markdownlint',
  'redhat.vscode-yaml'
)

foreach ($ext in $extensions) {
  Write-Host "Installing/Ensuring $ext" -ForegroundColor DarkGray
  code-insiders --install-extension $ext --force
}

# Create a profile (Insiders) referencing workspace instructions
$profileName = "Copilot-Advanced"
Write-Host "Creating/Updating profile: $profileName" -ForegroundColor DarkCyan

$profileDir = Join-Path $env:APPDATA "Code - Insiders/User/profiles/$profileName"
if (-not (Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir | Out-Null }

# Minimal profile settings layering
$profileSettings = @'{
  "workbench.startupEditor": "none",
  "workbench.experimental.chatAgentMode": true,
  "github.copilot.inlineSuggest.enable": true
}'@
Set-Content -Path (Join-Path $profileDir 'settings.json') -Value $profileSettings -Encoding UTF8

Write-Host "Done. Launch with: code-insiders --profile '$profileName' ." -ForegroundColor Green
