# Registro de hallazgos — Auditoría accesibilidad WCAG 2.1 AA (WEB_MINERA)

| Campo | Valor |
|---|---|
| **Herramientas** | Playwright + @axe-core/playwright (axe-core) |
| **Script** | `scripts/accessibility-audit.mjs` |
| **BASE_URL** | `http://127.0.0.1:3000` |
| **Sesión autenticada** | No (rutas protegidas redirigen a `/login`; el DOM analizado es el visible) |
| **Aviso** | Cero violaciones automáticas **no** declara cumplimiento WCAG 2.1 AA. Falta validación manual (teclado, foco, lector de pantalla, contraste, modales). |

## Ejecución 1 — Antes de corrección

| Métrica | Valor |
|---|---|
| Fecha (UTC) | 2026-11-08T14:11:59Z (también histórico en raíz `*-BEFORE-FIX*`) |
| Páginas | 16–17 |
| Violaciones totales | **1–2** (`select-name`, impacto **critical**) |
| Evidencia | `accessibility-report-BEFORE-FIX.json` / `.html` |

### Hallazgo A11Y-001

| Campo | Contenido |
|---|---|
| **ID regla** | `select-name` |
| **Impacto** | critical |
| **WCAG** | 4.1.2 Name, Role, Value (`wcag412`, `wcag2a`) |
| **Descripción** | `<select>` sin nombre accesible |
| **Elemento** | `<select class="w-full rounded-xl border ...">` |
| **Selector** | `select` (filtro de estados en `ResourcePage` / componente `Select`) |
| **Esperado** | Label visible o `aria-label` / `aria-labelledby` |
| **Obtenido** | `<label>` vacío sin texto ni `aria-label` |
| **Corrección** | `Select` siempre expone `aria-label`; filtro con `label="Estado"` |
| **Estado** | **Corregido** |

## Ejecución 2 — Después de corrección

| Métrica | Valor |
|---|---|
| Fecha (UTC) | 2026-11-08T14:14:29.588Z |
| Páginas | **16** |
| Violaciones | **0** |
| Reglas aprobadas (suma) | **344** |
| Incomplete | **0** |
| Evidencia | `accessibility-report.json` / `.html` · histórico `accessibility-report-2026-11-08T14-14-29-588Z.*` |

## Archivos de evidencia (capturas académicas)

1. Terminal: ejecutar `npm run audit:accessibility` desde `frontend/`
2. HTML resumen: abrir `reports/accessibility/accessibility-report.html`
3. Detalle violaciones: HTML sección hallazgos / JSON `violations[]`
4. JSON completo: `accessibility-report.json`
5. Segunda corrida: comparar `*-BEFORE-FIX*` vs reporte actual

## Validación manual pendiente

- Navegación teclado completa
- Orden y visibilidad del foco
- Lector de pantalla básico
- Etiquetas/errores de formularios
- Contraste
- Modales y menús
