# Produccion y confiabilidad — S11

## Smoke desplegado (2026-11-03)
- Frontend login: **200** https://web-minera-frontend.onrender.com/login
- Backend health: **200**
- /docs /openapi /redoc: **404** (alineado politica production)
- API sin auth: **401**

## No verificable
- SHA exacto desplegado en Render vs `﻿3792632418da5e24b209680dc30ad7f3552a95e9`
- ALLOW_DEMO_AUTH ausente en panel Render (solo inferencia por 401 login demo-like)
- Uptime >=99.5% / MTTR <5 min: **No medido**
- Rollback drill: No ejecutado
