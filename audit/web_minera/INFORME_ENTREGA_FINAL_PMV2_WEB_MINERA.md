# INFORME DE ENTREGA FINAL — PMV2 WEB_MINERA

| Campo | Valor |
|---|---|
| Proyecto | Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable |
| Componente | WEB_MINERA (Next.js / FastAPI / Supabase) |
| Fecha de entrega | 2026-11-03 |
| Generado | 2026-11-03 23:21 |
| Baseline auditoria | `d9aef31569bee06c9e55e010e0537a9bcf8593a5` |
| Remediacion | `ad30938bedec5b3ea6618e61382749a27440b538` |
| Cierre documental | `bca96c29042941c74c3d3455b050ce43634df152` (+ commit de este informe) |
| Dictamen PMV2 | **APTA CON RIESGOS ACEPTADOS** |
| Indice FURPS+ WEB (IC_WEB) | **67.4%** |

---

## 1. Proposito de este documento

Este es el **informe maestro de entrega** del PMV2 WEB. Consolida la auditoria integral, la remediacion, las pruebas de regresion y los informes tecnicos anexos listos para presentacion academica / QA.

No inventa resultados: lo no ejecutado aparece como No verificable o Riesgo aceptado con ID.

---

## 2. Resumen ejecutivo

WEB_MINERA entrega el PMV2 de Incrementos 1 y 2 (11 requisitos web aplicables) con:

1. Arquitectura hexagonal (0% contaminacion de dominio verificada).
2. Autenticacion real Supabase (demo rechazada en codigo).
3. Modulos: lotes, custodia, transporte + eventos, recepcion, pesaje, balance calculado, alertas, auditoria, ML heuristico (I3 experimental).
4. Remediacion P0 Python (pip-audit 0 vulns) y Next.js 15.5.28.
5. Validacion Zod en formularios clave; timeline en UI; rate limiting.
6. Pruebas: Pytest 52, Vitest 22, Playwright 5/7, Axe login limpio, k6 smoke health p95 16.93 ms.
7. Riesgos residuales formalizados (RLS vivo, E2E autenticado, monitoreo uptime, npm residual, Axe/k6 ampliados).

**Dictamen de entrega:** APTA CON RIESGOS ACEPTADOS.  
Pendiente solo firma humana de QA sobre `RIESGOS_ACEPTADOS_PMV2.md`.

---

## 3. Alcance y exclusiones

### Aplicables WEB (11)
RF-01, RF-02, RF-03, RF-04, RF-05 (consulta — Decision B), RF-07, RF-11, RF-12, RF-I2-01, RF-I2-02, RF-I2-04.

### N/A WEB → APP_MINERA (5)
RF-06, RF-08, RF-09, RF-10, RF-I2-03.

### RF-05 Decision B
WEB consulta/visualiza evidencias; APP carga. Ver `audit/web_minera/evidence/RF-05/DECISION_ALCANCE.md`.

### Incremento 3 / ML
Heuristico + fallback; no modelo validado MAE/RMSE/R2. No bloquea PMV2 I1–I2.

---

## 4. Linea base vs entrega

| Indicador | Auditoria inicial | Entrega PMV2 |
|---|---|---|
| SHA | d9aef31 | bca96c2 + este commit |
| IC_WEB | ~48% | **67.4%** |
| RF Aprobado estricto full E2E | 0/11 | 0/11 (honestidad); parciales con evidencia codigo+unit+E2E negativo |
| Pytest | 51 | **52** |
| Vitest | 19 | **22** |
| Playwright | 2 pass / 2 skip | **5 pass / 2 skip** |
| pip-audit | 43 | **0** |
| Next | 15.5.4 | **15.5.28** |
| Axe | No | Login 0 critical/serious |
| k6 | No | health p95 16.93 ms |
| Dictamen | Requiere mejoras | **APTA CON RIESGOS ACEPTADOS** |

---

## 5. Matriz funcional (estado de entrega)

Fuente oficial: `MATRIZ_TRAZABILIDAD_WEB_MINERA.csv`.

Todos los 11 aplicables: **Parcial** con implementacion sustancial + pruebas unitarias/negativas.  
Ninguno se marca Aprobado full-flow autenticado sin `E2E_EMAIL`/`E2E_PASSWORD` (no inventar).

Cobertura funcional estricta Aprobado: 0/11.  
Avance de implementacion (codigo verificado): alto (~73–90% segun rubrica de codigo).  
Entrega aceptada bajo regimen de riesgos residuales documentados.

---

## 6. Resultados de pruebas (regresion de entrega)

| Suite | Resultado | Ubicacion |
|---|---|---|
| Pytest | 52 passed | audit/web_minera/test-reports/pytest/ |
| Vitest | 22 passed | audit/web_minera/test-reports/vitest/ |
| Playwright | 5 passed, 2 skipped | audit/web_minera/test-reports/playwright/ |
| Axe /login | 0 critical/serious | audit/web_minera/accessibility/axe/ |
| k6 /health | p95 16.93 ms, 0% fail | audit/web_minera/performance/k6/ |
| ruff | All checks passed | audit/web_minera/security/sast/ |
| pip-audit | 0 vulns | audit/web_minera/security/dependencies/ |
| npm audit | residuales + excepcion formal | security/dependencies/EXCEPCIONES_FORMALES.md |

---

## 7. Seguridad (resumen)

- SEC-WEB-02 **Cerrado** (pip limpio).
- SEC-WEB-01 **Mitigado** (Next 15.5.28) + residual npm aceptado.
- SEC-WEB-03 demo: codigo rechaza; revalidar Render live.
- SEC-WEB-04 /docs: 404 con APP_ENV=production (verificado local).
- Rate limit activo.
- RLS: 48 politicas en migraciones (evidencia estatica). JWT multi-org vivo: riesgo aceptado.

---

## 8. Indice FURPS+ (entrega)

Pesos: F 30%, U 15%, R 15%, P 15%, S 10%, + 15%.

| Factor | Score | Nota |
|---|---|---|
| F | 72 | Implementacion + tests parciales |
| U | 70 | Contraste + Axe login |
| R | 55 | Controles; uptime NV |
| P | 60 | k6 health OK; negocio pendiente |
| S | 88 | Hexagonal limpio |
| + | 62 | pip limpio; npm residual |

**IC_WEB = 67.4%** → escala proyecto: cerca de Aceptable / requiere seguimiento de riesgos.

Detalle: `INFORME_FURPS_PLUS_WEB_MINERA.md`.

---

## 9. Anexos incluidos en la entrega (paquete audit/web_minera)

1. ACTA_CIERRE_PMV2_WEB_MINERA.md
2. RIESGOS_ACEPTADOS_PMV2.md
3. PLAN_CIERRE_PMV2_WEB_MINERA.md
4. INFORME_AUDITORIA_WEB_MINERA.md
5. INFORME_FURPS_PLUS_WEB_MINERA.md
6. INFORME_PRUEBAS_FUNCIONALES_WEB_MINERA.md
7. INFORME_SEGURIDAD_WEB_MINERA.md
8. INFORME_ACCESIBILIDAD_WEB_MINERA.md
9. INFORME_RENDIMIENTO_WEB_MINERA.md
10. INFORME_CONFIABILIDAD_WEB_MINERA.md
11. INFORME_ARQUITECTURA_WEB_MINERA.md
12. INFORME_BASE_DATOS_SUPABASE_WEB_MINERA.md
13. INFORME_CI_CD_DESPLIEGUE_WEB_MINERA.md
14. INFORME_ML_WEB_MINERA.md
15. INFORME_REGRESION_WEB_MINERA.md
16. MATRIZ_TRAZABILIDAD_WEB_MINERA.md / .csv
17. AUDIT_WEB_MINERA_HALLAZGOS.md
18. Evidencias test-reports/, security/, accessibility/, performance/

Copias de entrega academica tambien en `Document/` (este informe + acta + FURPS + matriz).

---

## 10. Checklist de entrega

- [x] Codigo en main versionado
- [x] Informes tecnicos completos
- [x] Matriz de trazabilidad
- [x] Registro de hallazgos actualizado
- [x] Acta de cierre emitida
- [x] Riesgos residuales formalizados
- [x] Regresion local verde (pytest/vitest)
- [x] Paquete consolidado (este documento)
- [ ] Firma QA humana
- [ ] Secretos E2E en CI (mejora post-entrega)
- [ ] Prueba RLS viva multi-org (mejora post-entrega)

---

## 11. Dictamen final de entrega

**WEB_MINERA PMV2 se declara listo para entrega bajo el regimen APTA CON RIESGOS ACEPTADOS.**

El producto web cumple el alcance I1–I2 implementado y documentado, con evidencia reproducible de pruebas automaticas y remediacion de seguridad Python. Los puntos no verificables quedan explicitamente aceptados y con fecha de revision, sin presentar ausencia de medicion como cumplimiento.

Responsable de emision tecnica: equipo de desarrollo WEB / agente de remediacion.  
Aceptacion academica/QA: firma en acta.
