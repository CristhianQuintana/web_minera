# Auditoría de accesibilidad WCAG 2.1 AA — WEB_MINERA

## Estructura

```text
WEB_MINERA/
├── scripts/accessibility-audit.mjs
├── reports/accessibility/
│   ├── accessibility-report.json
│   ├── accessibility-report.html
│   ├── accessibility-report-BEFORE-FIX.*
│   ├── findings-register.json
│   └── REGISTRO_HALLAZGOS_ACCESIBILIDAD.md
└── frontend/   # npm scripts + Playwright
```

## Ejecutar

```powershell
cd "c:\Users\USER\OneDrive\Documentos\Proyectos\web_minera\frontend"
# En otra terminal: npm run dev
$env:BASE_URL="http://127.0.0.1:3000"
npm run audit:accessibility
```

Páginas autenticadas (no versionar el JSON de sesión):

```powershell
$env:PLAYWRIGHT_STORAGE_STATE="playwright/.auth/user.json"
$env:BASE_URL="http://127.0.0.1:3000"
$env:AUDIT_PAGES="/dashboard,/lots,/transport,/receptions,/alerts,/custody,/weighings,/mass-balance"
npm run audit:accessibility
```

## Criterio

Cero violaciones automáticas **no** declara cumplimiento WCAG 2.1 AA.
