# Contratos API `WEB_MINERA`

Base URL: `{API_ORIGIN}/api/v1`

Autenticación: cookie `access_token` (httpOnly) o header `Authorization: Bearer <jwt>`.

No existe registro público. Las cuentas se crean por invitación.

## Errores

```json
{ "error": { "code": "unauthorized", "message": "El correo o la contraseña no son correctos." } }
```

Códigos: `bad_request`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `unprocessable`, `rate_limited`, `internal`.

## Endpoints

| Método | Ruta | Roles |
| --- | --- | --- |
| GET | `/health` | público |
| POST | `/api/v1/auth/login` | público |
| POST | `/api/v1/auth/logout` | autenticado |
| POST | `/api/v1/auth/forgot-password` | público |
| POST | `/api/v1/auth/refresh` | público |
| GET | `/api/v1/auth/me` | autenticado |
| GET | `/api/v1/auth/activate?token=` | público |
| POST | `/api/v1/auth/activate` | público |
| GET | `/api/v1/dashboard` | autenticado |
| GET/POST | `/api/v1/lots` | según permiso |
| GET | `/api/v1/lots/{id}` | según permiso |
| GET | `/api/v1/lots/{id}/timeline` | según permiso |
| GET | `/api/v1/lots/export` | según permiso |
| GET/POST | `/api/v1/custody` | según permiso |
| GET | `/api/v1/custody/{id}` | según permiso |
| GET/POST | `/api/v1/transport` | según permiso |
| GET | `/api/v1/transport/{id}` | según permiso |
| GET/POST | `/api/v1/receptions` | según permiso |
| GET | `/api/v1/receptions/{id}` | según permiso |
| GET/POST | `/api/v1/weighings` | según permiso |
| GET | `/api/v1/weighings/{id}` | según permiso |
| GET | `/api/v1/mass-balance` | autenticado |
| POST | `/api/v1/mass-balance/{lot_id}/recalculate` | receptor/admin/auditor |
| GET | `/api/v1/alerts` | autenticado |
| GET | `/api/v1/alerts/{id}` | autenticado |
| POST | `/api/v1/alerts/{id}/review` | auditor/admin |
| GET | `/api/v1/audits` | admin/auditor |
| GET | `/api/v1/audits/cases/{lot_id}` | admin/auditor |
| GET | `/api/v1/ml/models` | autenticado |
| GET | `/api/v1/ml/inferences` | autenticado |
| GET | `/api/v1/ml/inferences/{id}` | autenticado |
| POST | `/api/v1/ml/estimate/{lot_id}` | admin/auditor |
| GET | `/api/v1/users` | admin |
| POST | `/api/v1/users/invite` | admin |
| POST | `/api/v1/users/{id}/resend-invite` | admin |
| POST | `/api/v1/users/{id}/deactivate` | admin |
| POST | `/api/v1/users/{id}/activate` | admin |
| GET | `/api/v1/notifications` | autenticado |
| POST | `/api/v1/notifications/{id}/read` | autenticado |
| GET | `/api/v1/settings` | autenticado |
| PUT | `/api/v1/settings` | admin |
| POST | `/api/v1/settings/tolerances` | admin |
| GET | `/api/v1/search?q=` | autenticado |
| GET | `/api/v1/evidences/{id}/url` | autenticado |
| PATCH | `/api/v1/profile` | autenticado |

Paginación: `page`, `page_size`, `q`, `sort`, `order`. Respuesta lista:

```json
{ "items": [], "page": 1, "page_size": 20, "total": 0 }
```
