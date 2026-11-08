# Evidencia — Auditoría accesibilidad WCAG 2.1 AA (WEB_MINERA)

## Cómo reproducir

```powershell
cd c:\Users\USER\OneDrive\Documentos\Proyectos\web_minera\frontend
npm run dev

# Otra terminal
cd c:\Users\USER\OneDrive\Documentos\Proyectos\web_minera
$env:BASE_URL="http://127.0.0.1:3000"
npm run audit:accessibility
```

Autenticadas (opcional):

```powershell
$env:PLAYWRIGHT_STORAGE_STATE="playwright/.auth/user.json"
$env:AUDIT_PAGES="/dashboard,/lots,/transport,/receptions,/alerts"
npm run audit:accessibility
```

## Artefactos

| Artefacto | Ruta |
|---|---|
| Script | `scripts/accessibility-audit.mjs` |
| npm | `npm run audit:accessibility` (raíz / frontend) |
| Reportes | `reports/accessibility/` |
| Hallazgos | `reports/accessibility/HALLAZGOS_ACCESIBILIDAD.md` |

## Resultado consolidado

- Ejecución inicial: **2 violaciones critical** (`select-name`).
- Tras corrección de `Select`: **0 violaciones** automáticas en 17 rutas.
- **No** se declara conformidad WCAG 2.1 AA solo por axe en verde.
