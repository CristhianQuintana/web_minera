# Hallazgos y riesgos — Auditoria S11

Commit: `﻿3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: ﻿fecha_iso=2026-11-03T23:31:00-05:00

| ID | Descripcion | Componente/RF | Evidencia | Severidad | Impacto | Causa | Correccion | Prueba cierre | Responsable | Fecha objetivo | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S11-H-001 | E2E autenticado no ejecutado | RF-01/02/11/I2 | playwright skips | Alta | No se acredita PMV2 funcional UI | Falta E2E_EMAIL/PASSWORD | Configurar secretos CI | Playwright auth | Dev | 2026-11-17 | Pendiente |
| S11-H-002 | RLS JWT multi-org no probado | RF-07/10 WEB-AUD-012 | seguridad_probes | Critica/Alta | Riesgo acceso cruzado no desmentido en vivo | Sin usuarios org A/B | Ejecutar matriz RLS | JWT dual-org | Dev/Sec | 2026-11-17 | Pendiente |
| S11-H-003 | Axe solo login | WEB-AUD-002 | axe_s11_resumen | Media | a11y incompleta | Sin sesion E2E | Axe autenticado | Axe dashboard+ | Dev | 2026-11-17 | Pendiente |
| S11-H-004 | k6 solo /health | WEB-AUD-003 | k6 LIMITACIONES | Media | Capacidad negocio no medida | Sin TOKEN/perfil | k6 con auth | k6 lots/custody | Dev | 2026-11-17 | Pendiente |
| S11-H-005 | Uptime/MTTR no medidos | WEB-AUD-004 | — | Media | SLO no demostrable | Sin monitoreo | Instrumentar | Serie temporal | Ops | 2026-12-01 | No verificable |
| S11-H-006 | npm 20 vulns (2 crit / 2 high) | SEC-WEB-01 | npm_audit_s11 | Alta | Supply chain | vitest/tinypool/zod/postcss | Actualizar o excepcion formal renovada | npm audit | Dev | 2026-11-17 | Pendiente |
| S11-H-007 | Commit exacto en Render No verificable | Deploy | smoke prod | Media | Drift posible codigo vs deploy | Sin API metadata version | Exponer /version o header | Smoke + SHA | Dev/Ops | 2026-11-17 | No verificable |
| S11-H-008 | Semgrep/Gitleaks no ejecutados | SAST | — | Media | Cobertura SAST incompleta | Tools ausentes | Instalar en CI | Reportes | Dev | 2026-11-17 | No ejecutado |
| S11-H-OK-01 | pip-audit limpio | deps | pip_audit_s11 | — | — | Remediacion previa | Mantener | pip-audit | Dev | — | Resuelto |
| S11-H-OK-02 | /docs deshabilitado prod | SEC-WEB-04 | smoke_prod | — | — | APP_ENV production | Mantener | HTTP 404 | Dev | — | Resuelto (prod smoke) |
| S11-H-OK-03 | Contaminacion dominio 0% | Arquitectura | domain_contamination | — | — | Hexagonal | Mantener | isolation | Dev | — | Resuelto |

## Riesgos — recomendacion del desarrollador
**No se recomienda aceptar formalmente** WEB-AUD-012 ni ausencia de E2E autenticado como cierre de aptitud productiva.
La autoridad competente debe decidir aceptacion. Esta auditoria **no copia** la aceptacion del acta PMV2 previa.
