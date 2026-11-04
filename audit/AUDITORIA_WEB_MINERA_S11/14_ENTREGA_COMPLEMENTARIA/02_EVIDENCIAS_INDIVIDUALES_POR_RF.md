# Evidencias individuales por RF — S11 complemento

Commit: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

Regla: cada requisito lista **archivos exactos** (no solo carpetas). Si no hay prueba, se declara pendiente.

## RF-01 Autenticación
| Qué | Archivo exacto | Resultado |
|---|---|---|
| E2E credenciales incorrectas | `frontend/tests/e2e/auth-and-lots.spec.ts` (CP-W02) | Pass |
| E2E credenciales inválidas PMV2 | `frontend/tests/e2e/pmv2-public.spec.ts` (CP-WEB-RF01-02) | Pass |
| E2E redirect sin sesión | `frontend/tests/e2e/auth-and-lots.spec.ts`; `frontend/tests/e2e/pmv2-public.spec.ts` | Pass |
| Log Playwright S11 | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/playwright_s11.txt` | 5 passed / 2 skipped |
| Smoke prod login page | `audit/AUDITORIA_WEB_MINERA_S11/09_PRODUCCION_CONFIABILIDAD/smoke_prod_2026-11-03.txt` | HTTP 200 página |
| API sin JWT | `audit/AUDITORIA_WEB_MINERA_S11/05_SEGURIDAD_RLS/seguridad_probes_sin_jwt_usuario_2026-11-03.txt` | HTTP 401 |
| Aclaración alcance | `audit/AUDITORIA_WEB_MINERA_S11/14_ENTREGA_COMPLEMENTARIA/03_RF01_RF02_AUTENTICACION.md` | — |
| **Pendiente** CP-W01 login OK | mismo `auth-and-lots.spec.ts` | **skipped** (sin E2E_EMAIL/PASSWORD) |
| **Pendiente** CP-W13 logout | mismo spec | **skipped** |
| **Pendiente** expiración/refresh JWT | — | **No ejecutado** |

## RF-02 Lotes
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Unit schemas recursos | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/vitest_s11.txt` | 22 passed (suite) |
| Prod GET lots sin auth | `audit/AUDITORIA_WEB_MINERA_S11/09_PRODUCCION_CONFIABILIDAD/smoke_prod_2026-11-03.txt` | 401 (no valida create/list auth) |
| **Pendiente** E2E create/list/detail | `frontend/tests/e2e/auth-and-lots.spec.ts` (requiere sesión) | **No ejecutado** |

## RF-03 Validación
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Vitest | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/vitest_s11.txt` | Pass suite |
| Pytest | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/pytest_s11.txt` | 52 passed |
| **Pendiente** E2E manipulación autenticada | — | **No ejecutado** |

## RF-04 Geografía
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Inspección código UI detalle | código FE detalle lote (lat/lon) | Inspección; sin log E2E dedicado |
| **Pendiente** mapa E2E | — | **No ejecutado** |

## RF-05 Evidencias
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Decision B alcance | `audit/web_minera/evidence/RF-05/DECISION_ALCANCE.md` | Documentado |
| **Pendiente** consulta/denegación auth | — | **No ejecutado** |

## RF-06 / RF-08 / RF-I2-03
| RF | Justificación N/A | Archivo |
|---|---|---|
| RF-06 | Escaneo QR físico APP | `01_MATRIZ_TRAZABILIDAD_CORREGIDA.md` §1 |
| RF-08 | Sync offline APP | idem |
| RF-I2-03 | Escaneo trazabilidad APP | idem |

## RF-07 / RF-10 Seguridad acceso
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Probes sin JWT usuario | `audit/AUDITORIA_WEB_MINERA_S11/05_SEGURIDAD_RLS/seguridad_probes_sin_jwt_usuario_2026-11-03.txt` | 401 |
| Resumen seguridad | `audit/AUDITORIA_WEB_MINERA_S11/05_SEGURIDAD_RLS/RESUMEN_SEGURIDAD_S11.md` | Pendiente RLS vivo |
| Declaración RLS pendiente | `audit/AUDITORIA_WEB_MINERA_S11/14_ENTREGA_COMPLEMENTARIA/04_SEGURIDAD_RLS_PENDIENTE.md` | Pendiente |
| Redirect sin sesión | `playwright_s11.txt` | Pass |
| **Pendiente** JWT org A/B + roles | — | **No ejecutado / No verificable** |

## RF-09 Persistencia
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Pytest | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/pytest_s11.txt` | Pass suite |
| **Pendiente** E2E UI/API/DB | — | **No ejecutado** |

## RF-11 / RF-I2-04 Timeline
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Matriz I1/I2 | `audit/AUDITORIA_WEB_MINERA_S11/03_FUNCIONAL_I1/MATRIZ_RF_I1.md`; `04_FUNCIONAL_I2/MATRIZ_RF_I2.md` | Parcial código |
| **Pendiente** E2E autenticado | — | **No ejecutado** |

## RF-I2-01 Custodia / RF-I2-02 Transporte
| Qué | Archivo exacto | Resultado |
|---|---|---|
| Pytest (incl. transport_events) | `audit/AUDITORIA_WEB_MINERA_S11/13_EVIDENCIAS/reportes_herramientas/pytest_s11.txt` | Pass |
| Vitest Zod custodia | `vitest_s11.txt` | Pass suite |
| **Pendiente** E2E auth | — | **No ejecutado** |

## Transversales
| Tema | Archivos exactos |
|---|---|
| Arquitectura | `02_ARQUITECTURA/backend/domain_contamination_s11.txt`; `02_ARQUITECTURA/backend/isolation_s11.txt`; `02_ARQUITECTURA/RESUMEN_ARQUITECTURA_S11.md` |
| npm 20 vulns | `14_ENTREGA_COMPLEMENTARIA/npm/VULNERABILIDADES_DETALLE.md`; `…/VULNERABILIDADES_DETALLE.csv`; `…/npm_audit_full.json`; `06_DEPENDENCIAS_SAST_SECRETOS/npm_audit_s11.txt` |
| pip-audit | `06_DEPENDENCIAS_SAST_SECRETOS/pip_audit_s11.txt` |
| Axe complemento | `14_ENTREGA_COMPLEMENTARIA/axe/axe_login.json`; `axe_forgot_password.json`; `axe_activate_account.json`; `axe_forbidden.json`; `axe_dashboard_AUTH_PENDIENTE.txt`; `playwright_axe_complemento.txt` |
| k6 infra | `08_RENDIMIENTO_K6/k6_s11_health_only_stdout.txt`; `08_RENDIMIENTO_K6/LIMITACIONES.txt`; `08_RENDIMIENTO_K6/k6_health_prod.js` |
| Plan carga negocio | `14_ENTREGA_COMPLEMENTARIA/06_RENDIMIENTO_PLAN_CARGA.md` |
| Uptime/MTTR | `14_ENTREGA_COMPLEMENTARIA/07_CONFIABILIDAD_UPTIME_MTTR.md` |
| GQM/S9 | `14_ENTREGA_COMPLEMENTARIA/08_GQM_S9_TRAZABILIDAD.md`; `Document/actividad-3-matriz-metricas-gq-web.md`; `Document/actividad-4-evaluacion-arquitectura-hexagonal.md` |
| Deploy SHA | `14_ENTREGA_COMPLEMENTARIA/09_DESPLIEGUE_SHA_RENDER.md`; `09_PRODUCCION_CONFIABILIDAD/smoke_prod_2026-11-03.txt` |
| Typecheck | `13_EVIDENCIAS/reportes_herramientas/typecheck_s11.txt` |
