# Informe: eliminación de autenticación demo — WEB_MINERA

**Fecha:** 2026-10-20  
**Objetivo:** Operar exclusivamente con usuarios reales y JWT de Supabase Auth.

## Cambios realizados

### Backend
- Eliminado bypass `DEMO_*` / `ALLOW_DEMO_AUTH` de `platform.py` y `settings.py`.
- `authenticate`, `resolve_context`, `refresh` y `logout` rechazan tokens `demo-*` y organizaciones `demo-org`.
- Login exige perfil activo con `organization_id` válido y sesión JWT emitida por Supabase.
- Las operaciones protegidas siguen filtrando por `organization_id` del actor y `AuthContext.require(...)`.

### Frontend
- Eliminados `demo-catalog.ts`, flags `demoAuthEnabled` / `NEXT_PUBLIC_ENABLE_DEMO_AUTH`.
- `http-client` solo persiste JWT reales; renueva sesión vía `/api/v1/auth/refresh`; limpia sesión en 401.
- Login sin credenciales demo; `AppShell` redirige a `/login` sin access token válido.

### Base de datos / docs
- Removido seed automático de organización demo en `bootstrap_full.sql`.
- Actualizados `APLICAR_EN_SUPABASE.md` y `docs/deployment/render-checklist.md`.
- RLS existente: políticas por `current_org_id()` / `auth.uid()` sin cambio de diseño.

### Configuración producción
- `APP_ENV=production` (ejemplo y checklist).
- No usar `ALLOW_DEMO_AUTH` en Render: **eliminar la variable** si aún está definida.

## Pruebas ejecutadas

| ID | Caso | Resultado esperado | Resultado |
|---|---|---|---|
| BE-01 | `GET /health` | 200 | OK (suite backend) |
| BE-02 | Login mock Supabase JWT | 200 + token no-demo | OK |
| BE-03 | Credenciales incorrectas | 401 | OK |
| BE-04 | Sin token → `/auth/me` | 401 | OK |
| BE-05 | Token `demo-local-cristhian` | 401 | OK |
| BE-06 | Refresh con token demo | 401 | OK |
| BE-07 | Org `demo-org` en login | 401 | OK |
| BE-08 | Rol carrier → `/users` | 403 | OK |
| FE-01 | Persistencia token demo | Rechazada | OK (vitest) |
| FE-02 | Token JWT real | Aceptado | OK (vitest) |
| FE-03 | Aislamiento hexagonal FE | Sin violaciones | OK (vitest) |
| E2E-01 | Credenciales incorrectas | Permanecer en login | Requiere app en marcha |
| E2E-02 | Login/logout real | Dashboard / login | Requiere `E2E_EMAIL` + `E2E_PASSWORD` |

## Acción requerida en Render

1. Eliminar `ALLOW_DEMO_AUTH` del servicio backend.
2. Confirmar `APP_ENV=production`.
3. Redeploy backend y frontend (clear cache si cambian `NEXT_PUBLIC_*`).
4. Crear usuario en Supabase Auth + perfil con organización piloto (`e857fa80-1678-4b27-b80f-c38f471a8931` o la org real).

## Verificación manual post-deploy

1. Login con usuario real → dashboard.
2. Login incorrecto → mensaje de error, sin token.
3. DevTools: Authorization nunca debe ser `Bearer demo-local-cristhian`.
4. Logout → redirect a `/login`.
5. Usuario de org A no ve datos de org B (RLS + filtros de aplicación).
