# Matriz funcional Incremento 1 — S11 (actualizada complemento)

Commit codigo: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha complemento: 2026-11-03T23:50:00-05:00

Fuente canónica ampliada: `../14_ENTREGA_COMPLEMENTARIA/01_MATRIZ_TRAZABILIDAD_CORREGIDA.md` y evidencias en `02_EVIDENCIAS_INDIVIDUALES_POR_RF.md`.

| RF | Aplicable | Estado S11 | Unit | API | E2E ejecutado | No ejecutado / pendiente | Evidencia exacta (ejemplos) |
|---|---|---|---|---|---|---|---|
| RF-01 | Si | **Parcial** | — | 401 sin JWT; smoke login 200 | Negativos + redirect | Login OK, logout, expiracion | `13_EVIDENCIAS/reportes_herramientas/playwright_s11.txt`; `14_…/03_RF01_RF02_AUTENTICACION.md` |
| RF-02 | Si | **No ejecutado** (funcional) | Vitest schemas | lots 401 (no valida RF-02) | — | Create/list/detail auth | `vitest_s11.txt`; smoke_prod |
| RF-03 | Si | **Parcial** | Vitest+Pytest | — | — | E2E manipulado auth | vitest_s11.txt; pytest_s11.txt |
| RF-04 | Si (coords); GPS N/A APP | **Parcial** | — | — | — | Mapa E2E | inspeccion codigo |
| RF-05 | Si (Decision B) | **Parcial** | — | — | — | Consulta auth | `audit/web_minera/evidence/RF-05/DECISION_ALCANCE.md` |
| RF-06 | **N/A** escaneo APP | N/A | — | — | — | — | Justificado APP_MINERA |
| RF-07 | Si | **Pendiente / No verificable** | permisos unit | 401 sin JWT | — | RLS JWT org A/B | `05_SEGURIDAD_RLS/seguridad_probes_…txt`; `14_…/04_SEGURIDAD_RLS_PENDIENTE.md` |
| RF-08 | **N/A** sync APP | N/A | — | — | — | — | Justificado |
| RF-09 | Si | **Parcial** | pytest | — | — | E2E UI/API/DB | pytest_s11.txt |
| RF-10 | Si | **Parcial** | — | 401 | redirect sin sesion | Matriz rol E2E | probes + playwright |
| RF-11 | Si | **Parcial** | — | — | — | Timeline E2E auth | codigo FE |

**Aprobados flujo completo:** 0 / 9 aplicables I1 (excl. N/A 06 y 08).
