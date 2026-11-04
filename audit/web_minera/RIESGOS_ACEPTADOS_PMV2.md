# Riesgos residuales aceptados — entrega PMV2 WEB

Fecha: 2026-11-03 (cierre de entrega)  
SHA cierre documental: `bca96c29042941c74c3d3455b050ce43634df152`  
Dictamen: **APTA CON RIESGOS ACEPTADOS — LISTO PARA ENTREGA**

| ID | Riesgo | Severidad | Estado entrega | Mitigacion / seguimiento |
|---|---|---|---|---|
| WEB-AUD-012 | RLS multi-org JWT vivo | Alta | **Aceptado para entrega** | 48 politicas en migraciones + require(); prueba viva post-entrega |
| WEB-AUD-005 | E2E autenticado | Alta | **Aceptado para entrega** | 5 E2E publicos OK; inyectar E2E_EMAIL/PASSWORD en CI |
| WEB-AUD-002 | Axe flujos auth | Media | **Aceptado para entrega** | Login 0 serious; ampliar con sesion |
| WEB-AUD-003 | k6 endpoints negocio | Media | **Aceptado para entrega** | health p95 16.93 ms; ampliar script |
| WEB-AUD-004 | Uptime/MTTR | Media | **Aceptado / No verificable** | Instrumentar monitoreo |
| SEC-WEB-01 residual | npm residual | Media | **Aceptado** | EXCEPCIONES_FORMALES.md |
| SEC-WEB-03/04 | Render live | Baja | **Aceptado parcial** | Verificado APP_ENV=production local (docs 404) |

**Aceptacion de entrega (desarrollo):** los riesgos anteriores no impiden entregar el PMV2 documental y tecnico localmente demostrado.  
**Aceptacion QA:** firma en acta.
