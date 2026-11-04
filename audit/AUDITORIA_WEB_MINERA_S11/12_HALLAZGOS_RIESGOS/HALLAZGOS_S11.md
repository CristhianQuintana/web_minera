# Hallazgos y riesgos — Auditoria S11 (post-complemento)

Commit codigo: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha complemento: 2026-11-03T23:50:00-05:00

| ID | Descripcion | Componente/RF | Evidencia | Severidad | Impacto | Causa | Correccion | Prueba cierre | Responsable | Fecha objetivo | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S11-H-001 | E2E autenticado no ejecutado (login OK/logout/RF-02+) | RF-01/02/11/I2 | playwright_s11.txt (2 skipped); 03_RF01_RF02 | Alta | No se acredita cierre funcional UI | Falta E2E_EMAIL/PASSWORD | Configurar secretos CI | Playwright auth | Dev | 2026-11-17 | Pendiente |
| S11-H-002 | RLS JWT multi-org no probado | RF-07/10 WEB-AUD-012 | 04_SEGURIDAD_RLS_PENDIENTE.md | Critica/Alta | Aislamiento org no demostrado en vivo | Sin usuarios org A/B | Ejecutar matriz RLS | JWT dual-org | Dev/Sec | 2026-11-17 | Pendiente |
| S11-H-003 | Axe vistas autenticadas pendiente | WEB-AUD-002 | 05_ACCESIBILIDAD_COMPLEMENTO.md; axe/*.json publicas OK | Media | a11y incompleta en app autenticada | Sin sesion E2E | Axe dashboard+lotes | Axe auth | Dev | 2026-11-17 | Parcial (publico OK) |
| S11-H-004 | k6 negocio no ejecutado (/health = infra) | WEB-AUD-003 | 06_RENDIMIENTO_PLAN_CARGA.md | Media | Capacidad negocio no medida | Sin TOKEN/perfil | k6 auth negocio | PERF-B1..B5 | Dev | 2026-11-17 | Pendiente |
| S11-H-005 | Uptime/MTTR no medidos | WEB-AUD-004 | 07_CONFIABILIDAD_UPTIME_MTTR.md | Media | SLO no demostrable | Sin monitoreo | Instrumentar | Serie temporal | Ops | 2026-12-01 | No medido / No verificable |
| S11-H-006 | npm 20 vulns (2 crit / 2 high) | SEC-WEB-01 | npm/VULNERABILIDADES_DETALLE.*; PLAN_REMEDIACION.md | Alta | Supply chain | vitest/tinypool/zod/postcss | Bumps o excepcion formal | npm audit | Dev | 2026-11-17 | Pendiente |
| S11-H-007 | Commit exacto en Render No verificable | Deploy | 09_DESPLIEGUE_SHA_RENDER.md | Media | Drift posible codigo vs deploy | Sin metadata version | Exponer /version o header | Smoke + SHA | Dev/Ops | 2026-11-17 | No verificable |
| S11-H-008 | Semgrep/Gitleaks no ejecutados | SAST | — | Media | Cobertura SAST incompleta | Tools ausentes | Instalar en CI | Reportes | Dev | 2026-11-17 | No ejecutado |
| S11-H-OK-01 | pip-audit limpio | deps | pip_audit_s11.txt | — | — | Remediacion previa | Mantener | pip-audit | Dev | — | Resuelto |
| S11-H-OK-02 | /docs deshabilitado prod | SEC-WEB-04 | smoke_prod_2026-11-03.txt | — | — | APP_ENV production | Mantener | HTTP 404 | Dev | — | Resuelto (prod smoke) |
| S11-H-OK-03 | Contaminacion dominio 0% | Arquitectura | domain_contamination_s11.txt | — | — | Hexagonal | Mantener | isolation | Dev | — | Resuelto |
| S11-H-OK-04 | Axe vistas publicas ampliadas | a11y | axe/playwright_axe_complemento.txt | — | — | Complemento S11 | Completar auth | Axe auth | Dev | — | Mitigado parcial |

## Riesgos — recomendacion del desarrollador
**No se recomienda aceptar formalmente** WEB-AUD-012 ni ausencia de E2E autenticado como cierre de aptitud productiva.
La autoridad competente debe decidir aceptacion. Esta auditoria **no copia** la aceptacion del acta PMV2 previa.
Dictamen vigente: **NO APTO**.
