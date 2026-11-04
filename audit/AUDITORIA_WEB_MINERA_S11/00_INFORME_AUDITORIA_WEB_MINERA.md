# 00 — INFORME DE AUDITORÍA S11 — WEB_MINERA

| Campo | Valor |
|---|---|
| Fecha emision solicitud | 2026-11-03 |
| Fecha ejecucion | fecha_iso=2026-11-03T23:31:00-05:00 |
| Repo | https://github.com/CristhianQuintana/web_minera |
| Rama | main |
| Commit auditado | `3792632418da5e24b209680dc30ad7f3552a95e9` |
| Antecedente remediacion | `ad30938...` (no es HEAD) |
| Acta PMV2 previa | Antecedente; **no sustituye** este dictamen |
| Entorno verificado | Local (suites) + Produccion Render (smoke) |

---

## 1. Resumen ejecutivo y dictamen

### Dictamen S11 (nuevo)
**NO APTO para declarar cierre funcional/productivo completo.**  
**Verificacion parcial confirmada** (suites automaticas, smoke produccion basico, arquitectura dominio limpio, pip-audit 0).

| Dimension de aptitud | Dictamen |
|---|---|
| Apto para documentacion tecnica | **Parcial / Si** (paquete S11 generado con limitaciones) |
| Apto funcionalmente (RF UI autenticados) | **No** (0 RF con E2E autenticado Aprobado) |
| Apto tecnicamente (unit/integration/CI local) | **Parcial / Si** (52 pytest, 22 vitest, isolation OK) |
| Apto para produccion | **No** (RLS JWT vivo No verificable; commit deploy exacto NV; k6 negocio NV) |
| Apto con riesgos formalmente aceptados | **No emitido aqui** — requiere autoridad; no se hereda del acta PMV2 |

### Hallazgos bloqueantes abiertos
1. E2E autenticado omitido (S11-H-001 / WEB-AUD-005)
2. RLS multi-org JWT no ejecutado (S11-H-002 / WEB-AUD-012)
3. npm critical/high residuales (S11-H-006)
4. k6/Axe/uptime incompletos (S11-H-003/004/005)

---

## 2. Alcance y exclusiones
I1+I2 RF web aplicables; N/A: RF-06 escaneo, RF-08 sync, RF-09? (persistencia web SI aplica parcialmente — en matriz RF-09 Parcial), RF-10 es control acceso web. RF-I2-03 N/A.
ML heuristico; no ML validado.

---

## 3. Baseline y entorno
Ver carpeta `01_BASELINE/`.
- Node/npm, Python/FastAPI, Next/React/TS en archivos de versiones
- Config keys: SET/EMPTY sin secretos
- Prod URLs verificadas: web-minera-frontend/backend.onrender.com

---

## 4. Arquitectura
Ver `02_ARQUITECTURA/`. Contaminacion dominio BE **0%** (0/9). Isolation BE/FE passed.

---

## 5. Resultado por RF
Ver `03_FUNCIONAL_I1/` y `04_FUNCIONAL_I2/`.
**Aprobados flujo completo UI autenticado: 0.**

---

## 6. Casos de prueba ejecutados realmente
| Suite | Resultado |
|---|---|
| Pytest | 52 passed |
| Vitest | 22 passed |
| Playwright | 5 passed / 2 skipped |
| Isolation BE | 5 passed |
| Domain AST | 0 contamination |
| Prod smoke | health 200, docs 404, login 200, lots 401 |
| pip-audit | 0 |
| npm audit | 20 (2c/2h/16m) |
| k6 | /health only (ver limitaciones) |
| Axe | login only |

---

## 7. Seguridad / JWT / RLS
Probes sin JWT usuario: 401 OK. RLS multi-org: **No ejecutado**. No se uso service_role como usuario final.

---

## 8. Dependencias / SAST / secretos
pip limpio. npm 20 vulns. Semgrep/Gitleaks: No ejecutado.

---

## 9. Accesibilidad
Axe login limpio; demas vistas: No ejecutado.

---

## 10. Rendimiento / confiabilidad
k6 health prod ejecutado (ver stdout). Negocio/500 VU: No. Uptime/MTTR: No medido.

---

## 11. Despliegue
Smoke prod OK basico. SHA desplegado exacto: No verificable.

---

## 12. ML
Heuristico + fallback. No MAE/RMSE/R2.

---

## 13. GQM / AS-IS
Ver `10_GQM_AS_IS/`. M2.1 = 0% estricto. M3.x No medido sin insumos S9 completos.

---

## 14. Trazabilidad S9/S10/S11
Ver `11_MATRIZ_S9_S10_S11.csv`. Documentos S9 formales incompletos → no reconstruidos por suposicion.

---

## 15. Hallazgos y plan
Ver `12_HALLAZGOS_RIESGOS/HALLAZGOS_S11.md`.

---

## 16. Pruebas no ejecutadas / limitaciones
E2E auth, RLS JWT dual-org, Axe auth, k6 negocio, 500 VU, Semgrep, Gitleaks, uptime, SHA Render, Storage cross-org.

---

## 17. Conclusion
Esta auditoria S11 **confirma** mejoras tecnicas locales/prod basicas respecto al baseline d9aef31, pero **no confirma** el cierre funcional de los 11 RF ni la seguridad multi-tenant en vivo. El acta PMV2 previa no se reutiliza como dictamen.

## 18. Declaracion del desarrollador / ejecutor

| Confirmacion | Respuesta |
|---|---|
| Repo/rama/commit auditados confirmados | **Si** (`3792632418da5e24b209680dc30ad7f3552a95e9`) |
| Entorno desplegado corresponde al commit indicado | **No verificable** |
| Pruebas ejecutadas realmente | **Si** (las listadas) |
| Omitidas no declaradas aprobadas | **Si** |
| RLS con JWT reales o declarado pendiente | **Declarado pendiente/No verificable** |
| Reportes seguridad del lockfile auditado | **Si** (npm/pip S11) |
| Evidencias sanitizadas | **Si** |
| Limitaciones y riesgos declarados | **Si** |
| Ruta entrega | `audit/AUDITORIA_WEB_MINERA_S11/` |
| Nombre/rol | Agente auditor tecnico (Cursor) / apoyo Dev WEB |
| Fecha | fecha_iso=2026-11-03T23:31:00-05:00 |

Firma ejecutor tecnico: emitido electronicamente con este commit de evidencias.
Firma QA independiente: ________________
