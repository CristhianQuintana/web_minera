# Registro de hallazgos — WEB_MINERA

**Auditoría:** 2026-11-03  
**Commit baseline:** `d9aef31569bee06c9e55e010e0537a9bcf8593a5`  
**Regla:** no se corrigieron defectos durante esta auditoría.

---

## Defectos / incumplimientos

### SEC-WEB-01 — Dependencias frontend con vulnerabilidades críticas/altas
| Campo | Contenido |
|---|---|
| Fecha/área | 2026-11-03 / Seguridad A03 |
| Requisito | OWASP A03 Supply Chain; SEC-WEB-01 histórico |
| Descripción | `npm audit` reportó **23** vulnerabilidades: **3 critical**, **5 high**, **15 moderate**. Next.js 15.5.4 figura en rango afectado (RCE/DoS/XSS advisories). |
| Reproducción | `cd frontend && npm audit` |
| Esperado/real | 0 críticas/altas sin plan de remediación / 3 critical + 5 high abiertas |
| Evidencia | `security/dependencies/npm-audit.txt`, `npm-audit-summary.json` |
| Severidad/prioridad | **Crítica** / P0 |
| Impacto/causa | RCE/DoS potencial en runtime Next; causa: versión fijada 15.5.4 |
| Acción/responsable | Actualizar Next a versión parcheada compatible (≥15.5.28 sugerido por audit) + re-audit; Desarrollador web |
| Estado | **Abierto** |

### SEC-WEB-02 — Dependencias Python con vulnerabilidades
| Campo | Contenido |
|---|---|
| Fecha/área | 2026-11-03 / Seguridad A03 |
| Requisito | OWASP A03; SEC-WEB-02 histórico |
| Descripción | `pip-audit -r requirements/base.txt`: **43** vulnerabilidades en **6** paquetes (`python-multipart`, `orjson`, `python-jose`, `pyasn1`, `starlette`, `ecdsa`). |
| Reproducción | `backend\.venv\Scripts\python.exe -m pip_audit -r requirements\base.txt` |
| Esperado/real | Paquetes sin CVE conocidos / 43 findings |
| Evidencia | `security/dependencies/pip-audit.txt` |
| Severidad/prioridad | **Alta** / P0 |
| Impacto/causa | Multipart/DoS/JWT crypto risk |
| Acción/responsable | Bump versiones con fix; re-ejecutar pip-audit; Backend |
| Estado | **Abierto** |

### SEC-WEB-03 — Credencial/mecanismo demo
| Campo | Contenido |
|---|---|
| Fecha/área | 2026-11-03 / A07 |
| Descripción | En código actual el bypass demo está **rechazado** (FE `http-client`, BE `platform.py`). Remanentes documentales/seeds de cleanup. |
| Reproducción | Buscar `demo-` token reject; tests `http-client.auth.test.ts` |
| Esperado/real | Demo ausente en prod / código rechaza demo |
| Evidencia | Tests auth demo + Document/informe-eliminacion-auth-demo.md |
| Severidad/prioridad | Media (histórica) / P2 |
| Acción | Revalidar variables Render (`ALLOW_DEMO_AUTH` no definida) en deploy |
| Estado | **Corregido en código — Verificación prod pendiente** |

### SEC-WEB-04 — `/docs` OpenAPI en producción
| Campo | Contenido |
|---|---|
| Fecha/área | 2026-11-03 / A02 |
| Descripción | Código deshabilita docs si `APP_ENV==production`. No se verificó el valor real en el servicio desplegado. |
| Evidencia | `backend/app/composition/application_factory/factory.py` |
| Severidad | Baja / P3 |
| Estado | **Mitigado en código — deploy no revalidado** |

### WEB-AUD-001 — Contraste WCAG insuficiente (success/warning)
| Campo | Contenido |
|---|---|
| Área | Usabilidad U / WCAG 1.4.3 |
| Descripción | Recálculo: `#16A34A` y `#D97706` sobre blanco/fondo **&lt; 4.5:1**. UI usa `text-success`/`text-warning` y `bg-success` con texto blanco en toasts. |
| Reproducción | Ver `accessibility/contrast-recalc.txt`; `frontend/src/shared/components/ui.tsx` |
| Esperado | ≥4.5:1 texto normal |
| Real | warning/blanco 3.19; success/blanco 3.30 |
| Severidad | Media / P1 |
| Estado | **Abierto** |

### WEB-AUD-002 — WCAG AA no demostrable (Axe ausente)
| Campo | Contenido |
|---|---|
| Descripción | No se ejecutó Axe Core/DevTools sobre flujos reales. |
| Evidencia | `accessibility/BLOQUEO_AXE.txt` |
| Severidad | Alta (bloqueo de dictamen AA) / P1 |
| Estado | **Bloqueo externo / No verificable** |

### WEB-AUD-003 — Rendimiento p95 bajo carga no medido
| Campo | Contenido |
|---|---|
| Descripción | k6/JMeter no instalados. Solo `GET /health` &lt;500 ms (TestClient). No demuestra p95&lt;800 ms ni 500 VU. |
| Evidencia | `performance/k6/BLOQUEO.txt`, script `smoke-api.js`, `pytest-performance.txt` |
| Severidad | Alta (factor P) / P1 |
| Estado | **Bloqueo / No verificable** |

### WEB-AUD-004 — Disponibilidad ≥99.5 % y MTTR no medidos
| Campo | Contenido |
|---|---|
| Descripción | Un health puntual no prueba ventana temporal ni MTTR&lt;5 min. |
| Severidad | Alta / P1 |
| Estado | **No verificable** |

### WEB-AUD-005 — Cobertura funcional RF sin GWT E2E completo
| Campo | Contenido |
|---|---|
| Descripción | De 11 RF web aplicables I1–I2, **0 Aprobado** bajo criterio estricto (prueba de flujo completo). Todos **Parcial**. Playwright: 2 passed, 2 skipped por falta `E2E_EMAIL`/`E2E_PASSWORD`. |
| Severidad | Alta / P1 |
| Estado | **Abierto** |

### WEB-AUD-006 — Validación FE incompleta (RF-03)
| Campo | Contenido |
|---|---|
| Descripción | Zod solo en login; resto de formularios con `required` HTML. |
| Severidad | Media / P2 |
| Estado | **Abierto** |

### WEB-AUD-007 — Evidencias: sin upload web (RF-05)
| Campo | Contenido |
|---|---|
| Descripción | Solo URL firmada/consulta; no API/UI de adjunto en web. |
| Severidad | Media / P2 |
| Estado | **Abierto** (si el alcance web compromete adjunto) |

### WEB-AUD-008 — `transport_events` sin API
| Campo | Contenido |
|---|---|
| Descripción | Migración/RLS existen; backend expone `transports` pero no CRUD de `transport_events`. |
| Severidad | Media / P2 |
| Estado | **Abierto** |

### WEB-AUD-009 — Timeline de lote no consumido por FE (RF-I2-04/RF-11)
| Campo | Contenido |
|---|---|
| Descripción | `GET /lots/{id}/timeline` existe; UI drawer no lo invoca. |
| Severidad | Media / P2 |
| Estado | **Abierto** |

### WEB-AUD-010 — ML presentado como servicio sin métricas de modelo
| Campo | Contenido |
|---|---|
| Descripción | Estimador = heurística por mineral + fallback; sin dataset train/test ni MAE/RMSE/R². |
| Severidad | Media / P2 (documental/producto) |
| Estado | **Abierto** — no declarar ML validado |

### WEB-AUD-011 — Cobertura pytest 69 %; routers/platform poco cubiertos
| Campo | Contenido |
|---|---|
| Descripción | `platform.py` 45 %, `routers.py` 64 %, supabase client 26 %. |
| Evidencia | `test-reports/pytest/pytest-stdout.txt` |
| Severidad | Media / P2 |
| Estado | **Abierto** (deuda) |

### WEB-AUD-012 — RLS / aislamiento org no verificado en vivo
| Campo | Contenido |
|---|---|
| Descripción | Políticas en SQL; sin prueba de lectura cruzada entre organizaciones con JWT reales. |
| Evidencia | `security/rls/evidencia-rls.txt` |
| Severidad | Alta / P0 |
| Estado | **Bloqueo / No verificable** |

### WEB-AUD-013 — Semgrep/Gitleaks no disponibles
| Campo | Contenido |
|---|---|
| Descripción | SAST limitado a ruff (2 F401). Escaneo secretos por regex (menciones `service_role` en docs/config, no valores). |
| Severidad | Media / P2 |
| Estado | **Bloqueo herramienta** |

### WEB-AUD-014 — Compose sin servicio ML
| Campo | Contenido |
|---|---|
| Descripción | `ml/Dockerfile` existe pero `compose.yaml` no levanta ML. |
| Severidad | Baja / P3 |
| Estado | **Abierto** |

### WEB-AUD-015 — Rate limiting no evidenciado
| Campo | Contenido |
|---|---|
| Descripción | No se encontró middleware de rate limit en API. |
| Severidad | Media / P2 |
| Estado | **Abierto** |

### WEB-AUD-016 — ESLint warning hooks
| Campo | Contenido |
|---|---|
| Descripción | `resource-page.tsx` exhaustive-deps warning. |
| Severidad | Baja / P3 |
| Estado | **Abierto** |

---

## Riesgos

| ID | Riesgo | Severidad |
|---|---|---|
| RSK-01 | Explotación supply-chain Next/sharp/postcss en prod | Crítica |
| RSK-02 | Falsa sensación de “Inc. 3 completo” sin alcance formal ni métricas ML | Alta |
| RSK-03 | IDOR entre organizaciones si RLS mal aplicada en proyecto Supabase incorrecto | Alta |
| RSK-04 | Informes FURPS previos con % no revalidables (p. ej. IC≈87 %) | Media |

## Deuda técnica

- `platform.py` monolítico (~1000+ LOC aplicación).
- Migraciones `0002`/`0003` ausentes (salto numeración).
- Tabla `mass_balances` aún en esquema histórico SQL aunque Balance ya no la usa.

## Bloqueos externos

| Bloqueo | Impacto |
|---|---|
| Sin `E2E_EMAIL`/`E2E_PASSWORD` | Playwright login/logout real skipped |
| Sin acceso Supabase prod auditor | RLS/Storage/tablas aplicadas no confirmadas |
| k6/JMeter ausentes | Factor P no calculable bajo carga |
| Axe ausente | WCAG AA no dictaminable |
| Semgrep/Gitleaks ausentes | SAST/secretos incompletos |
| Sin monitoreo uptime | Factor R disponibilidad no calculable |

## Resumen conteo

| Severidad abierta / bloqueo | Cantidad |
|---|---|
| Crítica | 1 (SEC-WEB-01) |
| Alta | 5 (SEC-WEB-02, WEB-AUD-002/003/004/005/012 — agrupar ~5–6) |
| Media | 8+ |
| Baja | 3 |
| Críticos+Altos abiertos (dictamen) | **≥ 6** |


---

## Actualizacion remediacion PMV2 — 2026-11-03

| ID | Nuevo estado | Evidencia |
|---|---|---|
| SEC-WEB-02 | Corregido pendiente deploy | pip-audit post: 0 vulns |
| SEC-WEB-01 | En progreso | Next 15.5.28; ver EXCEPCIONES_FORMALES.md |
| WEB-AUD-008 | Corregido pendiente E2E | transport_events API/UI |
| WEB-AUD-009 | Corregido pendiente E2E | Timeline UI |
| WEB-AUD-006 | Parcial | Zod lotes/custodia/transporte |
| WEB-AUD-007 | Decision B | evidence/RF-05 |
| WEB-AUD-001 | Contraste tokens | contrast-post-fix.txt |
| WEB-AUD-015 | Codigo | RateLimitMiddleware |
| WEB-AUD-010 | Documentado | INFORME_ML_WEB_MINERA.md |
| WEB-AUD-012/002/003/004/005 | Abiertos | Bloqueos entorno |



## Cierre PMV2 — 2026-11-03 (tarde)

| ID | Estado cierre |
|---|---|
| SEC-WEB-02 | **Cerrado** (pip-audit 0) |
| SEC-WEB-01 | **Riesgo aceptado** residual npm (excepcion formal) |
| WEB-AUD-001 | **Cerrado** contraste tokens |
| WEB-AUD-002 | **Parcial/cerrado login** Axe 0 serious; resto riesgo aceptado |
| WEB-AUD-003 | **Parcial** k6 health OK; negocio riesgo aceptado |
| WEB-AUD-004 | **Riesgo aceptado** No verificable |
| WEB-AUD-005 | **Riesgo aceptado** E2E auth sin secretos |
| WEB-AUD-006 | **Parcial cerrado** Zod principal |
| WEB-AUD-007 | **Cerrado** decision B |
| WEB-AUD-008 | **Cerrado codigo** transport_events |
| WEB-AUD-009 | **Cerrado codigo** timeline UI |
| WEB-AUD-010 | **Cerrado** INFORME_ML |
| WEB-AUD-012 | **Riesgo aceptado** RLS vivo |
| WEB-AUD-015 | **Cerrado** rate limit |
| SEC-WEB-04 | **Verificado local** docs 404 con APP_ENV=production |
