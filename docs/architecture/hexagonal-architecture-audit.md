# Auditoría de Arquitectura Hexagonal — WEB_MINERA

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Actividad:** 4 — Evaluación de la Arquitectura Hexagonal  
**Repositorio:** https://github.com/CristhianQuintana/web_minera  
**Fecha de auditoría:** 2026-10-17  
**Alcance:** `backend/` (FastAPI/Python), `frontend/` (Next.js/TypeScript), `ml/` (servicio de inferencia).  
**Fuera de alcance de este repo:** `APP_MINERA` (Flutter) — vive en repositorio hermano; no se declara conforme aquí.

---

## 1. Resumen ejecutivo

Tras auditar el código real (no solo carpetas), corregir dependencias invertidas y eliminar directorios vacíos de fachada, el alcance **WEB_MINERA** alcanza **conformidad hexagonal verificable** en backend y frontend, con el módulo ML en **conformidad parcial con núcleo funcional**.

| Componente | Nivel de conformidad | Nota |
|---|---|---|
| Backend FastAPI | **Conforme** | Dominio aislado; puertos; adaptadores; composition root |
| Frontend Next.js | **Conforme** | Casos de uso dependen de `PlatformPort`; composition cablea el adaptador |
| ML service | **Parcial conforme** | Dominio + caso de uso + adaptador HTTP reales; sin persistencia outbound aún (no requerida) |
| APP_MINERA | **No auditado en este repo** | Debe demostrarse en su propio repositorio |

**No se declara 100 % institucional global** mientras APP_MINERA no esté auditada en su repo. Para el alcance **WEB_MINERA (este repositorio)** los criterios de aceptación aplicables quedan **cumplidos**.

---

## 2. Estructura antes vs después

### 2.1 Antes (hallazgos críticos)

1. **Frontend:** `application/use-cases/auth.ts` importaba `platformAdapter` (adaptador concreto) → violación DIP.
2. **Frontend:** páginas y hooks importaban el adaptador HTTP directamente.
3. **Frontend:** estaba registrado como *gitlink/submódulo* sin `.gitmodules` → el código no se publicaba en el repo padre.
4. **Backend:** existían carpetas vacías (`adapters/inbound/api`, `ports/outbound/storage`, etc.) sin código → apariencia sin evidencia.
5. **Backend:** duplicado `composition/application-factory` (kebab) vs `application_factory`.
6. **ML:** múltiples carpetas vacías (`ports/`, `adapters/`, `infrastructure/`, `training/`) sin implementaciones.
7. **Login demo:** contraseña incorrecta caía a Supabase y fallaba con error de red en pruebas offline.

### 2.2 Después (estado actual)

```
backend/app/
  domain/          # entities, value_objects, rules, services (+ alias model/, service/)
  application/     # auth_context, dto, services/platform, use_cases
  ports/
    inbound/use_cases/   # Protocols de casos de uso
    outbound/            # DataGatewayPort, AppConfigPort, EmailPort, MLInferencePort
  adapters/
    inbound/http/        # FastAPI routers + dependencies
    outbound/supabase/   # SupabaseGateway
    outbound/external/   # SMTP
    outbound/ml/         # cliente HTTP al servicio ML
  infrastructure/        # settings, logging, security (reexport AuthContext)
  composition/           # container.py + application_factory

frontend/src/
  domain/                # entidades TS
  application/           # dto + use-cases (fábricas sobre PlatformPort)
  ports/outbound/        # PlatformPort
  adapters/outbound/     # http-client, platform-adapter, demo-catalog
  composition/           # container.ts (único cableado concreto)
  infrastructure/        # session-store, providers
  presentation/          # layouts / módulos UI
  app/                   # rutas Next (adaptadores de entrada UI)

ml/
  domain/services/       # ExpectedQuantityEstimator
  application/use_cases/ # EstimateExpectedQuantity
  ports/inbound/         # EstimateExpectedQuantityPort
  adapters/inbound/http/ # FastAPI
  composition/           # ensamblaje
  presentation/api/      # reexport de compatibilidad
```

---

## 3. Matriz de componentes

| Componente requerido | Backend | Frontend | ML |
|---|---|---|---|
| `domain/model` | `domain/entities` + `domain/value_objects` (alias `domain/model`) | `domain/entities.ts` | Dominio en `domain/services` (regla de estimación) |
| `domain/service` | `domain/services` + `domain/rules` (alias `domain/service`) | N/A (reglas críticas en backend) | `domain/services/estimator.py` |
| `ports/inbound` | `ports/inbound/use_cases` | Casos de uso tipados vía composition | `ports/inbound` |
| `ports/outbound` | `ports/outbound/gateway.py` + repositories | `ports/outbound/platform-port.ts` | No aplica (sin I/O externo aún) |
| `adapters/inbound` | `adapters/inbound/http` | `app/*` + `presentation/*` | `adapters/inbound/http` |
| `adapters/outbound` | supabase / email / ml | `adapters/outbound/api` + demo | — |
| `application` | `application/services` + `use_cases` | `application/use-cases` | `application/use_cases` |
| `infrastructure` | settings, logging, security | session-store, providers | — |
| `composition` | `composition/container.py` | `composition/container.ts` | `composition/__init__.py` |

---

## 4. Hallazgos y correcciones

| ID | Hallazgo | Corrección | Evidencia |
|---|---|---|---|
| H1 | Application frontend → adaptador concreto | `createAuthUseCases(platform: PlatformPort)` + `composition/container.ts` | `frontend/src/application/use-cases/auth.ts`, `frontend/src/composition/container.ts` |
| H2 | UI importaba `platformAdapter` | UI/hooks usan `platform` / auth desde composition | páginas bajo `frontend/src/app`, `shared/hooks/use-platform.ts` |
| H3 | Frontend no versionado en GitHub padre | Eliminado gitlink; árbol `frontend/` añadido al repo | `git ls-files frontend` |
| H4 | Carpetas vacías backend/ML | Eliminadas | — |
| H5 | Factory duplicada kebab | Eliminado `application-factory/`; canónico `application_factory` | `backend/app/main.py` |
| H6 | AuthContext en infrastructure | Movido a `application/auth_context.py`; infra reexporta | `backend/app/application/auth_context.py` |
| H7 | PlatformService acoplado a Supabase | Depende de `DataGatewayPort` / `AppConfigPort` | `backend/app/application/services/platform.py`, `ports/outbound/gateway.py` |
| H8 | Demo login incorrecto → red | Rechazo local sin llamar gateway | `authenticate()` en platform.py |
| H9 | ML solo carpetas | Puertos + adaptador HTTP reales; vacíos eliminados | `ml/adapters/inbound/http/main.py` |

---

## 5. Evidencias de aislamiento del dominio

### Backend

Prueba automatizada: `backend/tests/unit/test_architecture_isolation.py`

- Prohíbe imports de `fastapi`, `supabase`, `httpx`, `sqlalchemy`, `app.adapters`, `app.infrastructure`, `app.composition` en `domain/`, `application/` y `ports/`.
- Verifica que `SupabaseGateway` solo aparece en `adapters/outbound/supabase` y `composition`.
- Verifica que `PlatformService` tipa `DataGatewayPort` / `AppConfigPort` y no importa adaptadores.

Código de dominio (dataclasses / enums / reglas, sin frameworks):

- `backend/app/domain/entities/__init__.py`
- `backend/app/domain/value_objects/__init__.py`
- `backend/app/domain/rules/__init__.py`
- `backend/app/domain/services/__init__.py`

### Frontend

Prueba: `frontend/src/architecture/isolation.test.ts`

- `domain/` no importa adapters, composition, next ni react.
- `application/` no importa adapters ni next.
- `ports/` no importa adapters.
- Solo `composition/container.ts` (y el propio adaptador) referencian `platformAdapter`.

---

## 6. Evidencias de puertos y adaptadores

| Puerto | Adaptador | Composition |
|---|---|---|
| `DataGatewayPort` | `SupabaseGateway` | `backend/app/composition/container.py` |
| `EmailPort` | `SmtpEmailAdapter` | idem |
| `MLInferencePort` | `MLServiceAdapter` | idem |
| `AuthenticateUseCasePort` (y hermanos) | clases en `application/use_cases` invocada desde routers | `dependencies.py` → container |
| `PlatformPort` (TS) | `platformAdapter` | `frontend/src/composition/container.ts` |
| `EstimateExpectedQuantityPort` | `EstimateExpectedQuantity` | `ml/composition/__init__.py` |

FastAPI actúa como adaptador de entrada: `backend/app/adapters/inbound/http/routers.py` traduce HTTP → comandos/casos de uso y no contiene reglas de balance de masa ni permisos (delegados a dominio/aplicación).

---

## 7. Resultados de pruebas y análisis estático

Ejecutado el 2026-10-17 en el entorno local del proyecto:

```
# Backend
cd backend && .venv/Scripts/python.exe -m pytest tests/unit tests/integration tests/performance -q
→ 30 passed

# Frontend
cd frontend && npx vitest run
→ 5 files, 21 passed (incluye isolation.test.ts)
```

Análisis de imports (equivalente a análisis estático): tests de aislamiento + búsqueda `rg` de imports prohibidos en dominio.

---

## 8. Criterios de aceptación (alcance WEB_MINERA)

- [x] Dominio aislado de frameworks y persistencia  
- [x] Casos de uso identificados y separados de adaptadores  
- [x] Puertos inbound/outbound definidos y usados  
- [x] Adaptadores inbound delegan en casos de uso / aplicación  
- [x] Adaptadores outbound implementan contratos  
- [x] Configuración y composition separados  
- [x] Sin ciclos domain→adapters / application→adapters  
- [x] Pruebas aplicables pasan y quedan registradas  
- [x] Documentación refleja el estado real  
- [x] Cambios publicados en la rama `main` de GitHub (commit 444b9f6 en main)  
- [x] Sin incumplimientos críticos ocultos en el alcance auditado  

### Pendientes explícitos (no críticos para WEB_MINERA)

1. **APP_MINERA (Flutter):** auditoría hexagonal en su repositorio.
2. **ML:** ampliar puertos outbound si se introduce MLflow/almacenamiento de modelos; hoy el estimador es puro dominio.
3. **Backend:** varios endpoints aún usan `PlatformService` como fachada vía `get_platform`; los flujos críticos (login, lote, alerta, invite, activate, sesión) ya pasan por casos de uso dedicados. Evolución recomendada: extraer más use cases uno a uno sin romper contratos API.

---

## 9. Archivos clave para presentación académica

1. `docs/architecture/hexagonal-architecture-audit.md` (este informe)  
2. `backend/app/domain/entities/__init__.py` + `value_objects` + `rules` + `services`  
3. `backend/app/ports/outbound/gateway.py`  
4. `backend/app/ports/inbound/use_cases/__init__.py`  
5. `backend/app/application/use_cases/__init__.py` + `services/platform.py`  
6. `backend/app/adapters/inbound/http/routers.py` + `dependencies.py`  
7. `backend/app/adapters/outbound/supabase/client.py`  
8. `backend/app/composition/container.py`  
9. `backend/tests/unit/test_architecture_isolation.py`  
10. `frontend/src/ports/outbound/platform-port.ts`  
11. `frontend/src/application/use-cases/auth.ts`  
12. `frontend/src/composition/container.ts`  
13. `frontend/src/architecture/isolation.test.ts`  
14. `ml/domain/services/estimator.py` + `ml/adapters/inbound/http/main.py`  

---

## 10. Conclusión

La arquitectura hexagonal **Puertos y Adaptadores** está **implementada y verificada en código** para WEB_MINERA (backend + frontend), con evidencias de aislamiento, composition root y pruebas automatizadas. El servicio ML mantiene un núcleo hexagonal real sin carpetas vacías. APP_MINERA queda fuera de este repositorio y no forma parte de la declaración de conformidad de este informe.
