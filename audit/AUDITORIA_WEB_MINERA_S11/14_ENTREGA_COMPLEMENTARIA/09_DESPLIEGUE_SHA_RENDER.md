# Despliegue — relación commit auditado ↔ artefacto Render

Commit auditado (código): `3792632418da5e24b209680dc30ad7f3552a95e9`  
Fecha: 2026-11-03T23:50:00-05:00

## Evidencia disponible
- Smoke prod: `audit/AUDITORIA_WEB_MINERA_S11/09_PRODUCCION_CONFIABILIDAD/smoke_prod_2026-11-03.txt`
  - Frontend `https://web-minera-frontend.onrender.com/login` → 200
  - Backend health → 200; docs → 404; API sin auth → 401

## Relación SHA ↔ deploy
**No verificable.** No se dispone de:
- Metadata `/version` o header con git SHA en el artefacto desplegado,
- Export/API Render que confirme el commit del release activo,
- Imagen/digest anclado al SHA `3792632418da5e24b209680dc30ad7f3552a95e9`.

## Declaración
La condición «entorno desplegado = commit auditado» se mantiene expresamente como **NO VERIFICABLE** (hallazgo S11-H-007).  
El smoke confirma disponibilidad básica, no la identidad del commit en Render.
