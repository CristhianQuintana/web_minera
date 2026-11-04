# Rendimiento — distinción infra vs negocio + plan pendiente

Commit: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## 1. Resultado ejecutado = infraestructura (NO negocio)

| Prueba | Archivo | Interpretación correcta |
|---|---|---|
| k6 `GET /health` prod | `08_RENDIMIENTO_K6/k6_s11_health_only_stdout.txt` | Disponibilidad/latencia del endpoint de salud |
| Script | `08_RENDIMIENTO_K6/k6_health_prod.js` | Smoke infra |
| Limitaciones | `08_RENDIMIENTO_K6/LIMITACIONES.txt` | Declara ausencia de carga de negocio |

**No** se presenta `/health` como validación de rendimiento de negocio (lotes, custodia, timeline, auth).

## 2. Plan de pruebas de carga pendiente (negocio)

| ID | Escenario | Precondiciones | Umbral propuesto* | Estado |
|---|---|---|---|---|
| PERF-B1 | Login + listar lotes | JWT / E2E creds | p95 < 2s @ 20 VU | **No ejecutado** |
| PERF-B2 | Detalle + timeline lote | JWT + lot_id | p95 < 2.5s @ 20 VU | **No ejecutado** |
| PERF-B3 | Alta evento transporte / custodia | JWT rol operador | p95 < 3s @ 10 VU | **No ejecutado** |
| PERF-B4 | Ramp-up 50→100→200 VU mixto | staging | error rate < 1% | **No ejecutado** |
| PERF-B5 | Stress 500 VU (si capacidad) | staging aislado | degradación documentada | **No ejecutado** |

\*Umbrales propuestos — no medidos; sujetos a acuerdo con Ops.

## 3. Artefactos a generar cuando se ejecute
- Script k6 autenticado (no commitear secretos).
- `stdout` + summary JSON por escenario.
- Actualizar matriz y hallazgo S11-H-004 → cerrado solo con evidencias.

## 4. Dictamen rendimiento S11
- Infra health: ejecutado.
- Rendimiento de negocio: **Pendiente / No ejecutado**.
