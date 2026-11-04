# Matriz de trazabilidad corregida — S11 complemento

Commit código: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## 1. Universo de RF aplicables a WEB_MINERA

| RF | Incremento | ¿Aplicable WEB? | Justificación |
|---|---|---|---|
| RF-01 Autenticación / sesión | I1 | **Sí** | Login web Supabase + gates de sesión |
| RF-02 Gestión lotes UI→API→DB | I1 | **Sí** | CRUD/consulta lotes en portal |
| RF-03 Validación FE+BE | I1 | **Sí** | Zod FE + Pydantic/reglas BE |
| RF-04 Geografía / coordenadas | I1 | **Sí (parcial alcance)** | Visualización lat/lon en detalle; captura GPS física = APP |
| RF-05 Evidencias (consulta web) | I1 | **Sí (alcance Decision B)** | Consulta URL firmada; upload físico = APP / N/A web |
| RF-06 Escaneo QR físico | I1 | **N/A** | Escaneo en dispositivo = APP_MINERA |
| RF-07 Aislamiento org / rol sobre lotes | I1 | **Sí** | RLS + autorización multi-tenant web |
| RF-08 Sync offline | I1 | **N/A** | Sync/offline = APP_MINERA |
| RF-09 Persistencia / consistencia | I1 | **Sí** | Persistencia vía API/DB consumida por web |
| RF-10 Control de acceso | I1 | **Sí** | PermissionGate + require() + JWT |
| RF-11 Detalle / timeline lote | I1 | **Sí** | UI detalle + timeline |
| RF-I2-01 Custodia | I2 | **Sí** | Flujo custodia web |
| RF-I2-02 Eventos transporte | I2 | **Sí** | transport_events API+UI |
| RF-I2-03 QR trazabilidad escaneo | I2 | **N/A** | Escaneo = APP_MINERA |
| RF-I2-04 Timeline trazabilidad | I2 | **Sí** | Timeline FE/API |

**Aplicables netos:** 12 (I1: 9 + I2: 3). **N/A:** RF-06, RF-08, RF-I2-03.

**Aprobados flujo funcional completo (E2E autenticado + negocio):** **0 / 12**.

## 2. Leyenda de tipos de prueba

| Tipo | Significado en esta matriz |
|---|---|
| Unit | pytest / vitest aislados |
| API | HTTP a endpoints (con o sin JWT) |
| Integración | isolation/arquitectura o suites que cruzan capas sin UI auth |
| E2E | Playwright UI |
| No ejecutado | Caso definido pero no corrido en S11 |
| Inspección código | Revisión estática / Decision doc; no prueba dinámica |

## 3. Matriz por RF (estado S11 complemento)

| RF | Estado | Unit | API | Integración | E2E ejecutado | E2E / prueba no ejecutada | Evidencia exacta (ver también 02_) |
|---|---|---|---|---|---|---|---|
| RF-01 | **Parcial** | — | Prod: 401 sin JWT / demo | — | Negativos + redirect sesión | Login OK, logout, expiración JWT | `03_RF01_RF02…`; `playwright_s11.txt` |
| RF-02 | **No ejecutado** (funcional) | Vitest schemas | Prod lots 401 sin auth (no crea lote) | — | — | Create/list/detail autenticado | `vitest_s11.txt`; código |
| RF-03 | **Parcial** | Vitest Zod + pytest validación | — | — | — | Request manipulado autenticado | `vitest_s11.txt`; `pytest_s11.txt` |
| RF-04 | **Parcial** | — | — | — | — | Mapa interactivo E2E | Inspección UI detalle (código) |
| RF-05 | **Parcial** | — | URL firmada en API (código) | — | — | Consulta/denegación auth | `audit/web_minera/evidence/RF-05/DECISION_ALCANCE.md` |
| RF-06 | **N/A** | — | — | — | — | — | Justificación APP |
| RF-07 | **No verificable / Pendiente** | Permisos unit | 401 sin JWT | — | — | RLS JWT org A vs B | `05_SEGURIDAD_RLS/…`; `04_SEGURIDAD_RLS_PENDIENTE.md` |
| RF-08 | **N/A** | — | — | — | — | — | Justificación APP |
| RF-09 | **Parcial** | pytest persistencia parcial | — | — | — | Consistencia UI/API/DB E2E | `pytest_s11.txt` |
| RF-10 | **Parcial** | — | 401 sin JWT | — | Redirect sin sesión | Matriz rol×acción E2E | probes + playwright redirect |
| RF-11 | **Parcial** | — | — | — | — | Timeline autenticado E2E | Código FE timeline |
| RF-I2-01 | **Parcial** | Zod/org unit | — | — | — | Custodia E2E auth | `pytest_s11.txt` / vitest |
| RF-I2-02 | **Parcial** | `test_transport_events` | — | — | — | Eventos E2E auth | `pytest_s11.txt` |
| RF-I2-03 | **N/A** | — | — | — | — | — | Justificación APP |
| RF-I2-04 | **Parcial** | — | — | — | — | Timeline E2E auth | Código FE |

## 4. Declaración
Ningún RF aplicable se marca **Aprobado**. El dictamen permanece **NO APTO**.
