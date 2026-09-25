# Base de datos WEB_MINERA

La persistencia vive en el mismo proyecto Supabase que `APP_MINERA`.

## Orden

1. Migraciones móviles 0001, 0004 y 0005 (si aún no están).
2. `migrations/0006_web_platform.sql` — o pegar `supabase_compile.sql` en el SQL Editor.

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

## Columnas nuevas

- `profiles.email`, `profiles.last_activity_at`, `profiles.invitation_status`
- `audit_log.context`, `audit_log.organization_id`
- `custody_transfers.created_by`, `custody_transfers.status`, `custody_transfers.responsible`
