# EZ-push: crea rama, commit, push, PR y auto-merge
param([string]$Message = "chore: actualizaciones")
$ErrorActionPreference="Stop"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Falta git" }
$HasGH = $true; try { Get-Command gh -ErrorAction Stop | Out-Null } catch { $HasGH = $false }

$porcelain = git status --porcelain
if (-not $porcelain) { Write-Host "ℹ No hay cambios que commitear." -ForegroundColor Yellow; exit 0 }

$branchDefault = (git symbolic-ref --short refs/remotes/origin/HEAD 2>$null) -replace '^origin/',''
if (-not $branchDefault) { $branchDefault = "main" }
$workBranch = "feat/ez-" + (Get-Date -Format "yyyyMMddHHmmss")

git checkout -b $workBranch | Out-Null
git add . | Out-Null
git commit -m $Message | Out-Null
git push -u origin $workBranch | Out-Null
Write-Host "✔ Push -> $workBranch" -ForegroundColor Green

if ($HasGH) {
  try {
    gh pr create --title $Message --body "Auto PR (EZ-push). " --base $branchDefault --head $workBranch --fill 2>$null
    gh pr edit --add-label "ci" --add-label "status/in-review" 2>$null
    gh pr merge --auto --merge 2>$null
    Write-Host "✔ PR abierto y auto-merge habilitado." -ForegroundColor Green
  } catch { Write-Host "ℹ No se pudo abrir/auto-merge PR. Abre y mergea manualmente." -ForegroundColor Yellow }
} else {
  Write-Host "ℹ 'gh' no disponible. Abre PR manualmente desde $workBranch." -ForegroundColor Yellow
}