# ML

Servicio independiente en `ml/`. Estima cantidad esperada y produce señales revisables.
MLflow queda aislado como infraestructura (`ml/infrastructure/mlflow`).

## Persistencia (`ml_inferences`)

1. Aplicar `database/migrations/0008_ensure_ml_inferences.sql` en Supabase.
2. Cargar demo: `database/seeds/dataset_ml_inferences_100.sql` (requiere lotes).
3. Backend lista/filtra por `organization_id` en `GET /api/v1/ml/inferences`.
4. Estimación: `POST /api/v1/ml/estimate/{lot_id}` → servicio `{ML_SERVICE_URL}/inference/estimate` → insert en `ml_inferences`.

Ver `Document/informe-modulo-ml.md`.
