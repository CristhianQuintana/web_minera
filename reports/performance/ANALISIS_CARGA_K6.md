# Análisis — Prueba de carga k6 WEB_MINERA

| Campo | Valor |
|---|---|
| Script | `performance/k6/load-web-minera.js` |
| Perfil | `load` (hasta 40 VU, ~85 s) |
| BASE_URL | `http://127.0.0.1:8000` |
| Fecha (UTC) | 2026-11-08T14:44:55Z |

## Resultado consolidado (corrida corregida)

| Métrica | Valor | Meta | ¿OK? |
|---|---:|---|---|
| Requests | 7781 | — | — |
| Iteraciones | 1556 | — | — |
| HTTP failed | **0.00 %** | < 10 % | Sí |
| Checks | **100 %** | > 90 % | Sí |
| HTTP p95 | **356 ms** | < 800 ms | Sí |
| Health p95 | **545 ms** | < 800 ms | Sí |
| Login inválido p95 | 860 ms | — | Observación (pico) |
| Authz 401/429 p95 | 159 ms | — | Sí |

**Dictamen:** carga **aceptable** en el perfil ejecutado (infra + caminos auth/autorización).

## Hallazgos de análisis

1. **Latencia global p95 356 ms** — dentro del umbral de 800 ms.
2. **Rate limiting activo** — ~120 req/60s por IP+segmento (`RateLimitMiddleware`). Bajo 40 VU aparecen 429 en rutas `/api/v1/*`; se consideran respuesta esperada de protección, no caída del servicio.
3. **Negocio autenticado no medido** en esta corrida (sin `TOKEN` / `K6_EMAIL`+`K6_PASSWORD`). Para capacidad de lotes/custodia/etc. hay que reejecutar con credenciales de prueba (no versionar secretos).
4. **`/health` no basta** para declarar rendimiento de negocio; sí valida liveness bajo carga.

## Endpoints ejercidos

- `GET /health`
- `POST /api/v1/auth/login` (credenciales inválidas)
- `GET /api/v1/lots`, `/dashboard`, `/auth/me` (sin token → 401|429)

## Cómo reproducir (reporte en terminal)

```powershell
# Backend en 8000
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

# Otra terminal — raíz del repo
$env:BASE_URL="http://127.0.0.1:8000"
$env:K6_PROFILE="load"   # smoke | load | stress
npm run load:k6
# o:
.\performance\k6\run-load.ps1 -Profile load
```

Con negocio autenticado:

```powershell
$env:TOKEN="<jwt>"
# o
$env:K6_EMAIL="..."; $env:K6_PASSWORD="..."
npm run load:k6
```
