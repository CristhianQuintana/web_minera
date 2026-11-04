# Confiabilidad — ausencia expresa de uptime y MTTR

Commit: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## Declaración
**No existen mediciones de uptime ni de MTTR** para WEB_MINERA en el expediente S11.

| Indicador | Meta referencial previa | Medición S11 | Estado |
|---|---|---|---|
| Uptime | ≥ 99.5% (si aplica acuerdo) | — | **No medido** |
| MTTR | < 5 min (si aplica acuerdo) | — | **No medido** |
| Serie temporal / monitoring | — | — | **Ausente** |
| Rollback drill | — | — | **No ejecutado** |

Evidencia de esta declaración: este archivo + `09_PRODUCCION_CONFIABILIDAD/RESUMEN_PRODUCCION_S11.md` + hallazgo S11-H-005.

Smoke HTTP puntual (`smoke_prod_2026-11-03.txt`) **no** sustituye uptime ni MTTR.
