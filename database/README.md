# Base de datos WEB_MINERA

Persistencia en Supabase (proyecto configurado en `.env` / `backend/.env`).

## Proyecto actual

- URL: `https://mxkegjxjhmlsujfjmaxw.supabase.co`
- Bootstrap completo (proyecto vacío): pegar **`bootstrap_full.sql`** en SQL Editor — ver `APLICAR_EN_SUPABASE.md`.

## Orden (incremental)

1. Migraciones móviles 0001, 0004 y 0005 (si aún no están).
2. `migrations/0006_web_platform.sql` — o pegar `supabase_compile.sql` en el SQL Editor.
3. En proyecto **nuevo**, preferir un solo run de `bootstrap_full.sql`.

## Tablas nuevas

- `invitations`
- `tolerance_rules`
- `mass_balances`
- `alerts`
- `alert_reviews`
- `ml_models`
- `ml_inferences`
- `notifications`
- `organization_settings`

## Módulo ML (producción)

Si `/api/v1/ml/inferences` falla porque la tabla no existe:

1. Ejecutar `migrations/0008_ensure_ml_inferences.sql`
2. (Opcional dataset) `seeds/dataset_ml_inferences_100.sql` — requiere lotes previos
3. Detalle: `Document/informe-modulo-ml.md`

## Columnas nuevas

- `profiles.email`, `profiles.last_activity_at`, `profiles.invitation_status`
- `audit_log.context`, `audit_log.organization_id`
- `custody_transfers.created_by`, `custody_transfers.status`, `custody_transfers.responsible`
