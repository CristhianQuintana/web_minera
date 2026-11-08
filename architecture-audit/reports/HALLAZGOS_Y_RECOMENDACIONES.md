# Resumen de hallazgos — Auditoría hexagonal WEB_MINERA

| Campo | Valor |
|---|---|
| Commit | `d0480fe` |
| Resultado global | **no_conforme** |
| Evidencia | `architecture-report.md` / `.json` / `violations.csv` / `console-evidence.txt` |

## Hallazgos reales (error)

| ID | Componente | Regla | Evidencia | Recomendación |
|---|---|---|---|---|
| AH-BE-01 | Backend | Hexagonal layers | `dependencies.py:17` → `app.composition.container` | Evitar import del composition root desde adapters; tipar `Depends` sin acoplar `Container`. |
| AH-FE-01 | Frontend | presentation → adapters | `app-shell.tsx`, `login/page.tsx`, `profile/page.tsx` → `@/adapters/.../http-client` | Exponer `ApiError`/sesión vía composition o puerto; UI solo consume ports/hooks. |

## Conformidades verificadas

- **Domain BE**: sin FastAPI/Supabase/SQLAlchemy/adapters (contratos KEPT).
- **Application BE**: sin adapters/HTTP stack (KEPT).
- **Ports BE**: sin adapters/infra (KEPT).
- **Ciclos BE**: 0 detectados.
- **Domain/Application/Ports FE**: sin violaciones en las reglas correspondientes.
- **ML**: separación domain/application/adapters, `model_version`, test reproducible; **sin** validación analítica MAE/RMSE.

## Observaciones (no defecto automático por LOC)

- `platform.py` (~1215 LOC): concentración de responsabilidades.
- `routers.py`, `supabase/client.py`, `resource-page.tsx`: cohesión/densidad a vigilar.

## Qué no se hizo

- No se “arregló” la arquitectura de negocio para forzar conforme.
- No se excluyeron las violaciones conocidas de los reportes.
- Solo se añadieron `__init__.py` marcadores donde faltaban, para que el grafo no ocultara módulos.
