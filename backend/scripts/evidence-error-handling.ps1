# Evidencia terminal: errores controlados / persistencia / logging / recuperacion
$ErrorActionPreference = "Continue"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host ""
Write-Host ("=" * 72)
Write-Host "EVIDENCIA — Tratamiento de errores y operaciones fallidas (WEB_MINERA)"
Write-Host ("=" * 72)
Write-Host "1) Respuesta controlada ante solicitudes invalidas"
Write-Host "2) Excepciones en operaciones de persistencia"
Write-Host "3) Logging sin exposicion de informacion sensible"
Write-Host "4) Recuperacion / gestion controlada de operaciones fallidas"
Write-Host ("-" * 72)
Write-Host "Codigo:"
Write-Host "  - app/adapters/inbound/http/errors.py"
Write-Host "  - app/adapters/outbound/supabase/client.py"
Write-Host "  - app/infrastructure/logging/logger.py"
Write-Host "  - app/domain/exceptions/__init__.py"
Write-Host ("-" * 72)
Write-Host ""

.\.venv\Scripts\python.exe -m pytest tests/integration/test_error_handling_evidence.py -v --tb=short
$code = $LASTEXITCODE

Write-Host ""
Write-Host ("-" * 72)
if ($code -eq 0) {
  Write-Host "DICTAMEN: Evidencia OK — los 4 controles pasaron las pruebas."
} else {
  Write-Host "DICTAMEN: Fallaron pruebas (exit=$code)."
}
Write-Host ("=" * 72)
Write-Host ""
exit $code
