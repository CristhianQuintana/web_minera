# Seguridad y RLS — S11 (post-complemento)

## Ejecutado
- GET /api/v1/lots sin auth → **401** (prod) — `seguridad_probes_sin_jwt_usuario_2026-11-03.txt`
- Login credenciales demo-like → **401** (prod)
- JWT invalido → **401** (prod)
- /docs /openapi /redoc prod → **404**
- Rate limit presente en codigo
- pip-audit: **0**
- npm audit: **20** — detalle `../14_ENTREGA_COMPLEMENTARIA/npm/`

## PENDIENTE / No verificable (bloqueante)
Ver `../14_ENTREGA_COMPLEMENTARIA/04_SEGURIDAD_RLS_PENDIENTE.md`:
- RLS multi-org con JWT reales org A/B
- Acceso Storage evidencia ajena
- Manipulacion organization_id con usuario autenticado
- E2E matriz rol-accion
- SAST Semgrep / Gitleaks: No ejecutado

## Conclusiones
401 sin JWT **no demuestra** aislamiento multi-tenant. WEB-AUD-012 / S11-H-002 = **Pendiente**.
