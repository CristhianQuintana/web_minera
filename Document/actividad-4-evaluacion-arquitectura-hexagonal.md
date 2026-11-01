# ACTIVIDAD 4: Evaluación de la Arquitectura Hexagonal en GitHub

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Repositorio institucional:** https://github.com/CristhianQuintana/web_minera  
**Equipo / alcance documentado:** WEB_MINERA (backend FastAPI, frontend Next.js, servicio ML)  
**Informe técnico de respaldo:** [`docs/architecture/hexagonal-architecture-audit.md`](../docs/architecture/hexagonal-architecture-audit.md)

---

## 1. ¿Qué se evalúa en esta actividad?

La Actividad 4 **no** se aprueba solo porque existan carpetas con nombres hexagonales. Se evalúa si el código cumple el patrón **Puertos y Adaptadores**:

| Pregunta de evaluación | Qué debe demostrar el repo |
|---|---|
| ¿El dominio es puro? | Entidades y reglas **sin** FastAPI, Supabase, SQLAlchemy, Next.js, Flutter, etc. |
| ¿Hay puertos reales? | Interfaces/contratos (`Protocol` / `interface`) con operaciones definidas, **sin** implementación de infraestructura. |
| ¿Los adaptadores delegan? | REST/UI traducen entrada y llaman casos de uso o puertos inbound; no meten reglas de negocio críticas. |
| ¿La salida está detrás de puertos? | Persistencia (Supabase/PostgreSQL), correo, ML HTTP, etc. solo en adaptadores outbound. |
| ¿Quién ensambla? | La inyección de dependencias ocurre en **composition** (o equivalente), no dentro del dominio. |
| ¿Se puede verificar? | Pruebas o análisis de imports que fallen si el dominio importa frameworks. |

**Regla de oro:** declarar *Conforme* solo con evidencia en archivos reales de GitHub (rutas + clases/interfaces + pruebas). Carpetas vacías = **No Conforme**.

---

## 2. Estructura académica vs estructura real del proyecto

La guía de la actividad muestra un árbol genérico estilo Java/Spring:

```text
/src
├── domain/
│   ├── model/
│   └── service/
├── ports/
│   ├── inbound/
│   └── outbound/
└── adapters/
    ├── inbound/
    └── outbound/
```

En WEB_MINERA **no hay un único `/src`**, porque hay varios ejecutables. Eso es válido: la hexagonalidad se aplica **por componente**, respetando el lenguaje y el framework.

| Componente ejecutable | Raíz hexagonal equivalente a `/src` | Stack |
|---|---|---|
| Backend API | `backend/app/` | FastAPI + Python + Supabase |
| Frontend web | `frontend/src/` | Next.js + TypeScript |
| Servicio ML | `ml/` | FastAPI + Python (inferencia) |
| APP_MINERA (móvil) | *Otro repositorio Flutter* | Fuera de este repo; no se declara conforme aquí |

### Correspondencia de carpetas (backend = referencia principal)

| Árbol de la actividad | Ruta real en GitHub | Contenido real |
|---|---|---|
| `/src/domain/model/` | `backend/app/domain/model/` (+ canónico en `entities/`, `value_objects/`) | Entidades y value objects |
| `/src/domain/service/` | `backend/app/domain/service/` (+ canónico en `services/`, `rules/`) | Reglas y servicios de dominio |
| `/src/ports/inbound/` | `backend/app/ports/inbound/use_cases/` | Protocols de casos de uso |
| `/src/ports/outbound/` | `backend/app/ports/outbound/` | `DataGatewayPort`, email, ML, etc. |
| `/src/adapters/inbound/rest/` | `backend/app/adapters/inbound/http/` | Routers FastAPI (adaptador REST) |
| `/src/adapters/outbound/persistence/` | `backend/app/adapters/outbound/supabase/` | Gateway concreto a Auth/DB/Storage |
| *(composition / DI)* | `backend/app/composition/` | Único lugar que instancia adaptadores |
| *(aplicación)* | `backend/app/application/` | Orquestación de casos de uso |

> **Nota sobre Spring/JPA:** el checklist académico menciona Spring Boot, Hibernate y JPA. Nuestro stack **aprobado** no los usa. El equivalente de “cero ORM/framework en dominio” se verifica contra **FastAPI, Supabase, SQLAlchemy, httpx**, no contra Spring.

---

## 3. Cómo evaluar (método paso a paso)

Usar este procedimiento al abrir el repositorio en GitHub o en local:

### Paso A — Inventario de carpetas
1. Abrir cada ruta de la matriz.
2. Confirmar que hay **archivos con código**, no solo directorios.
3. Anotar la ruta exacta que se mostrará en la presentación.

### Paso B — Desacoplamiento del dominio
1. Abrir `backend/app/domain/**/*.py`.
2. Buscar imports prohibidos: `fastapi`, `supabase`, `sqlalchemy`, `httpx`, `app.adapters`, `app.infrastructure`.
3. Evidencia automatizada:  
   `backend/tests/unit/test_architecture_isolation.py`

### Paso C — Puertos
1. **Inbound:** ¿existen Protocols/interfaces con métodos `execute(...)` u operaciones de caso de uso?  
   → `backend/app/ports/inbound/use_cases/__init__.py`
2. **Outbound:** ¿existen Protocols sin clientes Supabase/HTTP?  
   → `backend/app/ports/outbound/gateway.py`

### Paso D — Adaptadores
1. **Inbound:** ¿el router FastAPI inyecta casos de uso / container y no calcula balance de masa ni permisos?  
   → `backend/app/adapters/inbound/http/routers.py` + `dependencies.py`
2. **Outbound:** ¿`SupabaseGateway` implementa `DataGatewayPort` y solo se instancia en composition?  
   → `backend/app/adapters/outbound/supabase/client.py`  
   → `backend/app/composition/container.py`

### Paso E — Frontend (mismo criterio, otro stack)
1. Casos de uso dependen de `PlatformPort`, no del adaptador HTTP.  
   → `frontend/src/application/use-cases/auth.ts`  
   → `frontend/src/composition/container.ts`
2. Prueba: `frontend/src/architecture/isolation.test.ts`

### Paso F — Conclusión honesta
- Marcar **Conforme** solo si A–E pasan.
- Si hay pendientes (p. ej. APP_MINERA), declararlos **explícitamente**; no inventar 100 % global.

---

## 4. Matriz 4.1 — Lista de chequeo (Backend WEB_MINERA)

Matriz alineada a la actividad, con rutas **reales** del repositorio institucional.

| Componente hexagonal | Ruta en repositorio GitHub | Estado | Evidencia de desacoplamiento / hallazgo |
|---|---|---|---|
| Núcleo de dominio — modelo | `backend/app/domain/model/` (reexporta `entities/` + `value_objects/`) | **Conforme** | Dataclasses/enums de negocio sin FastAPI, Supabase ni ORM. Sin anotaciones de BD. |
| Núcleo de dominio — servicios | `backend/app/domain/service/` (reexporta `services/` + `rules/`) | **Conforme** | Reglas de lote, custodia, recepción, balance de masa en Python puro. |
| Puertos de entrada | `backend/app/ports/inbound/use_cases/` | **Conforme** | `Protocol`s (`AuthenticateUseCasePort`, `RegisterLotUseCasePort`, etc.) sin implementación de infra. |
| Puertos de salida | `backend/app/ports/outbound/gateway.py` y `.../repositories/` | **Conforme** | `DataGatewayPort`, `AppConfigPort`, `EmailPort`, `MLInferencePort` — contratos sin cliente concreto. |
| Adaptadores de entrada (REST) | `backend/app/adapters/inbound/http/` | **Conforme** | Routers FastAPI inyectan container/casos de uso (`dependencies.py`); traducen HTTP → aplicación. |
| Adaptadores de salida (persistencia) | `backend/app/adapters/outbound/supabase/` | **Conforme** | `SupabaseGateway` implementa el puerto outbound (Auth + PostgREST + Storage). Equivalente a “persistence” del checklist (no JPA: stack = Supabase/PostgreSQL). |
| Composition / DI | `backend/app/composition/container.py` | **Conforme** | Único ensamblaje de adaptadores → servicios → casos de uso. |
| Aislamiento verificable | `backend/tests/unit/test_architecture_isolation.py` | **Conforme** | Pruebas que fallan si el dominio/aplicación importan adapters o frameworks. |

### Matriz 4.1 ampliada — Frontend

| Componente | Ruta GitHub | Estado | Evidencia |
|---|---|---|---|
| Dominio UI | `frontend/src/domain/` | **Conforme** | Tipos/entidades sin Next/React en el núcleo de datos. |
| Puertos de salida | `frontend/src/ports/outbound/platform-port.ts` | **Conforme** | `PlatformPort` define login, listados, etc. |
| Casos de uso | `frontend/src/application/use-cases/auth.ts` | **Conforme** | Dependen de `PlatformPort`, no de `platformAdapter`. |
| Adaptadores salida | `frontend/src/adapters/outbound/api/` | **Conforme** | HTTP client + `platformAdapter`. |
| Adaptadores entrada (UI) | `frontend/src/app/`, `presentation/` | **Conforme** | Páginas delegan en composition (`platform` / auth use cases). |
| Composition | `frontend/src/composition/container.ts` | **Conforme** | Cablea adaptador concreto una sola vez. |
| Prueba de aislamiento | `frontend/src/architecture/isolation.test.ts` | **Conforme** | Impide que application/domain importen adapters. |

### Matriz 4.1 ampliada — ML

| Componente | Ruta GitHub | Estado | Evidencia |
|---|---|---|---|
| Dominio | `ml/domain/services/estimator.py` | **Conforme** | Estimador puro (sin FastAPI en dominio). |
| Puerto inbound | `ml/ports/inbound/` | **Conforme** | `EstimateExpectedQuantityPort`. |
| Caso de uso | `ml/application/use_cases/estimate.py` | **Conforme** | Orquesta el servicio de dominio. |
| Adaptador inbound | `ml/adapters/inbound/http/main.py` | **Conforme** | FastAPI llama al use case vía composition. |
| Adaptador outbound persistencia | — | **No aplica / parcial** | El PMV de ML no persiste modelos aún; no se inventa carpeta vacía. |

---

## 5. Qué **no** cuenta como conformidad

| Anti-patrón | Por qué falla la evaluación |
|---|---|
| Carpeta `domain/` vacía o solo `__init__.py` sin reglas | No hay núcleo de negocio demostrable. |
| Dominio que importa FastAPI/Supabase | Acoplamiento; el núcleo deja de ser portable. |
| “Puerto” que es una clase concreta con cliente HTTP | No es puerto; es adaptador mal ubicado. |
| Controller/página con reglas de balance de masa o permisos | La lógica de negocio invadió el adaptador. |
| Use case que hace `new SupabaseClient()` | Rompe inversión de dependencias. |
| Declarar 100 % incluyendo APP_MINERA sin auditar ese repo | Conformidad falsa. |

---

## 6. Resultados de verificación (evidencia ejecutable)

Ejecutados en el entorno del proyecto (registro en la auditoría técnica):

```text
# Backend — aislamiento + unit/integration
cd backend && python -m pytest tests/unit tests/integration tests/performance -q
→ 30 passed

# Frontend — incluye isolation.test.ts
cd frontend && npx vitest run
→ 21 passed

# ML
cd ml && python -m pytest tests/unit -q
→ 1 passed
```

Comandos útiles para re-auditar en la defensa:

```bash
# ¿El dominio backend importa frameworks? (debe no encontrar matches)
rg -n "fastapi|supabase|sqlalchemy|httpx|app\.adapters" backend/app/domain

# ¿Quién instancia SupabaseGateway? (solo composition + outbound)
rg -n "SupabaseGateway" backend/app
```

---

## 7. Conclusión de la Actividad 4

| Pregunta | Respuesta |
|---|---|
| ¿Cómo evaluamos nuestra arquitectura hexagonal? | Comparando el checklist académico con **rutas reales**, comprobando **código y dependencias**, y validando con **pruebas de aislamiento** — no con la sola existencia de carpetas. |
| ¿Cumple WEB_MINERA (este repo) el patrón puertos/adaptadores? | **Sí, conforme** en backend y frontend; ML **parcial conforme** con núcleo real. |
| ¿Hay un único `/src`? | No; cada ejecutable tiene su raíz (`backend/app`, `frontend/src`, `ml`). La equivalencia está en la sección 2. |
| ¿Usamos JPA/Spring? | No. El adaptador de persistencia es **Supabase/PostgreSQL** detrás de `DataGatewayPort`. |
| ¿Qué falta para conformidad institucional total? | Auditar **APP_MINERA** (Flutter) en su repositorio hermano con la misma matriz. |

### Veredicto para la entrega académica

- **Matriz 4.1 (backend + frontend en GitHub): Conforme**, con evidencias enlazables en el repositorio.  
- **No declarar 100 % del ecosistema completo** mientras APP_MINERA no esté auditada.  
- Documento técnico detallado (hallazgos, correcciones, estructura antes/después):  
  [`docs/architecture/hexagonal-architecture-audit.md`](../docs/architecture/hexagonal-architecture-audit.md)

---

## 8. Archivos a mostrar en la presentación

1. Este documento: `Document/actividad-4-evaluacion-arquitectura-hexagonal.md`  
2. `backend/app/domain/model/` y `backend/app/domain/service/`  
3. `backend/app/ports/inbound/use_cases/` y `backend/app/ports/outbound/gateway.py`  
4. `backend/app/adapters/inbound/http/routers.py`  
5. `backend/app/adapters/outbound/supabase/client.py`  
6. `backend/app/composition/container.py`  
7. `backend/tests/unit/test_architecture_isolation.py`  
8. `frontend/src/ports/outbound/platform-port.ts` + `frontend/src/composition/container.ts`  
9. `docs/architecture/hexagonal-architecture-audit.md`  

---

*Documento elaborado para la Actividad 4 — Evaluación de la Arquitectura Hexagonal en la carpeta GitHub.*
