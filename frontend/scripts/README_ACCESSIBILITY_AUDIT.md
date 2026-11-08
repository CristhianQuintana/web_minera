# Auditoría de accesibilidad — puente frontend

El script canónico y los reportes están en la raíz de WEB_MINERA:

- Script: `../scripts/accessibility-audit.mjs`
- Reportes: `../reports/accessibility/`
- Guía: `../scripts/README_ACCESSIBILITY_AUDIT.md`

```powershell
cd frontend
$env:BASE_URL="http://127.0.0.1:3000"
npm run audit:accessibility
```