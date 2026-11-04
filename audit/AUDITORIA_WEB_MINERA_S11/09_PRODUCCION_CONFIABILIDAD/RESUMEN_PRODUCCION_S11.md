# Produccion y confiabilidad — S11 (post-complemento)

## Smoke desplegado (2026-11-03)
Archivo: `smoke_prod_2026-11-03.txt`
- Frontend login: **200** https://web-minera-frontend.onrender.com/login
- Backend health: **200**
- /docs /openapi /redoc: **404**
- API sin auth: **401**

## Commit vs artefacto Render
Ver `../14_ENTREGA_COMPLEMENTARIA/09_DESPLIEGUE_SHA_RENDER.md`.
SHA exacto desplegado vs `3792632418da5e24b209680dc30ad7f3552a95e9`: **No verificable**.

## Confiabilidad
Ver `../14_ENTREGA_COMPLEMENTARIA/07_CONFIABILIDAD_UPTIME_MTTR.md`.
- Uptime: **No medido**
- MTTR: **No medido**
- Rollback drill: **No ejecutado**
