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

## Pruebas

- Unitarias de estado/rol + integración login `administrator`/`is_active`/reconciliación/bloqueo por baja.
- Tras deploy: login producción debe devolver `200` + JWT real (sin `demo-`).
