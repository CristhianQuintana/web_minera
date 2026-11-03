# ACTA DE CIERRE PMV2 — WEB_MINERA

| Campo | Valor |
|---|---|
| Fecha | 2026-11-03 (2026-11-03 12:05) |
| Baseline auditoria | `d9aef31569bee06c9e55e010e0537a9bcf8593a5` |
| Remediacion previa | `ad30938bedec5b3ea6618e61382749a27440b538` |
| Alcance | Incrementos 1–2 requisitos web aplicables (11) + N/A movil justificados |
| Dictamen | **APTA CON RIESGOS ACEPTADOS** |

## Resumen ejecutivo
WEB_MINERA cierra PMV2 documental y tecnico a nivel de codigo/pruebas locales ejecutadas, con remediacion de cadena de suministro Python, parche Next, timeline, transport_events, validacion Zod, contraste, rate limit, Axe login y k6 smoke. Permanecen riesgos residuales explicitos (RLS vivo, E2E autenticado, Axe autenticado, k6 de negocio, uptime) registrados en `RIESGOS_ACEPTADOS_PMV2.md`.

## Criterios
- [x] Alcance I1–I2 confirmado + N/A movil
- [x] Commit versionado y CI local (pytest/vitest/ruff) verde
- [x] pip critico/alto remediado (0 vulns)
- [x] Next parcheado; npm residual con excepcion formal
- [x] RF-05 decision B
- [x] RF-I2-02 API/UI
- [x] Timeline FE
- [x] Axe login ejecutado
- [x] k6 smoke ejecutado
- [ ] RLS JWT multi-org vivo → **riesgo aceptado**
- [ ] E2E autenticado completo → **riesgo aceptado / No verificable**
- [ ] Disponibilidad 99.5% → **No verificable aceptado**

## IC_WEB
**67.4%** (Aceptable). Detalle en INFORME_FURPS_PLUS_WEB_MINERA.md

## Firmas
- Desarrollo / agente de remediacion: emitido 2026-11-03
- QA / auditoria formal: ________________ (pendiente)
