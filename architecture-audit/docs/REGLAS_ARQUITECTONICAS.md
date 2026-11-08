# Documentación técnica — Reglas de arquitectura hexagonal (WEB_MINERA)

## Alcance

Auditoría estática automatizada para sustentar la **Matriz 3.6.3: Hallazgos de arquitectura hexagonal**.

Componentes inspeccionados según estructura **real** del repositorio:

| Componente | Raíz | Capas presentes |
|---|---|---|
| Backend | `backend/app/` | `domain`, `application`, `ports`, `adapters`, `infrastructure`, `composition` |
| Frontend | `frontend/src/` | `domain`, `application`, `ports`, `adapters`, `composition`, `infrastructure`, `presentation`, `shared`, `config`, `app` |
| ML | `ml/` | `domain`, `application`, `ports`, `adapters`, `composition`, `presentation` |

## Marcadores de paquete Python

Varias carpetas hexagonales (`ports`, `adapters`, `infrastructure` y subpaquetes) **no tenían** `__init__.py`, por lo que Import Linter/grimp **no inspeccionaban** módulos reales (p. ej. ocultaban `dependencies → composition`).

Se añadieron `__init__.py` vacíos/marcador **solo** para visibilidad del grafo. No cambian lógica de negocio ni ocultan violaciones; al contrario, permiten detectarlas.

## Backend (Import Linter)

Config: `architecture-audit/configs/backend-contracts.ini` (espejo en `backend/.importlinter`).

| Contrato | Tipo | Justificación |
|---|---|---|
| `domain-independence` | forbidden | El núcleo no puede conocer FastAPI, Supabase, SQLAlchemy, pydantic, adapters, infrastructure, composition, ports ni application. |
| `application-independence` | forbidden | Casos de uso dependen de puertos; no de adapters ni stack HTTP/Supabase. Pydantic en DTO de application está permitido (no vetado). |
| `ports-independence` | forbidden | Los contratos no importan implementaciones ni frameworks. |
| `hexagonal-layers` | layers | Dirección: composition → adapters\|infrastructure → application → ports → domain. |
| Ciclos (grimp) | script | Detección de ciclos entre módulos `app.*`. |

### Hallazgo esperado conocido (no se excluye)

`app.adapters.inbound.http.dependencies` importa `app.composition.container`. Viola la dirección layers (adapters no debe depender del composition root). Se reporta como violación/error.

## Frontend (Dependency Cruiser)

Config: `architecture-audit/configs/frontend-rules.cjs` (entrada `frontend/.dependency-cruiser.cjs`).

| Regla | Severidad | Justificación |
|---|---|---|
| `domain-no-ui-or-outer-layers` | error | Domain sin React/Next/adapters/composition/… |
| `application-no-adapters-or-next` | error | Application usa `PlatformPort`, no adaptadores. |
| `ports-no-adapters` | error | Puertos = contratos. |
| `no-direct-database-from-ui` | error | UI no habla con Supabase/Prisma/pg. |
| `presentation-prefer-ports-over-adapters` | error | Pages/layouts no importan `@/adapters/...` directamente. |
| `no-circular` | error | Sin ciclos. |

### Hallazgos esperados conocidos (no se excluyen)

Varias páginas bajo `src/app` importan `@/adapters/outbound/api/http-client` (p. ej. `ApiError`, `api`, `hasAccessToken`). Son acoplamientos UI→adaptador concreto.

## Acoplamiento / responsabilidades

El script añade **observaciones** (no fallos automáticos por LOC) sobre módulos densos (`platform.py`, `routers.py`, `resource-page.tsx`, etc.), con justificación y recomendación. Un archivo largo **no** se marca defectuoso solo por líneas.

## Servicio ML de estimación

Se verifica separación domain / application / adapters, contratos dict I/O, ausencia de frameworks ML en domain, `model_version`, y test unitario reproducible.

**Importante:** conformidad modular ≠ validación analítica (MAE/RMSE/R²).

## Limitación metodológica

> Ausencia de violaciones en las reglas configuradas **no** equivale a garantía absoluta de cumplimiento arquitectónico. Reglas no cubren estilo, complejidad ciclomática completa ni semántica de negocio.

## Reproducción

```bash
# Desde la raíz del repo
python architecture-audit/scripts/run_architecture_audit.py

# Backend solo
cd backend && .venv\Scripts\lint-imports.exe --config ..\architecture-audit\configs\backend-contracts.ini

# Frontend solo
cd frontend && npx depcruise --config .dependency-cruiser.cjs src

# Pruebas de validación de reglas
backend\.venv\Scripts\python.exe -m pytest architecture-audit/tests/test_rule_validation.py -q
```

Reportes en `architecture-audit/reports/`.
