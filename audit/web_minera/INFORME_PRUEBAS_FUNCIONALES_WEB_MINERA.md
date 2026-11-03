# Informe de pruebas funcionales — PMV2 WEB

Fecha: 2026-11-03

## Suites ejecutadas

| Suite | Resultado | Evidencia |
|---|---|---|
| Pytest | 52 passed | test-reports/pytest/ |
| Vitest | 22 passed | test-reports/vitest/ |
| Playwright cierre | 5 passed, 2 skipped | test-reports/playwright/playwright-cierre-stdout.txt |
| Axe login | 0 critical/serious | accessibility/axe/AXE-login_2026-11-03.txt |

## Casos GWT minimos

### CP-WEB-RF01-02 — Credenciales invalidas
- Given usuario en /login
- When ingresa correo/clave incorrectos
- Then permanece en login
- Estado: **Aprobado** (Playwright)

### CP-WEB-RF01-ruta — Sin sesion
- Given sin token
- When visita /lots o /dashboard
- Then redirige a /login
- Estado: **Aprobado**

### CP-WEB-RF01-01 — Login valido
- Estado: **No verificable** (falta E2E_EMAIL/PASSWORD)

### RF-02..I2-04 flujos autenticados
- Estado: **Parcial / No verificable E2E** — implementados en codigo + unit; E2E autenticado pendiente de secretos

### RF-05
- Decision B aprobada en evidence/RF-05/DECISION_ALCANCE.md
