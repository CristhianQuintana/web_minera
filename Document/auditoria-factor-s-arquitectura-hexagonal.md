# C. Auditoría Detallada de la Arquitectura Hexagonal (Factor S)

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Componente auditado:** `WEB_MINERA`  
**Repositorio GitHub:** https://github.com/CristhianQuintana/web_minera  
**Rama / commit de evidencia:** `main` · `4d9b0dd`  
**Fecha de auditoría:** 2026-10-25  
**Patrón evaluado:** Puertos y Adaptadores (Arquitectura Hexagonal / Factor S)

---

## 1. Objetivo del Factor S

Verificar en el repositorio institucional que el código implementa la separación hexagonal:

| Capa | Responsabilidad | Debe / No debe |
|---|---|---|
| **Domain core** | Entidades y reglas de negocio | Código puro; **cero** anotaciones JPA/Spring/ORM/frameworks de UI o BD |
| **Ports** | Contratos (interfaces) | Solo abstracciones; sin implementaciones de infraestructura |
| **Adapters** | Infraestructura externa | Controllers REST, clientes Supabase/HTTP, etc.; implementan o invocan puertos |

**Regla de evaluación:** no basta con que exista la carpeta; debe haber **código funcional**, dependencias orientadas hacia adentro y evidencias verificables.

---

## 2. Árbol académico vs estructura real en GitHub

La guía muestra un único `/src`. WEB_MINERA tiene **varios ejecutables**; cada uno aplica el mismo patrón en su raíz:

| Árbol de la actividad | Backend (principal) | Frontend | ML |
|---|---|---|---|
| `/src/domain/model/` | `backend/app/domain/model/` (+ `entities/`, `value_objects/`) | `frontend/src/domain/` | `ml/domain/services/` |
| `/src/domain/service/` | `backend/app/domain/service/` (+ `services/`, `rules/`) | Reglas críticas en backend | Estimador de dominio |
| `/src/ports/inbound/` | `backend/app/ports/inbound/use_cases/` | Casos de uso + composition | `ml/ports/inbound/` |
| `/src/ports/outbound/` | `backend/app/ports/outbound/` | `frontend/src/ports/outbound/` | N/A (sin I/O externo aún) |
| `/src/adapters/inbound/` | `backend/app/adapters/inbound/http/` | `frontend/src/app/`, `presentation/` | `ml/adapters/inbound/http/` |
| `/src/adapters/outbound/` | `supabase/`, `external/`, `ml/` | `frontend/src/adapters/outbound/` | — |
| Composition / DI | `backend/app/composition/` | `frontend/src/composition/` | `ml/composition/` |

> **Nota stack:** el checklist académico menciona JPA/Spring. Este proyecto usa **FastAPI + Supabase/PostgreSQL + Next.js**. El criterio equivalente es: dominio sin FastAPI, Supabase, SQLAlchemy, Next/React ni clientes HTTP.

---

## 3. Matriz Factor S — Backend (`backend/app/`)

| Componente hexagonal | Ruta en GitHub | Estado | Evidencia de desacoplamiento / hallazgo |
|---|---|---|---|
| Domain core — model | `backend/app/domain/model/` → reexporta `entities/`, `value_objects/` | **Conforme** | Dataclasses/enums de negocio; sin FastAPI, Supabase, JPA ni ORM. |
| Domain core — service | `backend/app/domain/service/` → reexporta `services/`, `rules/` | **Conforme** | Reglas de lote, custodia, recepción, balance de masa en Python puro. |
| Ports inbound | `backend/app/ports/inbound/use_cases/` | **Conforme** | `Protocol`s de casos de uso (`AuthenticateUseCasePort`, etc.); sin infra. |
| Ports outbound | `backend/app/ports/outbound/gateway.py`, `repositories/` | **Conforme** | `DataGatewayPort`, `AppConfigPort`, `EmailPort`, `MLInferencePort`; contratos sin implementación. |
| Adapters inbound (REST) | `backend/app/adapters/inbound/http/` | **Conforme** | Routers FastAPI + `dependencies.py`; traducen HTTP e inyectan casos de uso/container. |
| Adapters outbound (persistencia) | `backend/app/adapters/outbound/supabase/` | **Conforme** | `SupabaseGateway` implementa el puerto outbound (Auth + PostgREST + Storage). Equivalente a “persistence” (no JPA). |
| Adapters outbound (otros) | `adapters/outbound/external/`, `adapters/outbound/ml/` | **Conforme** | SMTP y cliente ML detrás de puertos. |
| Composition (DI) | `backend/app/composition/container.py` | **Conforme** | Único lugar que instancia adaptadores concretos y los inyecta. |
| Application | `backend/app/application/` | **Conforme** | Casos de uso y `PlatformService` dependen de puertos, no de Supabase. |
| Prueba de aislamiento | `backend/tests/unit/test_architecture_isolation.py` | **Conforme** | Falla si domain/application/ports importan frameworks o adapters. |

**Veredicto backend:** **CONFORME** al Factor S.

---

## 4. Matriz Factor S — Frontend (`frontend/src/`)

| Componente | Ruta en GitHub | Estado | Evidencia |
|---|---|---|---|
| Domain | `frontend/src/domain/` | **Conforme** | Entidades/tipos sin Next/React en el núcleo de datos. |
| Ports outbound | `frontend/src/ports/outbound/platform-port.ts` | **Conforme** | Interfaz `PlatformPort` (login, listados, etc.). |
| Application / use cases | `frontend/src/application/use-cases/auth.ts` | **Conforme** | Fábricas que reciben `PlatformPort`; no importan el adaptador HTTP. |
| Adapters outbound | `frontend/src/adapters/outbound/api/` | **Conforme** | `http-client` + `platformAdapter`. |
| Adapters inbound (UI) | `frontend/src/app/`, `presentation/` | **Conforme** | Páginas delegan en `composition` (`platform` / auth). |
| Composition | `frontend/src/composition/container.ts` | **Conforme** | Cablea `platformAdapter` una sola vez. |
| Prueba de aislamiento | `frontend/src/architecture/isolation.test.ts` | **Conforme** | Impide imports de adapters desde domain/application. |

**Veredicto frontend:** **CONFORME** al Factor S.

---

## 5. Matriz Factor S — ML (`ml/`)

| Componente | Ruta | Estado | Evidencia |
|---|---|---|---|
| Domain | `ml/domain/services/estimator.py` | **Conforme** | Estimador puro. |
| Ports inbound | `ml/ports/inbound/` | **Conforme** | `EstimateExpectedQuantityPort`. |
| Application | `ml/application/use_cases/estimate.py` | **Conforme** | Orquesta dominio. |
| Adapters inbound | `ml/adapters/inbound/http/main.py` | **Conforme** | FastAPI → use case vía composition. |
| Adapters outbound | — | **Parcial / N/A** | Sin persistencia de modelos en el PMV; no se inventan carpetas vacías. |

**Veredicto ML:** **PARCIALMENTE CONFORME** (núcleo hexagonal real; outbound no requerido aún).

---

## 6. Orientación de dependencias (Factor S)

```text
                    ┌─────────────────────────┐
                    │   Adapters inbound      │  FastAPI / Next UI
                    │   (HTTP, páginas)       │
                    └───────────┬─────────────┘
                                │ usa
                    ┌───────────▼─────────────┐
                    │  Ports inbound /        │
                    │  Application use cases  │
                    └───────────┬─────────────┘
                                │ usa
                    ┌───────────▼─────────────┐
                    │     DOMAIN CORE         │  model + service
                    │   (sin frameworks)      │
                    └───────────┬─────────────┘
                                │ define contratos
                    ┌───────────▼─────────────┐
                    │   Ports outbound        │
                    └───────────┬─────────────┘
                                │ implementado por
                    ┌───────────▼─────────────┐
                    │  Adapters outbound      │  Supabase / SMTP / HTTP ML
                    └─────────────────────────┘

        Composition root: único ensamblaje (adapters ↔ application)
```

| Condición Factor S | Backend | Frontend |
|---|---|---|
| Dominio no importa frameworks ni adapters | Cumple | Cumple |
| Ports sin implementación de infra | Cumple | Cumple |
| Inbound adapters delegan en use cases / ports | Cumple | Cumple |
| Outbound adapters implementan ports | Cumple | Cumple |
| DI en composition, no en dominio | Cumple | Cumple |
| Sin ciclos domain → adapters | Cumple | Cumple |

---

## 7. Evidencias concretas en GitHub (archivos a abrir)

### Backend
1. `backend/app/domain/model/__init__.py`  
2. `backend/app/domain/service/__init__.py`  
3. `backend/app/domain/entities/__init__.py` · `value_objects/` · `rules/` · `services/`  
4. `backend/app/ports/inbound/use_cases/__init__.py`  
5. `backend/app/ports/outbound/gateway.py`  
6. `backend/app/adapters/inbound/http/routers.py` · `dependencies.py`  
7. `backend/app/adapters/outbound/supabase/client.py`  
8. `backend/app/composition/container.py`  
9. `backend/app/application/use_cases/__init__.py` · `services/platform.py`  
10. `backend/tests/unit/test_architecture_isolation.py`

### Frontend
1. `frontend/src/domain/entities.ts`  
2. `frontend/src/ports/outbound/platform-port.ts`  
3. `frontend/src/application/use-cases/auth.ts`  
4. `frontend/src/adapters/outbound/api/platform-adapter.ts`  
5. `frontend/src/composition/container.ts`  
6. `frontend/src/architecture/isolation.test.ts`

### ML
1. `ml/domain/services/estimator.py`  
2. `ml/ports/inbound/__init__.py`  
3. `ml/adapters/inbound/http/main.py`  
4. `ml/composition/__init__.py`

### Informe técnico previo
- `docs/architecture/hexagonal-architecture-audit.md`

---

## 8. Cómo se verificó (método)

1. Inventario de rutas reales en el clon del repo.  
2. Búsqueda de imports prohibidos en `backend/app/domain` → **sin coincidencias** (`fastapi`, `supabase`, `sqlalchemy`, `httpx`, `app.adapters`).  
3. Comprobación de que `application` frontend **no** importa `platformAdapter`.  
4. Confirmación de que `SupabaseGateway` / `platformAdapter` se ensamblan solo en **composition**.  
5. Pruebas automatizadas de aislamiento (backend Pytest + frontend Vitest).

Comandos de re-verificación:

```powershell
# Dominio backend limpio (no debe listar matches)
rg -n "fastapi|supabase|sqlalchemy|httpx|app\.adapters" backend/app/domain

# Pruebas de aislamiento
cd backend; .\.venv\Scripts\python.exe -m pytest tests/unit/test_architecture_isolation.py -q
cd ..\frontend; npx vitest run src/architecture/isolation.test.ts
```

---

## 9. Hallazgos y pendientes

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| F1 | Backend y frontend cumplen Puertos/Adaptadores con código real | — | Resuelto / Conforme |
| F2 | No hay un único `/src` (hay `backend/app`, `frontend/src`, `ml`) | Informativo | Aceptable: multi-ejecutable |
| F3 | Persistencia no es JPA; es Supabase detrás de puerto | Informativo | Equivalente válido al stack |
| F4 | ML sin adaptador outbound de persistencia | Baja | Parcial; documentado |
| F5 | APP_MINERA (Flutter) no está en este repo | Fuera de alcance | Auditar en repo hermano |
| F6 | Algunos endpoints aún usan fachada `PlatformService` vía `get_platform` | Baja | Flujos críticos ya tienen use cases dedicados |

---

## 10. Conclusión Factor S

| Ámbito | Nivel Factor S |
|---|---|
| Backend FastAPI | **Conforme** |
| Frontend Next.js | **Conforme** |
| Servicio ML | **Parcialmente conforme** |
| APP_MINERA | **No evaluado** (otro repositorio) |

**Declaración para la entrega académica:**  
En el repositorio GitHub de **WEB_MINERA** se demuestra la arquitectura hexagonal (Factor S) con **dominio puro**, **puertos de entrada y salida**, **adaptadores inbound/outbound** y **composition root**, verificable en código y con pruebas de aislamiento.  

No se declara conformidad del ecosistema completo mientras **APP_MINERA** no se audite en su propio repositorio.

---

## 11. Resumen ejecutivo (una diapositiva)

| Pregunta | Respuesta |
|---|---|
| ¿Existe `domain/model` y `domain/service`? | Sí — en `backend/app/domain/` (con alias académicos + implementación canónica). |
| ¿Existen puertos inbound/outbound? | Sí — Protocols/interfaces reales. |
| ¿Existen adapters inbound/outbound? | Sí — HTTP FastAPI / UI Next / Supabase / SMTP / ML client. |
| ¿El dominio está desacoplado? | Sí — cero imports de frameworks en dominio; pruebas lo refuerzan. |
| ¿Factor S cumplido en WEB_MINERA? | **Sí** (backend + frontend); ML parcial; móvil fuera de este repo. |

---

## 12. ACTIVIDAD 4 — Factor + (Plus): Seguridad OWASP Top 10:2025 y restricciones técnicas

**Alcance de esta sección:** únicamente **WEB_MINERA** (backend FastAPI, frontend Next.js, SQL/RLS del repo, CI Docker).  
**Fuera de alcance:** APP_MINERA (Flutter) — permanece *Pendiente* en su propio repositorio.  
**Fecha de análisis:** 2026-10-25  
**Herramientas ejecutadas:** Ruff (SAST/lint Python), ESLint (frontend), `pip-audit`, `npm audit`, revisión manual de código/config/RLS, Pytest de autorización.  
**No ejecutados en esta corrida:** Semgrep, SonarQube, OWASP ZAP (DAST) — se recomiendan como complemento; su ausencia no invalida el SAST/deps ya realizado.

> Criterio de aceptación: análisis ejecutados, hallazgos revisados y **sin vulnerabilidades críticas/altas pendientes de corrección**.  
> En WEB_MINERA el análisis **sí se ejecutó**, pero quedan **hallazgos altos en dependencias** → dictamen **condicionado** (no “libre de vulnerabilidades”).

### 12.1 Auditoría OWASP Top 10:2025 — WEB_MINERA

| Código OWASP 2025 | Vulnerabilidad | Método de verificación | Mecanismo de mitigación observado | Estado |
|---|---|---|---|---|
| A01:2025 | Broken Access Control | Revisión `AuthContext.require`, matriz de permisos, routers, políticas RLS en `database/supabase_compile.sql`, tests `test_permissions.py` / API 401 | Autorización en backend; UI no es la única barrera; RLS en tablas web; sin registro público | **Listo** (mitigado; residual: ampliar pruebas multi-rol QA) |
| A02:2025 | Security Misconfiguration | Revisión CORS (`application_factory`), `.env.example`, `APP_ENV`, Dockerfiles, `.gitignore` | CORS limitado a orígenes conocidos; secretos vía env; `.env` ignorado | **Listo** (con hallazgo SEC-004 menor: `/docs` FastAPI por defecto) |
| A03:2025 | Software Supply Chain Failures | `pip-audit -r requirements/base.txt`; `npm audit --omit=dev`; lockfiles; workflows CI | Lockfiles + CI; **vulnerabilidades altas detectadas** en deps (ver SEC-001/002) | **Listo (auditado)** — remediación de deps **pendiente** |
| A04:2025 | Cryptographic Failures | Revisión transmisión (HTTPS Supabase), tokens en sesión, ausencia de secretos en git | TLS hacia Supabase; `service_role` no en frontend; JWT/sesión vía Auth | **Listo** (con hallazgo SEC-003: credencial demo en código) |
| A05:2025 | Injection | Ruff; revisión gateway Supabase/PostgREST; validación Zod login; sin SQL concatenado en dominio | Acceso a datos vía cliente tipado/filtros; validación de entradas en formularios críticos | **Listo** (recomendado complementar con Semgrep/Sonar) |
| A06:2025 | Insecure Design | Arquitectura hexagonal + reglas de dominio + permisos + ausencia de auto-registro | Seguridad en diseño: puertos, casos de uso, invariantes de negocio | **Listo** |
| A07:2025 | Authentication Failures | Flujos login/logout/`/me`, invite/activate, tests integración auth, demo login | Auth Supabase + sesión; rechazo de credenciales inválidas; no hay `/register` público | **Listo** (demo local solo para PMV; desactivar en prod) |
| A08:2025 | Software/Data Integrity Failures | CI GitHub Actions; `package-lock.json`; requirements; compose reproducible | Pipelines de test/lint; artefactos con lockfile | **Listo** (parcial: sin firma de artefactos / provenance avanzada) |
| A09:2025 | Security Logging & Alerting Failures | Revisión `audit_log` en `PlatformService`; handler de errores genérico | Eventos de negocio auditables; errores 500 sin stack al cliente | **Listo** (parcial: alertas operativas centralizadas no desplegadas) |
| A10:2025 | Mishandling of Exceptional Conditions | `register_error_handlers`, `DomainError`, tests 401/errores controlados | Excepciones de dominio → HTTP tipado; fallo no expone detalle interno | **Listo** |

### 12.2 Restricciones técnicas adicionales (Factor +) — WEB_MINERA

| Tipo | Especificación | Método | Evidencia | Estado |
|---|---|---|---|---|
| Diseño | Arquitectura hexagonal | Inspección módulos/imports + tests aislamiento | Secciones 1–11 de este documento; `test_architecture_isolation.py`; `isolation.test.ts` | **Listo** |
| Implementación | Stack + linters | Ruff, ESLint, Pytest, Vitest | Ruff: *All checks passed*; ESLint: 0 errors (1 warning hooks); CI `backend-ci` / `frontend-ci` | **Listo** |
| Interfaz y API | Contratos OpenAPI / endpoints | FastAPI genera OpenAPI en `/openapi.json` y `/docs` | App FastAPI en `composition/application_factory`; routers `/api/v1/*` | **Listo** |
| Despliegue | Docker + secretos fuera del código | Revisión `compose.yaml`, Dockerfiles, `.env.example` | `backend/Dockerfile`, `frontend/Dockerfile`, `compose.yaml`, `docker/nginx/` | **Listo** |
| Gestión de secretos | No versionar claves privadas | `.gitignore`, `git check-ignore`, revisión repo | `.env` / `backend/.env` ignorados; solo `.env.example` y anon key pública | **Listo** (SEC-003: password demo en código — ver hallazgos) |
| Control de acceso | AuthZ + RLS | Código + SQL + tests | `AuthContext`, permisos, RLS en `database/supabase_compile.sql` | **Listo** |

### 12.3 Registro de hallazgos de seguridad (WEB_MINERA)

| ID | Plataforma | OWASP | Descripción | Severidad | Acción correctiva | Estado |
|---|---|---|---|---|---|---|
| SEC-001 | WEB_MINERA | A03 | `npm audit --omit=dev`: 5 vulnerabilidades (4 high, 1 critical) en cadena Next/sharp/postcss/source-map-js/zod | Crítica / Alta | Actualizar `next` y dependencias (`npm audit fix` / bump controlado); re-ejecutar audit | **Pendiente remediación** |
| SEC-002 | WEB_MINERA | A03 | `pip-audit`: hallazgos en `python-multipart`, `starlette`, `orjson`, `python-jose`, `pyasn1`, `ecdsa` | Alta | Subir versiones en `requirements/base.txt` (p. ej. multipart≥0.0.31, starlette acorde a FastAPI) y re-auditar | **Pendiente remediación** |
| SEC-003 | WEB_MINERA | A04 / A07 | Credenciales demo (`DEMO_PASSWORD`) embebidas en `platform.py` / catálogo frontend para PMV | Media | Condicionar demo a `APP_ENV!=production` o feature flag; rotar si se expuso en prod | **Pendiente remediación** (aceptable solo en demo) |
| SEC-004 | WEB_MINERA | A02 | Documentación OpenAPI `/docs` habilitada por defecto en FastAPI | Baja | Deshabilitar `docs_url`/`redoc_url` cuando `APP_ENV=production` | **Pendiente remediación** |

**Nota:** Si una herramienta no reporta un tipo de fallo, **no** se afirma que el sistema esté libre de vulnerabilidades. Semgrep, SonarQube y ZAP quedan como mejora del plan de evolución.

### 12.4 Dictamen Factor + (alcance WEB_MINERA)

| Plataforma | SAST ejecutado | Dependencias analizadas | Restricciones verificadas | Vulnerabilidades críticas/altas pendientes | Dictamen |
|---|---|---|---|---|---|
| APP_MINERA | Pendiente | Pendiente | Pendiente | Pendiente | **Pendiente** (fuera de este repo) |
| WEB_MINERA | **Sí** (Ruff + ESLint + revisión manual) | **Sí** (`pip-audit` + `npm audit`) | **Sí** (hexagonal, Docker, secretos, OpenAPI, RLS/AuthZ) | **Sí — SEC-001 y SEC-002** | **Condicionado / en remediación** |

**Conclusión Factor + (WEB_MINERA):** la auditoría de seguridad y restricciones técnicas **se ejecutó y documentó**. Controles de acceso, diseño, despliegue y secretos de entorno están **Listos**. El dictamen **no es de cierre pleno** mientras existan vulnerabilidades **críticas/altas** de cadena de suministro sin corregir.

---

## 13. ACTIVIDAD 5 — Consolidación FURPS+ e índice \(IC_P\) (WEB_MINERA)

Fórmula:

\[
IC_P = \sum (C_i \times W_i)
\]

Donde \(C_i\) es el % de cumplimiento del factor y \(W_i\) su peso.  
**Estimación basada en evidencias disponibles solo para WEB_MINERA** (no incluye APP_MINERA). Los valores se actualizarán cuando se completen capturas funcionales formales y la remediación SEC-001/002.

### 13.1 Matriz 5.1 — Cuadro de mando (WEB_MINERA)

| Factor FURPS+ | Peso \(W_i\) | Cumplimiento \(C_i\) (%) | Puntaje ponderado (\(C_i \times W_i\)) | Brecha | Acción de evolución |
|---|---|---|---|---|---|
| F — Funcionalidad | 30 % | **75** | **22.5** | Faltan capturas/cierre formal de todas las fichas del informe funcional | Completar `Document/informe-pruebas-funcionales-web.md` + `evidencias/web/` |
| U — Usabilidad | 15 % | **60** | **9.0** | Sin auditoría formal de contraste/a11y | Evaluar UI admin; contrastes; navegación teclado |
| R — Confiabilidad | 15 % | **65** | **9.75** | Sin medición prolongada de disponibilidad/MTTR | Pruebas de fallo/recuperación; health checks en despliegue |
| P — Rendimiento | 15 % | **70** | **10.5** | Solo latencia `/health` local; sin k6/JMeter de carga | Ejecutar k6/JMeter en endpoints críticos |
| S — Soportabilidad | 10 % | **90** | **9.0** | Mejoras menores (más use cases dedicados) | Mantener aislamiento hexagonal + cobertura tests |
| \+ — Seguridad | 15 % | **72** | **10.8** | Deps con CVEs altas; demo password; `/docs` en prod | Remediar SEC-001…004; re-auditar |
| **TOTAL** | **100 %** | — | **\(IC_P\) ≈ 71.6 %** | Índice calculable con supuestos WEB | Completar remediaciones y pruebas Inc. 3 |

### 13.2 Interpretación del índice

| Índice | Nivel |
|---|---|
| ≥ 90 % | Excelente |
| ≥ 80 % y < 90 % | Bueno |
| ≥ 70 % y < 80 % | **Aceptable** ← WEB_MINERA (~71.6 %) |
| < 70 % | Requiere mejoras |

Escala **propuesta del proyecto**, no normativa oficial FURPS+.

### 13.3 Plan de evolución (prioridad WEB_MINERA)

| Prioridad | Área | Actividad | Indicador | Plataforma |
|---|---|---|---|---|
| Alta | Seguridad | Actualizar deps (`npm`/`pip`) y re-ejecutar audits | 0 críticas/altas pendientes en alcance | WEB_MINERA |
| Alta | Funcionalidad | Cerrar fichas funcionales con capturas reales | 100 % RF aplicables con evidencia | WEB_MINERA |
| Alta | Auth demo | Desactivar bypass demo en producción | `APP_ENV=production` sin `DEMO_PASSWORD` activo | WEB_MINERA |
| Media | Rendimiento | k6/JMeter en login/lotes | p95 dentro de umbral acordado | WEB_MINERA / backend |
| Media | Usabilidad | Revisión a11y/contraste del panel | Criterios aplicables cumplidos | WEB_MINERA |
| Media | Confiabilidad | Fallo de red/API y recuperación UI | Comportamiento controlado documentado | WEB_MINERA |
| Media | Soportabilidad | Mantener SAST en CI + Semgrep opcional | Pipeline verde + informe actualizado | WEB_MINERA |
| Planificación | Incremento 3 | Definir RF y criterios antes de evaluar | Matriz de trazabilidad actualizada | WEB_MINERA (+ APP si aplica) |

---

## 14. Resumen de estados (WEB_MINERA)

| Bloque | Antes | Después de esta auditoría |
|---|---|---|
| Factor S (hexagonal) | Evaluado conforme | **Listo / Conforme** |
| OWASP A01–A10 (auditoría) | Pendiente de auditoría | **Listo** (auditado; A03 con hallazgos abiertos) |
| Restricciones técnicas 4.2 | Pendiente de auditoría | **Listo** |
| Remediación CVEs deps | — | **Pendiente** (SEC-001, SEC-002) |
| Dictamen Factor + | Pendiente | **Condicionado** |
| FURPS+ \(IC_P\) | No calculable | **≈ 71.6 % — Aceptable** (solo WEB) |
| APP_MINERA | — | **Pendiente** (excluido) |

---

*Documento C ampliado — Factor S + Factor + (OWASP 2025) + consolidación FURPS+ · alcance WEB_MINERA · GitHub.*
