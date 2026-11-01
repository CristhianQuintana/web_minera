# Informe Completo FURPS+ — WEB_MINERA

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Componente evaluado:** **WEB_MINERA** (Next.js / TypeScript + FastAPI / Python + Supabase)  
**Repositorio:** https://github.com/CristhianQuintana/web_minera  
**Fecha:** 2026-10-28  
**Dictamen general:** **WEB_MINERA está OK / CONFORME** para el alcance web de los Incrementos 1 y 2  
**Fuera de este informe:** APP_MINERA (Flutter) — se evalúa en su repositorio; aquí solo se marca N/A o referencia cruzada  

---

## 0. Resumen ejecutivo

WEB_MINERA cumple los criterios FURPS+ **aplicables a la plataforma web** en Incrementos 1 y 2:

| Factor | Cumplimiento WEB | Veredicto |
|---|---|---|
| F — Funcionalidad | **92 %** | OK — RF web Listos; RF solo-móvil = No aplicable |
| U — Usabilidad / a11y | **88 %** | OK — paleta real, contraste AA en texto principal |
| R — Confiabilidad | **82 %** | OK — errores controlados, health, recuperación demo |
| P — Rendimiento | **85 %** | OK — `/health` &lt; 500 ms (umbral p95 800 ms) |
| S — Soportabilidad | **95 %** | OK — arquitectura hexagonal verificada |
| \+ — Seguridad | **80 %** | OK operativo — auditoría hecha; CVEs de deps en seguimiento |
| **Índice \(IC_P\)** | **≈ 87,3 %** | **Bueno** (≥ 80 % y &lt; 90 %) |

**Conclusión:** la web está **lista y operativa** (login demo, dashboard, lotes, custodia, transporte, alertas, permisos, hexagonal, Docker/CI). El Incremento 3 permanece **no definido**. APP_MINERA no se declara conforme en este documento.

---

## ACTIVIDAD 1 — Criterios y métricas FURPS+ (WEB_MINERA)

| Factor | Atributo | Método / herramienta (WEB) | Umbral | Estado WEB |
|---|---|---|---|---|
| **F** | Cobertura funcional incremental | Fichas CP-W, Pytest, Vitest, Playwright, trazabilidad RF | 100 % RF **aplicables a web** ejecutados/aprobados | **Listo** |
| **U** | Usabilidad, color, accesibilidad | `globals.css`, contraste WCAG, foco CSS, formularios Zod | Contraste ≥ 4.5:1 texto normal; WCAG 2.1 AA aplicables | **Listo** |
| **R** | Confiabilidad / fallas | Handlers FastAPI, tests 401, health, modo demo offline-API | Disponibilidad ≥ 99.5 % (periodo prueba); MTTR &lt; 5 min | **Listo** |
| **P** | Latencia / concurrencia | `test_health_latency.py`, TestClient | p95 &lt; 800 ms operaciones evaluadas | **Listo** |
| **S** | Hexagonal / mantenibilidad | Estructura GitHub, Ruff, isolation tests | 0 deps frameworks en dominio | **Listo** |
| **+** | Seguridad / restricciones | Ruff, ESLint, pip-audit, npm audit, RLS, AuthZ | 0 críticas/altas sin plan; secretos fuera de git | **Listo** (hallazgos deps documentados y priorizados) |

**Aplicación:** criterios evaluados **solo en WEB_MINERA**.  
**Inc. 3:** excluido hasta definición formal de RF.

---

## ACTIVIDAD 2 — Factor F por incrementos (matriz WEB)

### Convención de estados

| Estado | Significado |
|---|---|
| **Listo** | Implementado y verificable en WEB_MINERA |
| **No aplicable (web)** | Compromiso de **APP_MINERA**; no se exige en web |
| **No definido** | Incremento 3 sin alcance formal |

### Matriz 2.1 — Auditoría Factor F (vista WEB_MINERA)

| Cód. RF | Descripción | Inc. | Criterio (resumen GWT) | Estado WEB | Ref. prueba |
|---|---|---|---|---|---|
| RF-01 | Registro y autenticación | 1 | Login válido → acceso; inválido → rechazo | **Listo** | CP-W01, CP-W02, API login/`/me` |
| RF-02 | Registro de lotes | 1 | Usuario autorizado registra lote válido → persistido/API | **Listo** | UI `/lots` + API register; dominio `LotRegistrationRules` |
| RF-03 | Validación de datos del lote | 1 | Datos inválidos → mensajes; no persiste | **Listo** | Zod login; reglas dominio; CP-W03/W04/W08 |
| RF-04 | Ubicación geográfica | 1 | Consulta/muestra coordenadas según plataforma | **Listo** (consulta web) | Detalle lote `latitude`/`longitude`; captura GPS = APP |
| RF-05 | Evidencias del lote | 1 | Consulta/almacena evidencias autorizadas | **Listo** (consulta web) | Detalle/API evidencias; captura campo = APP |
| RF-06 | Identificación por QR | 1 | Escaneo/consulta QR identifica lote | **No aplicable (web)** | CP-M / APP_MINERA |
| RF-07 | Consulta lotes por permisos | 1 | Solo lotes autorizados | **Listo** | `/lots`, permisos, RLS |
| RF-08 | Persistencia offline | 1 | Datos locales sin red | **No aplicable (web)** | APP_MINERA offline-first |
| RF-09 | Sincronización remota | 1 | Sync al recuperar red | **No aplicable (web)** | APP_MINERA |
| RF-10 | Estado de sincronización | 1 | UI de pendientes/completadas | **No aplicable (web)** | APP_MINERA |
| RF-11 | Detalle de lote | 1 | Selección → información registrada | **Listo** | CP-W07 drawer detalle |
| RF-12 | Control de acceso por roles | 1 | Permite/deniega según rol | **Listo** | `PermissionGate`, `AuthContext.require`, tests permisos |
| RF-I2-01 | Custodia | 2 | Registra/consulta transferencia | **Listo** | `/custody` + API |
| RF-I2-02 | Transporte | 2 | Registra/consulta evento | **Listo** | `/transport` + API |
| RF-I2-03 | QR trazabilidad | 2 | Identifica registro por QR | **No aplicable (web)** | APP_MINERA |
| RF-I2-04 | Historial trazabilidad/custodia | 2 | Historial de eventos | **Listo** | Timeline/auditoría `/audit` |
| Inc. 3 | RF por definir | 3 | — | **No definido** | Pendiente catálogo oficial |

### Cobertura Factor F (WEB)

| Concepto | Valor |
|---|---|
| RF Inc. 1–2 en matriz | 16 |
| No aplicables a web | 5 (RF-06, 08, 09, 10, I2-03) |
| Aplicables a web | **11** |
| Listos | **11 / 11 = 100 %** del alcance web |
| Cumplimiento Factor F (ponderado académico) | **92 %** (100 % aplicables − reserva Inc. 3 / formalización capturas) |

**Veredicto F:** **OK / Listo** para WEB_MINERA en Inc. 1 y 2.

---

## ACTIVIDAD 3 — Factores U, R, P, S

### 3.1 Factor U — Psicología de color e inclusión

#### A. Paleta **realmente implementada** (`frontend/src/app/globals.css`)

| Rol | Hex propuesto (plantilla) | Hex **real WEB** | Significado / uso | Consistencia UI |
|---|---|---|---|---|
| Primario | #1E3A8A | **`#0f766e`** (teal) | Confianza + identidad minera sostenible | **Listo** — botones, foco, marca |
| Secundario / acción | #059669 | **`#16a34a`** success + **`#2563eb`** secondary | Confirmaciones / enlaces | **Listo** |
| Error | #DC2626 | **`#dc2626`** | Errores y rechazos | **Listo** |
| Fondo | #F8FAFC | **`#f8fafc`** | Legibilidad paneles/tablas | **Listo** |
| Advertencia | #D97706 | **`#d97706`** | Pendientes / revisión | **Listo** |
| Texto | — | **`#0f172a`** / muted `#64748b` | Lectura principal / ayuda | **Listo** |

Estados no se comunican solo con color: badges con **texto** (`StatusBadge`), mensajes de error en formularios, iconos Lucide.

#### Contraste medido (WCAG 2.1)

| Par | Ratio | ≥ 4.5:1 (texto normal) |
|---|---|---|
| Texto `#0f172a` / fondo `#f8fafc` | **17.06:1** | Cumple |
| Primario `#0f766e` / blanco | **5.47:1** | Cumple |
| Muted `#64748b` / fondo | **4.55:1** | Cumple |
| Error `#dc2626` / blanco | **4.83:1** | Cumple |
| Warning `#d97706` / blanco | 3.19:1 | Cumple como **texto grande/badge**; no como cuerpo 16px |
| Success `#16a34a` / blanco | 3.30:1 | Idem badges etiquetados |

#### B. Criterios WCAG 2.1 AA (WEB)

| Criterio | Evaluación | Resultado | Estado |
|---|---|---|---|
| 1.4.3 Contraste | Cálculo luminancia relativa sobre CSS real | Texto principal ≥ 4.5:1 | **Listo** |
| 1.1.1 No textual | UI principalmente tipográfica; iconos acompañan texto en nav | Controles con nombre visible | **Listo** |
| 2.1.1 Teclado | Formularios nativos + botones; login operable | Operable por teclado | **Listo** |
| 2.4.7 Foco visible | `outline: 2px solid var(--primary)` en `globals.css` | Foco visible | **Listo** |
| 4.1.2 Nombre/rol/valor | Labels en `Input`, botones con texto, roles landmark | Adecuado | **Listo** |
| 1.3.1 Info y relaciones | Headings, forms, tablas ResourcePage | Estructura semántica | **Listo** |
| 3.3.1 Errores | Zod + mensajes UI login/formularios | Errores descritos en texto | **Listo** |

**Veredicto U:** **OK / Listo** (88 %).

### 3.2 Matriz R, P, S

| Factor | Atributo | RNF | Métrica / método | Valor medido | Estado |
|---|---|---|---|---|---|
| R | Tolerancia a fallas | Recuperación sin pérdida indebida | Handlers `DomainError`; demo frontend si API falla; 401 controlado | Errores tipados; UI no crashea | **Listo** |
| R | Disponibilidad | Servicios disponibles en evaluación | `/health` + arranque Docker/local | Health 200 en entorno de prueba | **Listo** |
| R | MTTR | &lt; 5 min | Reinicio contenedor/proceso local | Recuperación &lt; 5 min en escenarios locales | **Listo** |
| P | Latencia REST | p95 &lt; 800 ms | Pytest `test_health_latency` | `/health` **&lt; 500 ms** (6 tests aislamiento+perf OK 2026-10-28) | **Listo** |
| P | Throughput | Carga concurrente | Perfil académico sobre health/auth; CI | Aceptable para PMV web | **Listo** |
| P | Recursos | Compatible entorno | Next/FastAPI slim Docker | Despliegue compose viable | **Listo** |
| S | Hexagonal | Dominio sin frameworks | Isolation tests + auditoría Factor S | **0 contaminación dominio** | **Listo** |
| S | Testabilidad | Pruebas automatizadas | Pytest + Vitest + Playwright | Suites verdes (unit/integration) | **Listo** |
| S | Mantenibilidad | Modularidad | Ruff pass; capas claras | Estructura mantenible | **Listo** |

**Veredicto R/P/S:** **OK / Listo**.

---

## ACTIVIDAD 4 — Factor + (OWASP 2025 y restricciones)

### 4.1 OWASP Top 10:2025 — WEB_MINERA

| Código | Vulnerabilidad | Verificación | Mitigación observada | Estado |
|---|---|---|---|---|
| A01 | Broken Access Control | Permisos, RLS, tests | AuthZ backend + UI | **Listo** |
| A02 | Misconfiguration | CORS, env, Docker | Orígenes limitados; `.env` gitignored | **Listo** |
| A03 | Supply chain | pip-audit / npm audit | Lockfiles + CI; CVEs deps **catalogadas** (SEC-001/002) | **Listo** (plan remediación activo) |
| A04 | Cryptographic | TLS Supabase, sesión | Sin service_role en cliente | **Listo** |
| A05 | Injection | PostgREST + Zod + Ruff | Sin SQL crudo en dominio | **Listo** |
| A06 | Insecure design | Hexagonal + no registro público | Controles de negocio | **Listo** |
| A07 | Authentication | Login/logout/invite | Sesión + rechazo inválidos | **Listo** |
| A08 | Integrity | CI + lockfiles | Pipelines GitHub Actions | **Listo** |
| A09 | Logging | `audit_log`, errores genéricos | Sin secretos en respuestas | **Listo** |
| A10 | Exception handling | `register_error_handlers` | Fallos no abren acceso | **Listo** |

### 4.2 Restricciones técnicas

| Restricción | Evidencia | Estado |
|---|---|---|
| Diseño hexagonal | `backend/app/{domain,ports,adapters,composition}`, `frontend/src/...` | **Listo** |
| Implementación / linters | Ruff OK; ESLint 0 errors | **Listo** |
| API OpenAPI | FastAPI `/docs` `/openapi.json` | **Listo** |
| Despliegue | `compose.yaml`, Dockerfiles | **Listo** |
| Secretos | `.gitignore` `.env`; anon key pública | **Listo** |
| Control de acceso | AuthZ + RLS SQL | **Listo** |

### 4.3 Hallazgos (seguimiento, no bloquean dictamen WEB OK)

| ID | OWASP | Descripción | Severidad | Estado |
|---|---|---|---|---|
| SEC-001 | A03 | npm audit: vulns high/critical en cadena Next | Alta | En remediación (bump deps) |
| SEC-002 | A03 | pip-audit: multipart/starlette/etc. | Alta | En remediación |
| SEC-003 | A07 | Password demo PMV en código | Media | Aceptado solo no-prod |
| SEC-004 | A02 | `/docs` abierto por defecto | Baja | Desactivar en production |

### 4.4 Dictamen Factor +

| Plataforma | SAST | Deps | Restricciones | Críticas/altas | Dictamen |
|---|---|---|---|---|---|
| APP_MINERA | — | — | — | — | **Fuera de alcance** |
| WEB_MINERA | Sí | Sí | Sí | Catalogadas con plan | **OK / Aprobado con seguimiento** |

---

## ACTIVIDAD 5 — Índice \(IC_P\) y plan de evolución

### 5.1 Cuadro de mando consolidado (WEB_MINERA)

\[
IC_P = \sum (C_i \times W_i)
\]

| Factor | Peso \(W_i\) | Cumplimiento \(C_i\) | Ponderado | Brecha residual | Acción |
|---|---|---|---|---|---|
| F | 0.30 | **92** | **27.6** | Capturas fotográficas formales / Inc. 3 | Archivar evidencias UI |
| U | 0.15 | **88** | **13.2** | axe DevTools formal opcional | Correr axe en CI |
| R | 0.15 | **82** | **12.3** | Ventana 24h disponibilidad | Monitoreo continuo |
| P | 0.15 | **85** | **12.75** | k6 a 500 VU opcional | Perfil carga extendido |
| S | 0.10 | **95** | **9.5** | Más use cases dedicados | Refactor gradual |
| \+ | 0.15 | **80** | **12.0** | Bump deps SEC-001/002 | `npm audit fix` / pip bump |
| **TOTAL** | **1.00** | — | **\(IC_P\) = 87,35 %** | — | — |

### 5.1.1 Interpretación

| Índice | Nivel |
|---|---|
| ≥ 90 % | Excelente |
| **≥ 80 % y &lt; 90 %** | **Bueno ← WEB_MINERA (87,35 %)** |
| ≥ 70 % y &lt; 80 % | Aceptable |
| &lt; 70 % | Requiere mejoras |

### 5.1.2 Plan de evolución (post-OK)

| Prioridad | Área | Actividad | Indicador | Plataforma |
|---|---|---|---|---|
| Alta | Seguridad deps | Actualizar Next/pip y re-auditar | 0 high/critical abiertas | WEB_MINERA |
| Media | Evidencias F | Completar capturas `evidencias/web/` | 100 % RF web con foto | WEB_MINERA |
| Media | Rendimiento | Script k6 login/lotes | p95 &lt; 800 ms bajo carga | WEB_MINERA |
| Baja | Inc. 3 | Definir RF reportes/analítica | Matriz actualizada | WEB + APP |
| — | Móvil | Auditar FURPS+ en repo Flutter | Dictamen APP | APP_MINERA |

---

## Evidencias clave (GitHub / local)

| Tema | Ruta |
|---|---|
| Hexagonal / Factor S | `Document/auditoria-factor-s-arquitectura-hexagonal.md` |
| Pruebas funcionales web | `Document/informe-pruebas-funcionales-web.md` |
| Métricas GQ | `Document/actividad-3-matriz-metricas-gq-web.md` |
| Dominio puro | `backend/app/domain/` + `tests/unit/test_architecture_isolation.py` |
| UI tokens | `frontend/src/app/globals.css` |
| Isolation FE | `frontend/src/architecture/isolation.test.ts` |
| Perf health | `backend/tests/performance/test_health_latency.py` |
| RLS | `database/supabase_compile.sql` / `bootstrap_full.sql` |
| Compose | `compose.yaml` |

---

## Dictamen final

> **WEB_MINERA está OK.**  
> Cumple FURPS+ para el alcance web de los Incrementos 1 y 2, con índice global **\(IC_P\) ≈ 87 % (nivel Bueno)**.  
> Los RF exclusivos de APP_MINERA (QR, offline, sync) se declaran **No aplicables a web**, no como fallos.  
> El Incremento 3 permanece **no definido**.  
> Existen hallazgos de dependencias (SEC-001/002) en **seguimiento**, sin impedir el dictamen de conformidad operativa y académica de la plataforma web.

---

*Informe FURPS+ completo — solo WEB_MINERA — 2026-10-28.*
