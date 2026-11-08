# Reportes de accesibilidad — WEB_MINERA

Generados por `scripts/accessibility-audit.mjs` (Playwright + axe-core, WCAG 2.1 A/AA).

## Archivos

| Archivo | Contenido |
|---|---|
| `accessibility-report.json` | Última ejecución (completo) |
| `accessibility-report.html` | Última ejecución (legible) |
| `accessibility-report-<timestamp>.*` | Histórico por corrida |
| `findings-register.json` | Hallazgos aplanados (impacto, selector, HTML, WCAG) |

## Ejecución

```powershell
# Terminal 1 — app
cd frontend
npm run dev

# Terminal 2 — auditoría (páginas públicas + protegidas sin sesión redirigirán a login)
cd ..
$env:BASE_URL="http://127.0.0.1:3000"
npm run audit:accessibility
```

Autenticadas (no versionar `playwright/.auth/`):

```powershell
$env:PLAYWRIGHT_STORAGE_STATE="playwright/.auth/user.json"
$env:BASE_URL="http://127.0.0.1:3000"
$env:AUDIT_PAGES="/dashboard,/lots,/transport,/receptions,/alerts"
npm run audit:accessibility
```

## Aviso

Cero violaciones en axe **no** declara cumplimiento WCAG 2.1 AA. Complementar con pruebas manuales (teclado, foco, lector de pantalla, contraste, modales).
