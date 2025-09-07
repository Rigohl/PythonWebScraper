$ErrorActionPreference="Stop"

# == Rutas base ==
$desk = [Environment]::GetFolderPath("Desktop")
$ROOT = Join-Path $desk "DevNuclear"
$PRO  = Join-Path $ROOT "profiles"
$WS   = Join-Path $ROOT "workspace-plantilla"
$DOCS = Join-Path $ROOT "docs"
$SNP  = Join-Path $ROOT "snippets"
$SCR  = Join-Path $ROOT "scripts"
New-Item -ItemType Directory -Force -Path $ROOT,$PRO,$WS,$DOCS,$SNP,$SCR | Out-Null

function Save-Json([object]$o,[string]$p){ ($o | ConvertTo-Json -Depth 25) | Set-Content -Path $p -Encoding utf8 }

# == Snippets globales (prompts IA) ==
$snips = @{
  "SPEC"=@{prefix="pp-spec";description="Especificación antes de código";body=@(
    "Actúa como Tech Lead. Especifica objetivo, entradas/salidas, contratos, errores, rendimiento, seguridad. Lista de funciones y firmas. No implementes aún.","","$TM_SELECTED_TEXT")};
  "TDD-TESTGEN"=@{prefix="pp-testgen";description="Tests primero (TDD)";body=@(
    "Genera tests unitarios (pytest/jest) con casos borde, fixtures, mocks y parametrización para el siguiente código. No implementes.","","$TM_SELECTED_TEXT")};
  "REVIEW"=@{prefix="pp-review";description="Revisión estricta de PR";body=@(
    "Code-review: lógica, rendimiento, seguridad, errores, legibilidad; entrega diff mínimo de cambios.","","$TM_SELECTED_TEXT")};
  "DOCSTR"=@{prefix="pp-doc";description="Docstrings Google/NumPy";body=@(
    "Docstrings Google/NumPy + ejemplo de uso y notas de errores comunes.","","$TM_SELECTED_TEXT")}
}
Save-Json $snips (Join-Path $SNP "prompts-global.code-snippets")

# == Extensiones base que recomiendo (no instala aún; se sugieren por perfil) ==
$extBase = @("usernamehw.errorlens","EditorConfig.EditorConfig","yzhang.markdown-all-in-one","PKief.material-icon-theme")

# ---------- Perfiles ----------
# Perfil: Python • Focus
$pySettings = [ordered]@{
  "workbench.locale"="es"; "telemetry.telemetryLevel"="off"; "workbench.iconTheme"="material-icon-theme";
  "editor.wordWrap"="on"; "editor.minimap.enabled"=$false; "editor.formatOnSave"=$true; "editor.formatOnPaste"=$true; "editor.formatOnType"=$true;
  "files.insertFinalNewline"=$true; "files.encoding"="utf8"; "files.autoSave"="onWindowChange";
  "errorLens.enabled"=$true; "errorLens.gutterIconsEnabled"=$true;
  "python.languageServer"="Pylance"; "python.analysis.autoSearchPaths"=$true; "python.formatting.provider"="black"; "python.testing.unittestEnabled"=$true;
  "ruff.enable"=$true; "isort.importStrategy"="fromEnvironment";
  "[python]"=@{"editor.defaultFormatter"="ms-python.black-formatter"; "editor.formatOnSave"=$true};
  "editor.codeActionsOnSave"=@{ "source.fixAll"="explicit"; "source.organizeImports"="explicit" }
}
$pyExt = $extBase + @("ms-python.python","ms-python.black-formatter","charliermarsh.ruff","ms-python.isort")
$profilePy = [ordered]@{
  "name"="Python • Focus"; "settings"=$pySettings;
  "extensions"=@{ "recommendations"=$pyExt };
  "snippets"=@{ "global"=(Get-Content (Join-Path $SNP "prompts-global.code-snippets") -Raw | ConvertFrom-Json) };
  "keybindings"=@(
    @{key="ctrl+alt+o";command="workbench.action.chat.open"},
    @{key="ctrl+alt+s";command="editor.action.insertSnippet";args=@{name="SPEC"}},
    @{key="ctrl+alt+t";command="editor.action.insertSnippet";args=@{name="TDD-TESTGEN"}},
    @{key="ctrl+alt+r";command="editor.action.insertSnippet";args=@{name="REVIEW"}},
    @{key="ctrl+alt+d";command="editor.action.insertSnippet";args=@{name="DOCSTR"}}
  )
}
Save-Json $profilePy (Join-Path $PRO "profile-python.code-profile")

# Perfil: Web • TDD
$webSettings = [ordered]@{
  "workbench.locale"="es"; "telemetry.telemetryLevel"="off"; "errorLens.enabled"=$true;
  "editor.formatOnSave"=$true;
  "[json]"=@{"editor.defaultFormatter"="esbenp.prettier-vscode"};
  "[jsonc]"=@{"editor.defaultFormatter"="esbenp.prettier-vscode"};
  "[typescript]"=@{"editor.defaultFormatter"="esbenp.prettier-vscode"};
  "[javascript]"=@{"editor.defaultFormatter"="esbenp.prettier-vscode"};
  "eslint.validate"=@("javascript","javascriptreact","typescript","typescriptreact")
}
$webExt = $extBase + @("dbaeumer.vscode-eslint","esbenp.prettier-vscode","ms-vscode.vscode-typescript-next")
$profileWeb = [ordered]@{
  "name"="Web • TDD"; "settings"=$webSettings; "extensions"=@{ "recommendations"=$webExt };
  "snippets"=@{ "global"=(Get-Content (Join-Path $SNP "prompts-global.code-snippets") -Raw | ConvertFrom-Json) };
  "keybindings"=@(
    @{key="ctrl+alt+o";command="workbench.action.chat.open"},
    @{key="ctrl+alt+t";command="editor.action.insertSnippet";args=@{name="TDD-TESTGEN"}}
  )
}
Save-Json $profileWeb (Join-Path $PRO "profile-web.code-profile")

# Perfil: Review • QA (Copilot + Gemini)
$revSettings = [ordered]@{
  "workbench.locale"="es"; "telemetry.telemetryLevel"="off"; "errorLens.enabled"=$true; "errorLens.gutterIconsEnabled"=$true;
  "github.copilot.enable"=@{"*"=$true;"markdown"=$true;"plaintext"=$false};
  "github.copilot.inlineSuggest.enable"=$true; "github.copilot.nextEditSuggestions.enabled"=$true;
  "github.copilot.editor.enableCodeActions"=$true; "github.copilot.chat.enable"=$true;
  "geminicodeassist.inlineSuggestions.enableAutoList"=$true; "geminicodeassist.codeActions.enable"=$true;
  "geminicodeassist.recitation.maxCitedLength"=0
}
$revExt = $extBase + @("GitHub.copilot","GitHub.copilot-chat","google.geminicodeassist","eamodio.gitlens")
$profileRev = [ordered]@{
  "name"="Review • QA (Copilot + Gemini)"; "settings"=$revSettings; "extensions"=@{"recommendations"=$revExt};
  "snippets"=@{ "global"=(Get-Content (Join-Path $SNP "prompts-global.code-snippets") -Raw | ConvertFrom-Json) };
  "keybindings"=@(
    @{key="ctrl+alt+o";command="workbench.action.chat.open"},
    @{key="ctrl+alt+r";command="editor.action.insertSnippet";args=@{name="REVIEW"}}
  )
}
Save-Json $profileRev (Join-Path $PRO "profile-review.code-profile")

# Perfil: DevOps
$devopsExt = $extBase + @("ms-azuretools.vscode-docker","redhat.vscode-yaml","ms-kubernetes-tools.vscode-kubernetes-tools")
$devopsSettings = [ordered]@{
  "workbench.locale"="es"; "telemetry.telemetryLevel"="off"; "errorLens.enabled"=$true;
  "[yaml]"=@{"editor.defaultFormatter"="redhat.vscode-yaml"}
}
$profileDevOps = [ordered]@{
  "name"="DevOps"; "settings"=$devopsSettings; "extensions"=@{"recommendations"=$devopsExt};
  "snippets"=@{ "global"=(Get-Content (Join-Path $SNP "prompts-global.code-snippets") -Raw | ConvertFrom-Json) }
}
Save-Json $profileDevOps (Join-Path $PRO "profile-devops.code-profile")

# Perfil: Data / ML (ligero)
$mlExt = $extBase + @("ms-toolsai.jupyter","ms-toolsai.jupyter-keymap","ms-toolsai.jupyter-renderers","ms-python.vscode-pylance")
$mlSettings = [ordered]@{
  "workbench.locale"="es"; "telemetry.telemetryLevel"="off"; "errorLens.enabled"=$true;
  "jupyter.askForKernelRestart"="never"
}
$profileML = [ordered]@{
  "name"="Data • ML (ligero)"; "settings"=$mlSettings; "extensions"=@{"recommendations"=$mlExt};
  "snippets"=@{ "global"=(Get-Content (Join-Path $SNP "prompts-global.code-snippets") -Raw | ConvertFrom-Json) }
}
Save-Json $profileML (Join-Path $PRO "profile-ml.code-profile")

# ---------- Workspace plantilla (tasks/launch/settings) ----------
New-Item -ItemType Directory -Force -Path (Join-Path $WS ".vscode") | Out-Null

$wsSettings = [ordered]@{
  "files.exclude"=@{"**/.git"=$true;"**/.venv"=$true;"**/node_modules"=$true;"**/dist"=$true;"**/build"=$true};
  "search.exclude"=@{"**/.git"=$true;"**/.venv"=$true;"**/node_modules"=$true;"**/dist"=$true;"**/build"=$true};
  "files.watcherExclude"=@{"**/.git/**"=$true;"**/.venv/**"=$true;"**/node_modules/**"=$true;"**/dist/**"=$true;"**/build/**"=$true};
  "git.scanRepositories"=$false; "git.autoRepositoryDetection"="openEditors"; "explorer.autoReveal"=$false
}
Save-Json $wsSettings (Join-Path $WS ".vscode\settings.json")

$tasks = [ordered]@{
  "version"="2.0.0";
  "tasks"=@(
    @{label="python:black";type="shell";command=".\\.venv\\Scripts\\black.exe";args=@(".");problemMatcher=@()},
    @{label="python:ruff"; type="shell";command=".\\.venv\\Scripts\\ruff.exe"; args=@("check",".");problemMatcher=@()},
    @{label="python:pytest";type="shell";command=".\\.venv\\Scripts\\pytest.exe";args=@("-q","--maxfail=1");problemMatcher="@pytest"},
    @{label="python:qa-all";type="shell";command="pwsh";args=@("-NoProfile","-ExecutionPolicy","Bypass","-File",".vscode\\qa-run.ps1");dependsOn=@("python:black","python:ruff");problemMatcher=@()}
  )
}
Save-Json $tasks (Join-Path $WS ".vscode\tasks.json")

$qaRun = @'
param()
$ErrorActionPreference="SilentlyContinue"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$out = Join-Path (Get-Location) "qa-report-$ts.md"
$pytest = ".\.venv\Scripts\pytest.exe"
if (!(Test-Path $pytest)) { Write-Host "⚠ No hay venv/pytest. Crea venv e instala pytest." ; exit 0 }
$txt = & $pytest -q 2>&1
$failed = ($LASTEXITCODE -ne 0)
$md=@("# QA Report $ts","","## Resultado", ($failed ? "**❌ Fallos**" : "**✅ Todo OK**"),"","## Pytest salida","```",$txt,"```")
$md -join "`n" | Set-Content -Path $out -Encoding utf8
try { & code-insiders $out } catch { Start-Process $out }
'@
$qaRun | Set-Content -Path (Join-Path $WS ".vscode\qa-run.ps1") -Encoding utf8

$launch = [ordered]@{
  "version"="0.2.0";
  "configurations"=@(
    @{name="Python: archivo actual";type="python";request="launch";program="${file}";console="integratedTerminal"},
    @{name="Node: archivo actual";type="node";request="launch";program="${file}"}
  )
}
Save-Json $launch (Join-Path $WS ".vscode\launch.json")

# ---------- Scripts útiles ----------
# 1) Lanzadores por perfil
'param($Path=".") ; & code-insiders --profile "Python • Focus" $Path' |
  Set-Content -Path (Join-Path $SCR "Open-PythonProfile.ps1") -Encoding utf8
'param($Path=".") ; & code-insiders --profile "Web • TDD" $Path' |
  Set-Content -Path (Join-Path $SCR "Open-WebProfile.ps1") -Encoding utf8
'param($Path=".") ; & code-insiders --profile "Review • QA (Copilot + Gemini)" $Path' |
  Set-Content -Path (Join-Path $SCR "Open-ReviewProfile.ps1") -Encoding utf8
@"
param([string]\$Profile,[string]\$Path=".")
if([string]::IsNullOrWhiteSpace(\$Profile)){
  Write-Host "Perfiles: 'Python • Focus' | 'Web • TDD' | 'Review • QA (Copilot + Gemini)' | 'DevOps' | 'Data • ML (ligero)'" ; exit 1
}
& code-insiders --profile \$Profile \$Path
"@ | Set-Content -Path (Join-Path $SCR "Open-Profile.ps1") -Encoding utf8

# 2) Español permanente (opcional) — SOLO añade locale en argv.json
$setES = @'
$UserDir = Join-Path $env:APPDATA "Code - Insiders\User"
$Argv    = Join-Path $UserDir "argv.json"
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
try { $o = Get-Content $Argv -Raw | ConvertFrom-Json -ErrorAction Stop } catch { $o=@{} }
$o.locale = "es"
($o | ConvertTo-Json -Depth 5) | Set-Content -Path $Argv -Encoding utf8
Write-Host "✔ Idioma español fijado en argv.json"
'@
$setES | Set-Content -Path (Join-Path $SCR "Set-VSCodeSpanish.ps1") -Encoding utf8

# 3) Hook auto-push (opcional) — ejecútalo dentro del repo donde lo quieras
$hook = @'
$ErrorActionPreference="Stop"
$repo = (git rev-parse --show-toplevel) 2>$null
if(-not $repo){ Write-Host "⚠ No estás dentro de un repo Git." ; exit 0 }
$hooks = Join-Path $repo ".git\hooks"; New-Item -ItemType Directory -Force -Path $hooks | Out-Null
$pc = Join-Path $hooks "post-commit"
@"
#!/usr/bin/env bash
set -e
remote=$(git remote 2>/dev/null | head -n1)
[ -z "\$remote" ] && exit 0
branch=$(git rev-parse --abbrev-ref HEAD)
if git rev-parse --symbolic-full-name --abbrev-ref @{u} >/dev/null 2>&1; then
  git push
else
  git push -u "\$remote" "\$branch" || true
fi
"@ | Set-Content -Path $pc -Encoding ascii
git update-index --add --chmod=+x ".git/hooks/post-commit" 2>$null
Write-Host "✔ Hook post-commit creado (auto-push activo): $pc"
'@
$hook | Set-Content -Path (Join-Path $SCR "Enable-AutoPush.ps1") -Encoding utf8

# ---------- README ----------
$readme = @"
# DevNuclear — Arranque rápido

## 1) Importar perfiles (1 minuto)
En VS Code Insiders: **Perfil → Profiles: Import Profile…**
- `profiles\profile-python.code-profile\`  → Python • Focus
- `profiles\profile-web.code-profile\`     → Web • TDD
- `profiles\profile-review.code-profile\`  → Review • QA (Copilot + Gemini)
- `profiles\profile-devops.code-profile\`  → DevOps
- `profiles\profile-ml.code-profile\`      → Data • ML (ligero)

> Sugerencia: al importar, VS Code te propondrá instalar las extensiones recomendadas del perfil.

## 2) Abrir con un perfil (PowerShell)
- `.\scripts\Open-Profile.ps1 -Profile "Python • Focus" -Path "C:\ruta\miProyecto"\`
- o usa los atajos: `Open-PythonProfile.ps1`, `Open-WebProfile.ps1`, `Open-ReviewProfile.ps1`.

## 3) Workspace plantilla (QA encadenado)
- Abre carpeta: `workspace-plantilla`.
- Crea venv e instala QA básico:
  `py -3.12 -m venv .venv && . .\.venv\Scripts\Activate.ps1 && pip install black ruff pytest`
- Ejecuta `Ctrl+Shift+B` → **python:qa-all** → verás `qa-report-YYYYMMDD-HHMMSS.md`.

## 4) Español permanente (opcional)
- Ejecuta `.\scripts\Set-VSCodeSpanish.ps1` (solo añade `locale: es` a `argv.json`, no toca tus settings).

## 5) Auto-push a GitHub (opcional, por repo)
- En el directorio de tu repo: `.\scripts\Enable-AutoPush.ps1` → crea hook `post-commit` que empuja al remoto.

## 6) Snippets de prompts (Copilot/Gemini)
- Están en `snippets/prompts-global.code-snippets`. Atajos:
  - Chat: **Ctrl+Alt+O**
  - SPEC: **Ctrl+Alt+S**
  - TESTGEN: **Ctrl+Alt+T**
  - REVIEW: **Ctrl+Alt+R**
  - DOCSTR: **Ctrl+Alt+D**

## Consejos rápidos
- Mantén tus proyectos dentro de una carpeta limpia (evita abrir `C:\Users\...\` completo) → acelera IA y búsqueda.
- En Copilot/Gemini: pega SPEC → TESTGEN → IMPLEMENT → REVIEW para ciclos muy rápidos y controlados.
"@
$readme | Set-Content -Path (Join-Path $ROOT "README.md") -Encoding utf8

Write-Host "✔ Listo. Carpeta creada:" -ForegroundColor Green
Write-Host "  $ROOT" -ForegroundColor Cyan
Write-Host "Sigue el README para importar perfiles y correr QA. 🚀"
 ESTO CON LA B Y A
