# Ejecuta carga k6 sobre WEB_MINERA e imprime el reporte en terminal.
# Uso:
#   .\performance\k6\run-load.ps1
#   .\performance\k6\run-load.ps1 -BaseUrl http://127.0.0.1:8000 -Profile smoke
#   .\performance\k6\run-load.ps1 -Token $env:TOKEN

param(
  [string]$BaseUrl = $(if ($env:BASE_URL) { $env:BASE_URL } else { "http://127.0.0.1:8000" }),
  [string]$Profile = $(if ($env:K6_PROFILE) { $env:K6_PROFILE } else { "load" }),
  [string]$Token = $(if ($env:TOKEN) { $env:TOKEN } else { "" }),
  [string]$Email = $(if ($env:K6_EMAIL) { $env:K6_EMAIL } else { "" }),
  [string]$Password = $(if ($env:K6_PASSWORD) { $env:K6_PASSWORD } else { "" })
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$K6 = Join-Path $Root "audit\web_minera\performance\k6\bin\k6-v0.54.0-windows-amd64\k6.exe"
$Script = Join-Path $Root "performance\k6\load-web-minera.js"
$OutDir = Join-Path $Root "reports\performance"

if (-not (Test-Path $K6)) {
  Write-Error "No se encontró k6.exe en $K6"
}
if (-not (Test-Path $Script)) {
  Write-Error "No se encontró script $Script"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "========================================================================"
Write-Host "WEB_MINERA — Ejecutando k6 ($Profile) contra $BaseUrl"
Write-Host "========================================================================"

$env:BASE_URL = $BaseUrl
$env:K6_PROFILE = $Profile
if ($Token) { $env:TOKEN = $Token }
if ($Email) { $env:K6_EMAIL = $Email }
if ($Password) { $env:K6_PASSWORD = $Password }

Push-Location $Root
try {
  & $K6 run $Script
  $code = $LASTEXITCODE
} finally {
  Pop-Location
}

Write-Host ""
Write-Host "Exit code k6: $code"
if (Test-Path (Join-Path $OutDir "k6-report.txt")) {
  Write-Host "Reporte también guardado en: reports\performance\k6-report.txt"
}
exit $code
