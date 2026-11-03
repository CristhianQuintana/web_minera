# Informe de seguridad — PMV2 WEB

Fecha: 2026-11-03

## Dependencias
- pip-audit: **No known vulnerabilities found** (requirements/base.txt)
- npm audit: residuales documentados (EXCEPCIONES_FORMALES.md); Next 15.5.28

## Controles
- Demo auth: rechazado en FE/BE
- /docs y /openapi.json: deshabilitados con APP_ENV=production (verificado local 404)
- Rate limiting: RateLimitMiddleware 120/min
- service_role: no en frontend; vacio en .env local auditado (solo presencia de claves)

## OWASP
Ver security/owasp/MATRIZ_OWASP_2025.md (actualizar estados con remediacion pip/next).

## RLS
Politicas en migraciones SQL. Prueba JWT multi-org: **No verificable** en esta corrida → riesgo aceptado WEB-AUD-012.
