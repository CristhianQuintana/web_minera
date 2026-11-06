# EV-11 — Cobertura de pruebas (WEB_MINERA)

| Campo | Valor |
|---|---|
| Evidencia | **EV-11** (prioritaria) |
| Meta | **≥ 80 %** líneas / statements (referencia de entrega) |
| Fecha medición | 2026-11-06T08:21:42-05:00 |
| Commit medido | 615cdc0ba14a88c96808b15b62b1a63275c92dba |
| Alcance | Backend FastAPI (pp/) + Frontend Next (src/) |
| Herramientas | pytest-cov  / Vitest + @vitest/coverage-v8 |

---

## 1. Resultado frente a la meta (80 %)

| Componente | Métrica | Valor | Meta 80 % | Estado | Brecha |
|---|---|---|---|---|---|
| Backend | Lines / statements (pytest-cov) | **69.49 %** | 80 % | **NO CUMPLE** | 10.51 pp por debajo |
| Frontend | Lines (Vitest v8) | **16.21 %** | 80 % | **NO CUMPLE** | 63.79 pp por debajo |
| Frontend | Branches | **71.11 %** | 80 % | **NO CUMPLE** | 8.89 pp por debajo |
| Frontend | Functions | **48.78 %** | 80 % | **NO CUMPLE** | 31.22 pp por debajo |
| Indicador simple (promedio BE lines + FE lines) | — | **42.85 %** | 80 % | **NO CUMPLE** | 37.15 pp por debajo |

### Dictamen EV-11
**Meta del 80 % no alcanzada.**  
Backend ~69 % (parcial). Frontend ~16 % líneas (crítico: pocos tests unitarios sobre UI/hooks/adapters).

---

## 2. Cómo se midió

### Backend
`	ext
cd backend
python -m pytest tests/unit tests/integration --cov=app \
  --cov-report=term-missing --cov-report=xml --cov-report=html --cov-report=json
`
- Pruebas: **51 passed**
- Paquete medido: pp/
- Artefactos: ver §4

### Frontend
`	ext
cd frontend
npx vitest run --coverage
`
- Incluye: src/**/*.test.ts
- Excluye de cobertura: pages App Router (src/app/**/page.tsx, layouts), *.test.ts, e2e
- Umbral configurado en itest.config.ts (80 %) para futuras corridas CI
- Artefactos: ver §4

---

## 3. Lectura / comparación con la meta

1. Abrir este informe (§1).
2. Comparar columnas **Valor** vs **Meta 80 %**.
3. Detalle HTML:
   - Backend: udit/web_minera/evidence/EV-11/backend_html/index.html
   - Frontend: udit/web_minera/evidence/EV-11/frontend_coverage/index.html
4. JSON máquina:
   - ackend_coverage.json / rontend_coverage-summary.json

---

## 4. Archivos de evidencia (nombres exactos)

| Archivo | Descripción |
|---|---|
| udit/web_minera/evidence/EV-11/backend_coverage_stdout.txt | Salida pytest-cov |
| udit/web_minera/evidence/EV-11/backend_coverage.xml | Cobertura XML (CI) |
| udit/web_minera/evidence/EV-11/backend_coverage.json | Cobertura JSON |
| udit/web_minera/evidence/EV-11/backend_html/index.html | Informe HTML backend |
| udit/web_minera/evidence/EV-11/frontend_coverage_stdout.txt | Salida Vitest coverage |
| udit/web_minera/evidence/EV-11/frontend_coverage-summary.json | Resumen FE |
| udit/web_minera/evidence/EV-11/frontend_coverage/ | HTML/LCOV FE |
| Document/EV-11_COBERTURA_PRUEBAS.md | Este reporte |

---

## 5. Principales huecos (para plan de cierre a 80 %)

### Backend (prioridad)
- pp/adapters/outbound/supabase/client.py (~26 %)
- pp/application/services/platform.py (~47 %)
- pp/adapters/inbound/http/routers.py (~64 %)
- Adapters email/ML parcialmente cubiertos

### Frontend (prioridad)
- presentation/layouts/app-shell.tsx, 
esource-page.tsx (0 %)
- dapters/outbound/api/* (bajo)
- shared/components/ui.tsx (~12 %)
- hooks / session-store / container (0 %)

---

## 6. Declaración
Los porcentajes anteriores fueron **medidos en esta corrida** sobre el commit indicado.  
No se declara cumplimiento del 80 %: EV-11 evidencia el estado real y la brecha.

Firma técnica: generado con pytest-cov + Vitest coverage-v8 · 2026-11-06T08:21:42-05:00
