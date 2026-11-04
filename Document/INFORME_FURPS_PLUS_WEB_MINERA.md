# Informe FURPS+ WEB_MINERA — post remediacion PMV2

Fecha: 2026-11-03 | Baseline auditoria: d9aef31 | Remediacion: `ad30938bedec5b3ea6618e61382749a27440b538+`

## Linea base vs actual

| Indicador | Baseline 2026-11-03 am | Post remediacion |
|---|---|---|
| IC_WEB | ~48% | **67.4%** |
| pip-audit | 43 vulns | **0** |
| Next | 15.5.4 | **15.5.28** |
| Pytest | 51 | **52** |
| Vitest | 19 | **22** |
| Playwright | 2 pass / 2 skip | **5 pass / 2 skip** |
| Axe login | No ejecutado | **0 critical/serious** |
| k6 | No ejecutado | **health p95=16.93ms** |

## Scores (pesos F30 U15 R15 P15 S10 +15)

| Factor | Score | Justificacion breve |
|---|---|---|
| F | 72 | 11 RF con implementacion + tests unit/E2E parcial; 0/11 Aprobado estricto full-flow |
| U | 70 | Contraste tokens *-fg; Axe login limpio; AA completo de flujos auth pendientes |
| R | 55 | Rate limit + errores tipados; uptime/MTTR No verificable |
| P | 60 | k6 smoke health OK; no perfil negocio/500 VU |
| S | 88 | Dominio 0% contaminacion; ruff limpio; cov ~69% |
| + | 62 | pip limpio; Next parcheado; npm residual documentado; docs off en prod local |

`IC_WEB = 67.4%` → escala proyecto: **70–80 Aceptable** (borde).

Formula reproducible en este archivo. No copiar el 48% baseline como resultado actual.
