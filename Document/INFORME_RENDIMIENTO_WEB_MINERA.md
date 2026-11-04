# Informe de rendimiento — PMV2 WEB

Fecha: 2026-11-03
Herramienta: k6 v0.54.0
Script: performance/k6/smoke-api.js
Target: http://127.0.0.1:8000/health
Perfil: ramp 5→20 VU, 50s

## Resultados
- Requests: 780
- RPS: ~15.5
- http_req_failed: 0%
- p50 ~10.1 ms | p90 ~14.3 ms | **p95 ~16.93 ms** | max 364.74 ms
- Umbral p95<800 ms: **CUMPLE** para /health

## Limitacion
No incluye login/lotes/custodia ni 500 VU. Ampliar perfil en revision.
Evidencia: performance/k6/k6-smoke-stdout.txt
