# INFORME DE AUDITORÍA INTEGRAL — WEB_MINERA


---

## Portada de entrega PMV2 — 2026-11-03

**Estado del paquete:** LISTO PARA ENTREGA  
**Dictamen:** APTA CON RIESGOS ACEPTADOS  
**Informe maestro consolidado:** `INFORME_ENTREGA_FINAL_PMV2_WEB_MINERA.md` (tambien en `Document/`)  
**IC_WEB entrega:** 67.4%  
**SHA cierre:** `bca96c29042941c74c3d3455b050ce43634df152`  

Este informe de auditoria conserva el baseline historico y los addenda de remediacion.  
Para la carpeta de entrega academica usar el informe maestro + anexos copiados en `Document/`.




| Campo | Valor |

|---|---|

| Proyecto | Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable |

| Componente | WEB_MINERA — Next.js/TypeScript, FastAPI/Python, Supabase |

| Versión informe | 1.0 |

| Fecha | 2026-11-03 |

| Responsable auditoría | Agente de auditoría (Cursor) sobre repositorio del desarrollador |

| Baseline commit | `d9aef31569bee06c9e55e010e0537a9bcf8593a5` |

| Rama | `main` |

| Dictamen | **REQUIERE MEJORAS** — no conforme para cierre FURPS+ / aceptación académica completa |



> **Política aplicada:** se registró estado inicial; **no** se corrigieron defectos durante la auditoría. Correcciones = tareas separadas + regresión.



---



## 1. Resumen ejecutivo



WEB_MINERA tiene una base funcional amplia (auth Supabase, lotes, custodia, transporte, recepción, pesaje, balance calculado, alertas, auditoría, ML heurístico) y arquitectura hexagonal con **0 % contaminación del dominio** verificada en este commit. Sin embargo, la auditoría **revalida** —y **no confirma**— el índice FURPS+ previo (~87 %): faltan pruebas de flujo completo, Axe, carga k6, disponibilidad temporal, RLS en vivo y remediación de CVEs críticos en Next.js.



### Tabla obligatoria



| Dimensión | Resultado | Evidencia | Pendientes críticos |

|---|---|---|---|

| Avance implementación | **≈ 73 %** (8/11 aplicables con implementación sustancial; 0/11 Aprobado estricto) | Matriz RF | Completar GWT + E2E |

| Cobertura funcional | **0 % Aprobado** / **100 % Parcial** sobre 11 aplicables I1–I2 | Matriz + Playwright | Credenciales E2E + RLS vivo |

| Pruebas aprobadas | **Pytest 51/51**; **Vitest 19/19**; **Playwright 2/4 (2 skip)** | `test-reports/` | E2E con secretos; ampliar casos RF |

| Accesibilidad | **No verificable AA** | Contraste recalculado; Axe bloqueado | Axe + fix success/warning |

| Confiabilidad | **No verificable** (≥99.5 % / MTTR) | Solo health puntual | Monitoreo / runbooks |

| Rendimiento | **No verificable** p95 carga | Solo `/health` &lt;500 ms; k6 ausente | Ejecutar `performance/k6/smoke-api.js` |

| Arquitectura | **≈ 85 %** (dominio 0 % contaminación; cov 69 %) | `architecture/` | Subir cobertura platform/routers |

| Seguridad | **≈ 38 %** (deps fallidas) | OWASP + npm/pip audit | P0 Next + pip bumps |

| Datos/integración | **Parcial** | SQL en git; Supabase live no confirmado; ML heurístico | Validar migraciones aplicadas |

| Índice FURPS+ WEB | **≈ 50 %** (estimación conservadora) | §20 | Requiere mejoras (&lt;70) |

| Hallazgos críticos/altos abiertos | **≥ 6** | `AUDIT_WEB_MINERA_HALLAZGOS.md` | SEC-WEB-01/02, RLS, Axe, k6, RF |



---



## 2. Alcance, exclusiones y metodología



### Alcance

Frontend, backend, API, SQL/migraciones, ML repo, Docker/CI, pruebas locales, escaneos de dependencias, contraste CSS, aislamiento de dominio.



### Exclusiones / N/A

- **APP_MINERA (Flutter):** GPS nativo, Drift offline, sync cliente, escaneo QR físico → **N/A WEB** (RF-06, 08, 09, 10, I2-03).

- Decisiones legales/fraude/sanciones: el software no debe declararlas; ML no valida legalidad.



### Metodología

1. Snapshot baseline (`logs/baseline.txt`).

2. Inspección estática de rutas/API/SQL/tema.

3. Ejecución real: pytest+cov, vitest, eslint, tsc, playwright, ruff, npm audit, pip-audit, escaneo patrones, contraste WCAG, isolation tests.

4. Marcado honesto: Aprobado / Parcial / Fallido / No implementado / No verificable / N/A.

5. **No** se reutilizaron % del informe FURPS+ del 2026-10-28 sin revalidar.



---



## 3. Repositorio y entorno



| Ítem | Valor |

|---|---|

| Repo | https://github.com/CristhianQuintana/web_minera.git |

| Rama | `main` |

| SHA | `d9aef31569bee06c9e55e010e0537a9bcf8593a5` |

| Mensaje | fix: balance de masas calculado sin tabla mass_balances |

| Fecha commit | 2026-11-03 10:25:05 -0500 |

| Node / npm | v24.13.0 / 11.19.1 |

| Next / React / TS | 15.5.4 / 19.1.0 / 5.9.3 |

| Python / FastAPI | 3.11.9 / 0.115.12 |

| Árbol inicial | ver `logs/git-status-inicial.txt` |



---



## 4. Arquitectura real



```text

[Next.js FE] --JWT--> [FastAPI hexagonal] --service_role (server)--> [Supabase Auth+DB+Storage]

                              |

                              +--> [ML service HTTP] (heurística; fallback local)

```



Capas BE: `domain` → `application` → `ports` ← `adapters` ← `composition`.  

FE: isolation test obliga a no contaminar domain/application con Next/adapters.



Diagrama detallado y métricas: `architecture/domain-audit.md`.



---



## 5. Factor F — Funcionalidad



### 5.1 Mapeo Incrementos 1–2 (11 aplicables web)



N/A justificados (excluidos del denominador): RF-06, RF-08, RF-09, RF-10, RF-I2-03 → APP_MINERA.



| Código | Estado auditoría 2026-11-03 | ¿Flujo completo demostrado? |

|---|---|---|

| RF-01 | Parcial | No (login OK E2E skipped) |

| RF-02 | Parcial | No |

| RF-03 | Parcial | No |

| RF-04 | Parcial | No |

| RF-05 | Parcial | No |

| RF-07 | Parcial | No (RLS vivo pendiente) |

| RF-11 | Parcial | No |

| RF-12 | Parcial | No |

| RF-I2-01 | Parcial | No |

| RF-I2-02 | Parcial | No (`transport_events` gap) |

| RF-I2-04 | Parcial | No |



**Cobertura funcional (estricto):** `(0 aprobados / 11) × 100 = 0 %`  

**Avance implementación (código sustancial presente):** `(≈8 / 11) × 100 ≈ 73 %`  

(RF-05 upload y RF-I2-02 eventos finos restan; se contabilizan como parciales no “completos”.)



### 5.2 Incremento 3 / TO-BE

Capacidades **presentes en código** pero **sin alcance formal aprobado** ni catálogo RF oficial: recepción, pesaje, balance determinístico (sin `mass_balances`), ML heurístico, alertas, auditoría.  

Clasificación: **Parcial / diseñada-operativa sin formalización**. **No** se declara Incremento 3 completo.



Candidatos RF-I3 (separados de aprobados): ver backlog §21.



---



## 6. Factor S — Hexagonal y mantenibilidad



| Criterio | Resultado |

|---|---|

| Contaminación dominio | **0 / 9 archivos** → 0 % |

| Isolation BE | 5 passed |

| Isolation FE | 4 passed |

| Cobertura | 69 % líneas `app` |

| Ruff | 2 F401 |

| Duplicación/CC cuantitativa | No verificable |



**Score S estimado: 85 %**



---



## 7. Factor U — Usabilidad / WCAG



### Paleta real (`globals.css`) — coincide con referencia



| Rol | Hex |

|---|---|

| Primario | `#0F766E` |

| Secundario | `#2563EB` |

| Éxito | `#16A34A` |

| Error | `#DC2626` |

| Fondo | `#F8FAFC` |

| Warning | `#D97706` |

| Texto | `#0F172A` / `#64748B` |



### Contraste recalculado (2026-11-03)



| Par | Ratio | ≥4.5 |

|---|---|---|

| Texto/fondo | 17.06 | PASS |

| Primario/blanco | 5.47 | PASS |

| Secundario texto/fondo | 4.55 | PASS |

| Error/blanco | 4.83 | PASS |

| Warning/blanco | 3.19 | **FAIL** |

| Success/blanco | 3.30 | **FAIL** |



Foco visible: `:focus-visible` definido.  

**Axe:** no ejecutado → **WCAG 2.1 AA no dictaminable**.  

**Score U estimado: 48 %** (paleta OK − fallos contraste − sin Axe).



---



## 8. Factor R — Confiabilidad



Escenarios: handlers tipados y fallback ML existen en código; **no** se midió indisponibilidad prolongada, MTTR, ni recuperación en prod.



| Objetivo | Estado |

|---|---|

| Disponibilidad ≥99.5 % | **No verificable** |

| MTTR &lt;5 min | **No verificable** |

| Health puntual | OK (pytest performance) |



**Score R estimado: 40 %**



---



## 9. Factor P — Rendimiento



| Medición | Resultado |

|---|---|

| `GET /health` TestClient | &lt;500 ms (1 test) |

| k6/JMeter | **No ejecutado** (herramienta ausente) |

| p95 operaciones reales bajo VU | **No verificable** |



Script entregado: `performance/k6/smoke-api.js`.  

**Score P estimado: 28 %**



---



## 10. Factor + — OWASP 2025



Ver `security/owasp/MATRIZ_OWASP_2025.md`.



| Hallazgo histórico | Estado cierre |

|---|---|

| SEC-WEB-01 npm | **Abierto** (3 critical / 5 high) |

| SEC-WEB-02 pip | **Abierto** (43 vulns / 6 pkgs) |

| SEC-WEB-03 demo | Código OK; prod **pendiente** |

| SEC-WEB-04 /docs | Código OK; deploy **pendiente** |



**Score + estimado: 38 %**



---



## 11. Base de datos / Supabase / Storage



- Migraciones en git: `0001`, `0004`–`0008` (+ seeds `APPLY_FIX_ML_AND_DEMO.sql`).

- RLS políticas declaradas en SQL; **aplicación real en proyecto Supabase prod no confirmada en esta corrida**.

- Bucket `evidencias` (privado) en `0001_init.sql`.

- `service_role`: referencias de configuración/docs; **no** en bundle FE. Uso BE debe permanecer secreto de servidor.

- Balance: **no** depende de tabla `mass_balances` (cálculo live).



---



## 12. Integración FE / BE / ML



- OpenAPI: deshabilitado en `APP_ENV=production` (código).

- ML: factor por mineral (`oro`/`carbón`/default) + fallback `1.0.0-fallback`; **no** hay MAE/RMSE/R² ni dataset train/test versionado como modelo validado.

- Compose **no** incluye servicio ML.



---



## 13. CI/CD y despliegue



Workflows GitHub presentes. Dockerfiles presentes. Despliegue Render **no revalidado** aquí (`deployment/evidencia-despliegue.md`).



---



## 14. Resultados de pruebas (ejecutados)



| Suite | Resultado | Exit |

|---|---|---|

| Pytest | 51 passed; cov 69 % | 0 |

| Vitest | 19 passed / 5 files | 0 |

| ESLint | 0 errors, 1 warning | 0 |

| tsc | OK | 0 |

| Playwright | 2 passed, 2 skipped | 0 |

| Pytest performance | 1 passed | 0 |

| npm audit | 23 vulns | ≠0 |

| pip-audit | 43 vulns | ≠0 |

| ruff | 2 F401 | ≠0 |

| Semgrep / Axe / k6 / Gitleaks | No ejecutados | Bloqueo |



**Cumplimiento de pruebas (casos locales planificados ejecutables sin secretos externos):**  

Pytest+Vitest+perf = 71/71 = **100 %** de esa subtalla.  

Incluyendo E2E aplicables con credenciales: 2 passed + 2 no ejecutados → **50 %** E2E.  

**Global transparente:** no se declara 100 % del plan RF/GWT.



---



## 15. Indicadores de valor



| Indicador | Estado |

|---|---|

| Tiempo registro / sync / predicción | **No medido** en esta auditoría |

| MAE / RMSE / R² | **No aplicables** (heurística; no inventar) |

| Discrepancias de masa | Capacidad de cálculo presente; métrica operativa no medida |

| Reducción tiempo auditoría | Sin línea base |



---



## 16. Cálculo FURPS+ WEB (reproducible)



Pesos: F 30 %, U 15 %, R 15 %, P 15 %, S 10 %, + 15 %.



| Factor | Score usado | Aporte |

|---|---|---|

| F | 55 % (parciales con código; 0 % estricto no se usa solo) | 16.5 |

| U | 48 % | 7.2 |

| R | 40 % | 6.0 |

| P | 28 % | 4.2 |

| S | 85 % | 8.5 |

| + | 38 % | 5.7 |

| **IC_WEB** | | **≈ 48 %** |



Escala proyecto: **&lt;70 Requiere mejoras**.



Notas:

- Si F se fijara en 0 % (solo Aprobados), IC ≈ **31 %**.

- El informe del 2026-10-28 (~87 %) **no** se adopta: no revalidó k6/Axe/disponibilidad/CVEs actuales.



---



## 17. Actores y cadena de valor (validación)



| Actor | Soporte WEB | Notas |

|---|---|---|

| Minero/Productor | Parcial | Consulta lotes/org; corrección según permisos |

| Transportista | Parcial | Transporte web; eventos finos limitados |

| Planta/Comprador | Parcial | Recepción/pesaje |

| Auditor/Admin | Parcial | Balance, alertas, audit, users |

| Autoridad | Parcial/consulta | Sin decisión automática de fraude |



---



## 18. Plan correctivo priorizado (backlog)



### P0

1. Actualizar Next.js y deps críticas; `npm audit` limpio (SEC-WEB-01).

2. Bump `python-multipart`, `starlette`/`fastapi` alineado, `orjson`, reemplazar/actualizar stack JWT (`python-jose`/`ecdsa`/`pyasn1`) (SEC-WEB-02).

3. Pruebas RLS multi-org con JWT reales + evidencia (WEB-AUD-012).



### P1

4. Ejecutar Axe en login/dashboard/lots/custody; corregir contraste success/warning.

5. Ejecutar k6 con script entregado; publicar p95 por endpoint.

6. Completar E2E con secretos de CI; GWT por RF aplicable.

7. Cablear timeline FE; decidir alcance upload evidencias web.



### P2

8. Zod en formularios de escritura; API `transport_events` o documentar N/A.

9. Formalizar RF Incremento 3; etiquetar ML como heurística hasta métricas.

10. Rate limit + Semgrep/Gitleaks en CI.

11. Monitoreo uptime/MTTR.



### P3

12. Incluir ML en compose o documentar despliegue separado.

13. Limpiar F401 ruff; warning eslint hooks.

14. Revalidar `/docs` y demo flags en Render.



---



## 19. Dictamen



**WEB_MINERA no puede declararse conforme FURPS+ ni “lista académicamente cerrada” en esta fecha.**  

Fortalezas reales: hexagonal limpio, auth demo eliminada en código, suite unit/integration verde, módulos I3 prototipados.  

Brechas bloqueantes de aceptación §20: CVEs críticos, ausencia Axe/k6/disponibilidad/RLS vivo, RF sin Aprobado por flujo completo.



---



## 20. Anexos



```text

audit/web_minera/

  INFORME_AUDITORIA_WEB_MINERA.md

  MATRIZ_TRAZABILIDAD_WEB_MINERA.csv

  AUDIT_WEB_MINERA_HALLAZGOS.md

  test-reports/pytest|vitest|playwright/

  security/{sast,dependencies,secrets,owasp,rls}/

  accessibility/

  performance/k6/

  architecture/

  deployment/

  logs/baseline.txt

```



---

## Addendum cierre PMV2 — 2026-11-03

Dictamen actualizado: **APTA CON RIESGOS ACEPTADOS** (ver ACTA_CIERRE_PMV2_WEB_MINERA.md).
IC_WEB recalculado: **67.4%**.
Evidencias nuevas: Axe login, k6 smoke, pip-audit 0, Next 15.5.28, Playwright 5/7.
Riesgos residuales: RIESGOS_ACEPTADOS_PMV2.md.
No reemplaza la seccion de baseline; conviven historico y post-correccion.
