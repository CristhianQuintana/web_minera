# Registro de hallazgos — Accesibilidad WCAG 2.1 AA (automatizado)

| Campo | Valor |
|---|---|
| Proyecto | WEB_MINERA |
| Herramienta | Playwright + axe-core (`@axe-core/playwright`) |
| Estándar | WCAG 2.1 A / AA (tags axe: wcag2a, wcag2aa, wcag21a, wcag21aa) |
| BASE_URL | `http://127.0.0.1:3000` |
| Sesión autenticada | No (páginas protegidas redirigen a `/login`) |

## Ejecución 1 (antes de corrección)

| Métrica | Valor |
|---|---|
| Páginas | 17 |
| Violaciones | **2** (critical) |
| Evidencia | `accessibility-report-BEFORE-FIX.*`, `console-run-BEFORE-FIX.txt`, `findings-register-BEFORE-FIX.json` |

### Hallazgos

| Página | Regla | Impacto | WCAG | Elemento | Corrección |
|---|---|---|---|---|---|
| `/alerts` → login | `select-name` | critical | 4.1.2 | `<select>` sin nombre accesible | Asegurar `aria-label` / label en `Select` |
| `/mass-balance` → login | `select-name` | critical | 4.1.2 | idem | idem |

## Corrección aplicada

Archivo: `frontend/src/shared/components/ui.tsx` — componente `Select`:

- Evitar que `{...props}` sobrescriba `aria-label`.
- Nombre accesible obligatorio (`label` / `aria-label` / `name` / fallback).
- `sr-only` cuando no hay label visible.

## Ejecución 2 (después de corrección)

| Métrica | Valor |
|---|---|
| Páginas | 17 |
| Violaciones | **0** |
| Evidencia | `accessibility-report.json/.html`, `console-run-AFTER-FIX.txt`, histórico `*-2026-11-08T14-16-43*` |

## Aviso metodológico

**Cero violaciones axe no declara cumplimiento WCAG 2.1 AA.**  
Falta validación manual: teclado, orden/foco visible, lector de pantalla, contraste, modales/menús, formularios con errores.  
Páginas autenticadas deben reevaluarse con `PLAYWRIGHT_STORAGE_STATE` (no versionar secretos).

## Capturas sugeridas (informe académico)

1. Terminal: `npm run audit:accessibility` (BEFORE / AFTER).
2. HTML: resumen general.
3. HTML: detalle violaciones (BEFORE-FIX).
4. JSON: resultados completos.
5. Segunda ejecución AFTER-FIX (0 violaciones + disclaimer).
