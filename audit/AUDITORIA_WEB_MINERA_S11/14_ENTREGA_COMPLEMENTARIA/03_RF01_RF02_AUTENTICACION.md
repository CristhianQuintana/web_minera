# RF-01 y RF-02 — Autenticación: ejecutado vs pendiente

Commit: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## Principio
Una respuesta HTTP **200** (página login) o **401** (API sin token / credencial inválida) **no** constituye validación completa de autenticación ni de autorización de negocio.

## RF-01 — Qué se ejecutó realmente

| ID / caso | Tipo | Evidencia | Resultado | ¿Auth completa? |
|---|---|---|---|---|
| CP-W02 credenciales incorrectas | E2E | `playwright_s11.txt` + `auth-and-lots.spec.ts` | Pass | Parcial (rechazo) |
| CP-WEB-RF01-02 inválidas | E2E | `pmv2-public.spec.ts` | Pass | Parcial (rechazo) |
| Sin sesión → redirect login | E2E | ambos specs | Pass | Parcial (guard de ruta) |
| GET /api/v1/lots sin JWT | API prod | `seguridad_probes_sin_jwt_usuario_2026-11-03.txt` | 401 | Solo ausencia de token |
| Login demo-like prod | API/UI smoke | `smoke_prod_2026-11-03.txt` | 401 | Rechazo; no prueba login válido |
| Página `/login` prod | Smoke | `smoke_prod_2026-11-03.txt` | 200 | Solo disponibilidad de UI |

## RF-01 — Pendiente (obligatorio para Aprobado)

| Caso | Estado |
|---|---|
| CP-W01 login correcto → dashboard | **skipped / No ejecutado** (faltan `E2E_EMAIL` / `E2E_PASSWORD`) |
| CP-W13 logout → login | **skipped / No ejecutado** |
| Expiración de sesión / refresh JWT | **No ejecutado** |
| Sesión concurrente / invalidación | **No ejecutado** |

## RF-02 — Qué se ejecutó realmente

| Caso | Tipo | Resultado | ¿Valida RF-02? |
|---|---|---|---|
| Vitest schemas de recursos/lotes | Unit | Pass (suite) | Solo contrato FE |
| GET lots sin JWT → 401 | API | Pass rechazo | **No** (no crea ni lista con usuario) |

## RF-02 — Pendiente

| Caso | Estado |
|---|---|
| Login + crear lote + ver en listado | **No ejecutado** |
| Consultar detalle persistido | **No ejecutado** |
| Validar fila en DB / API coherente con UI | **No ejecutado** |

## Dictamen parcial
- RF-01: **Parcial** (solo negativos/guards).
- RF-02: **No ejecutado** a nivel funcional autenticado.
- Ninguno puede marcarse **Aprobado** con la evidencia actual.
