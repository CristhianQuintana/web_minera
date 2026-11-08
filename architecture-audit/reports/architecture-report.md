# Architecture Audit Report — WEB_MINERA

| Campo | Valor |
|---|---|
| Proyecto | WEB_MINERA |
| Fecha | 2026-11-07 19:49:30 -0500 |
| Commit | `d0480fe` |
| Rama | `main` |
| Resultado global | **no_conforme** |

> La ausencia de violaciones detectadas por las reglas configuradas **no** es garantía absoluta de cumplimiento arquitectónico total.

## Componente: backend

- Archivos inspeccionados: **50**
- Reglas evaluadas: **5**
- Violaciones (error/warning): **1**
- Dependencias circulares: **0**
- Resultado: **parcialmente_conforme**
- Exit code herramienta: `1`

### Reglas

- `domain-independence`: Dominio sin frameworks ni capas externas
- `application-independence`: Application sin adapters/HTTP/Supabase
- `ports-independence`: Ports sin adapters/infra/frameworks
- `hexagonal-layers`: Dirección de capas hexagonal
- `no-circular-grimp`: Sin ciclos entre módulos app.* (grimp)

### Violaciones

| Severidad | Regla | Archivo | Línea | Dependencia | Mensaje | Recomendación |
|---|---|---|---|---|---|---|
| error | `Hexagonal layer direction` | `backend/app/adapters/inbound/http/dependencies.py` | 17 | `app.composition.container` | app.adapters.inbound.http.dependencies -> app.composition.container (l.17) | Inyectar el contenedor desde el composition root (p. ej. app.state) sin que adapters importen app.composition. |

## Componente: frontend

- Archivos inspeccionados: **46**
- Reglas evaluadas: **6**
- Violaciones (error/warning): **3**
- Dependencias circulares: **0**
- Resultado: **no_conforme**
- Exit code herramienta: `3`

### Reglas

- `domain-no-ui-or-outer-layers`: Domain sin React/Next/capas externas
- `application-no-adapters-or-next`: Application sin adapters/Next/React
- `ports-no-adapters`: Ports sin adapters/composition
- `no-direct-database-from-ui`: UI sin acceso directo a BD/SDK
- `presentation-prefer-ports-over-adapters`: Presentation/App no importan adapters
- `no-circular`: Sin dependencias circulares

### Violaciones

| Severidad | Regla | Archivo | Línea | Dependencia | Mensaje | Recomendación |
|---|---|---|---|---|---|---|
| error | `presentation-prefer-ports-over-adapters` | `frontend/src/presentation/layouts/app-shell.tsx` |  | `@/adapters/outbound/api/http-client` | src/presentation/layouts/app-shell.tsx → @/adapters/outbound/api/http-client incumple presentation-prefer-ports-over-adapters | Importar desde @/composition o hooks que usen PlatformPort; no desde @/adapters/.... |
| error | `presentation-prefer-ports-over-adapters` | `frontend/src/app/(app)/profile/page.tsx` |  | `@/adapters/outbound/api/http-client` | src/app/(app)/profile/page.tsx → @/adapters/outbound/api/http-client incumple presentation-prefer-ports-over-adapters | Importar desde @/composition o hooks que usen PlatformPort; no desde @/adapters/.... |
| error | `presentation-prefer-ports-over-adapters` | `frontend/src/app/login/page.tsx` |  | `@/adapters/outbound/api/http-client` | src/app/login/page.tsx → @/adapters/outbound/api/http-client incumple presentation-prefer-ports-over-adapters | Importar desde @/composition o hooks que usen PlatformPort; no desde @/adapters/.... |

## Observaciones de acoplamiento / responsabilidades

### Hallazgos (error)

- `backend/app/adapters/inbound/http/dependencies.py:17` — **adapters-must-not-import-composition**: El adaptador inbound HTTP importa el composition root (Container).
  - Recomendación: Leer container solo desde request.app.state inyectado en composition; tipar Depends con Protocol/callable sin importar Container.
- `frontend/src/app/(app)/profile/page.tsx:3` — **presentation-prefer-ports-over-adapters**: UI importa adaptador concreto @/adapters/outbound/api/http-client
  - Recomendación: Usar @/composition o un hook sobre PlatformPort; tipar errores vía dominio/ports.
- `frontend/src/app/login/page.tsx:4` — **presentation-prefer-ports-over-adapters**: UI importa adaptador concreto @/adapters/outbound/api/http-client
  - Recomendación: Usar @/composition o un hook sobre PlatformPort; tipar errores vía dominio/ports.
- `frontend/src/presentation/layouts/app-shell.tsx:4` — **presentation-prefer-ports-over-adapters**: UI importa adaptador concreto @/adapters/outbound/api/http-client
  - Recomendación: Usar @/composition o un hook sobre PlatformPort; tipar errores vía dominio/ports.

### Observaciones (no fallan por LOC sola)

- `backend/app/application/services/platform.py` — PlatformService concentra muchos casos de uso; riesgo de god-service. (tamaño actual: 1215 líneas; el tamaño solo contextualiza, no define defecto).
  - Evaluar split por bounded contexts manteniendo DataGatewayPort.
- `backend/app/adapters/inbound/http/routers.py` — Router HTTP amplio: mezcla superficie API; acoplamiento de presentación inbound. (tamaño actual: 511 líneas; el tamaño solo contextualiza, no define defecto).
  - Partir routers por recurso si crece el churn.
- `backend/app/adapters/outbound/supabase/client.py` — Gateway Supabase monolítico implementa el puerto unificado. (tamaño actual: 332 líneas; el tamaño solo contextualiza, no define defecto).
  - Aceptable como adaptador; vigilar que application no lo importe (ya vetado).
- `frontend/src/presentation/modules/resource-page.tsx` — ResourcePage mezcla listado, detalle, create y export en un módulo UI. (tamaño actual: 503 líneas; el tamaño solo contextualiza, no define defecto).
  - Observación de cohesión UI; no es violación hexagonal por sí sola.

## Servicio de estimación (ML)

- Conformidad arquitectónica: **conforme**
- Nota: La conformidad modular NO demuestra precisión ni reproducibilidad analítica del modelo (MAE/RMSE/R²). El estimador actual es heurístico.

| Check | OK | Detalle |
|---|---|---|
| `domain_estimator_exists` | sí | ml/domain/services/estimator.py |
| `application_use_case_exists` | sí | ml/application/use_cases/estimate.py |
| `composition_wiring_exists` | sí | ml/composition/__init__.py |
| `http_adapter_exists` | sí | ml/adapters/inbound/http/main.py |
| `unit_test_exists` | sí | ml/tests/unit/test_estimator.py |
| `domain_free_of_ml_frameworks` | sí | imports=['typing']; forbidden_hits=[] |
| `model_version_identified` | sí | ExpectedQuantityEstimator.version == '1.0.0' |
| `input_output_contract` | sí | EstimateExpectedQuantity.execute(features: dict) -> dict |
| `use_case_depends_on_domain_not_fastapi` | sí | use case importa estimador de dominio |
| `adapter_uses_composition` | sí | HTTP adapter cablea composition |
| `adapter_has_pydantic_request_model` | sí | EstimateRequest como contrato de borde HTTP |
| `reproducible_unit_test` | sí | ml/tests/unit/test_estimator.py |
| `test_input_fixture` | sí | features de prueba en test_estimator.py |

## Cómo reproducir

```bash
python architecture-audit/scripts/run_architecture_audit.py
```

Configs: `architecture-audit/configs/backend-contracts.ini`, `architecture-audit/configs/frontend-rules.cjs`
