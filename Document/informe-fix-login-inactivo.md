# Fix: «Tu cuenta está inactiva» en login real (Render)

**Fecha:** 2026-11-01  
**Síntoma en producción:** `POST /api/v1/auth/login` con usuario Auth confirmado → `403 inactive_account`.

## Causa raíz

El backend validaba solo `profiles.status == "active"` (comparación exacta) y no alineaba:

- señal `is_active` / confirmación de Auth (`email_confirmed_at`, `banned_until`)
- alias de rol `administrator` → `admin`
- perfiles con `status=inactive` e `invitation_status=active` (inconsistencia, no baja administrativa)

No intervenía el flujo demo: el token `demo-local-cristhian` sigue rechazado.

Evidencia previa al fix (producción):

```text
POST https://web-minera-backend.onrender.com/api/v1/auth/login
email=cristhian@gmail.com → 403 inactive_account
```

Auth aceptaba la contraseña (si fueran credenciales inválidas sería 401). El fallo ocurría al evaluar el perfil.

## Corrección

1. Normalización de perfil/rol (`domain/services/profile_status.py`).
2. Reconciliación de perfil confirmado en Auth con `status` inconsistente (sin rehabilitar `invitation_status=inactive|expired`).
3. Gateway: JWT de usuario cuando no hay service role; updates de actividad no tumba el login.
4. SQL de reparación: `database/seeds/repair_login_profile.sql` + `0007_profiles_update_own.sql`.

## Pruebas automatizadas

- Backend: `test_profile_status` + `test_api_health_auth` (login `administrator`/`is_active`, reconciliación, org piloto, baja por invitation).
- Frontend vitest: sin tokens demo.

## Evidencia producción (2026-11-01)

```text
POST https://web-minera-backend.onrender.com/api/v1/auth/login
→ 200 access_token JWT ES256 (issuer https://kwygymkrlwthddjijdyr.supabase.co)
→ user.role=admin
→ user.organization_id=e857fa80-1678-4b27-b80f-c38f471a8931
→ sin demo-local-cristhian / demo-org

GET /api/v1/auth/me  Authorization: Bearer <jwt>
→ 200 perfil activo

UI https://web-minera-frontend.onrender.com/login
→ redirect a /dashboard con menú admin (Usuarios, Configuración, Cerrar sesión)
```

Commits: `93cd001` (inactiva) + `306718d` (organización piloto).

**Nota:** Render usa el proyecto Supabase `kwygymkrlwthddjijdyr` (distinto del local `mxkegjxjhmlsujfjmaxw`). Ejecutar `database/seeds/repair_login_profile.sql` y `0007_profiles_update_own.sql` en ese proyecto para persistir org/status en BD. El endpoint `/dashboard` aún puede devolver 500 si faltan tablas/datos en ese proyecto; el login y `/auth/me` ya son exitosos.
