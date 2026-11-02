# Informe técnico — Módulo Análisis ML (WEB_MINERA)

**Fecha:** 2026-11-02  
**Objetivo:** Dejar operativo el listado/persistencia de `ml_inferences` y cargar 100 registros simulados.

## Diagnóstico

En producción, `GET /api/v1/ml/inferences` y `GET /api/v1/ml/models` fallaban porque las tablas **no existían** en el proyecto Supabase de Render (`kwygymkrlwthddjijdyr`), aunque ya estaban definidas en `bootstrap_full.sql` / `0006_web_platform.sql`. PostgREST devolvía 404 y el backend lo traducía a 500.

## Diseño de `ml_inferences`

| Columna | Tipo | Notas |
|---|---|---|
| `id` | uuid PK | `gen_random_uuid()` |
| `organization_id` | uuid FK → organizations | aislamiento multi-tenant |
| `lot_id` | uuid FK → lots | lote analizado |
| `model_id` | uuid FK → ml_models | opcional |
| `model_version` | text | versión usada |
| `expected_quantity` | numeric | estimación |
| `observed_quantity` | numeric | recepción/observado |
| `deviation` / `deviation_percent` | numeric | calculados |
| `signal` | text | `none` \| `review_signal` |
| `features` | jsonb | entradas + metadata (`source`, mineral, etc.) |
| `created_at` | timestamptz | |

**RLS:** SELECT por `current_org_id()`; INSERT para roles operativos con la misma org.

## Archivos entregados

1. `database/migrations/0008_ensure_ml_inferences.sql` — aplicar YA en Supabase prod.
2. `database/seeds/dataset_ml_inferences_100.sql` — 100 inferencias DEMO (requiere lotes previos).
3. Ajustes backend: filtro por org, persistencia enriquecida, cliente ML con `source`.
4. UI ML: columnas legibles (lote/mineral/fuente).

## Orden de ejecución en Supabase

```text
1) 0008_ensure_ml_inferences.sql
2) (si no hay lotes) seeds/dataset_demo_220.sql
3) seeds/dataset_ml_inferences_100.sql
```

## Validación esperada

- SQL seed → `total_demo_ml_inferences = 100`
- `GET /api/v1/ml/inferences` → 200 con items
- UI `/ml` lista registros, busca por versión/señal, pagina
- `POST /api/v1/ml/estimate/{lot_id}` inserta fila; si `ML_SERVICE_URL` está vivo, `features.source = ml_service` (no `fallback`)

## Render

Configurar `ML_SERVICE_URL=https://<web-minera-ml>.onrender.com` en el backend. Sin URL o servicio caído se usa fallback marcado explícitamente (`1.0.0-fallback`).
