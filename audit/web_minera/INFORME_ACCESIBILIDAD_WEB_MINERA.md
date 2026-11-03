# Informe de accesibilidad — PMV2 WEB

Fecha: 2026-11-03

## Contraste
Tokens success-fg/warning-fg/error-fg aplicados a badges/toasts.
Ver accessibility/contrast/contrast-post-fix.txt

## Axe Core
- Herramienta: @axe-core/playwright
- Ruta: /login
- Resultado: **0 violaciones critical/serious**
- Evidencia: accessibility/axe/AXE-login_2026-11-03.txt + playwright stdout

## Limitacion
No se ejecuto Axe autenticado en dashboard/lots/custody (sin E2E credentials).
Dictamen WCAG AA completo de PMV2: **Parcial** (login OK; resto No verificable).
