# M2.2 — Tasa de defectos funcionales (TDF) — WEB_MINERA

| Campo | Valor |
|---|---|
| Componente | WEB_MINERA (Next.js / FastAPI / Supabase) |
| Métrica GQM | M2.2 — Tasa de defectos funcionales |
| Fórmula | \( TDF = \frac{\text{N.º defectos funcionales confirmados}}{\text{N.º RF funcionales evaluados}} \) |
| Fecha de consolidación | 2026-11-07 |
| Commit evaluado (HEAD) | `d0480fe` |
| Baseline de entrega PMV2 | `bca96c2` / remediación documentada 2026-11-03 |
| Fuentes | `Document/MATRIZ_TRAZABILIDAD_WEB_MINERA.csv`, `Document/AUDIT_WEB_MINERA_HALLAZGOS.md`, `Document/INFORME_PRUEBAS_FUNCIONALES_WEB_MINERA.md`, `audit/web_minera/test-reports/**` |

---

## 0. Criterios de clasificación (obligatorios)

Se contabiliza como **defecto funcional confirmado** solo si:

1. El RF está en alcance WEB del incremento,
2. Existe comportamiento incorrecto frente al resultado esperado del RF, y
3. Fue observado con evidencia (prueba, código o reporte).

**No** se registran como defecto funcional:

| Tipo | Ejemplos en este repo |
|---|---|
| Observación técnica / deuda | Cobertura pytest 69 %, ESLint hooks, monolito `platform.py` |
| Vulnerabilidad de seguridad | SEC-WEB-01 npm residual, pip histórico, rate-limit previo |
| Funcionalidad no implementada / no evaluada | Candidatos Incremento 3 sin catálogo RF |
| Fuera de alcance WEB (N/A → APP) | RF-06, RF-08, RF-09, RF-10, RF-I2-03; upload RF-05 (Decision B) |
| Bloqueo de entorno de prueba | E2E login OK skipped sin `E2E_EMAIL`/`E2E_PASSWORD`; RLS vivo NV |

---

## 1. Requisitos funcionales evaluados

### 1.1 Totales definidos (catálogo I1 + I2)

| Incremento | RF definidos | N/A WEB (APP) | Aplicables WEB | Sometidos a evaluación funcional |
|---|---:|---:|---:|---:|
| **Incremento 1** | 12 (RF-01…RF-12) | 4 | **8** | **8** |
| **Incremento 2** | 4 (RF-I2-01…04) | 1 | **3** | **3** |
| **Total I1+I2** | **16** | **5** | **11** | **11** |

### 1.2 Identificación y resultado por RF evaluado

Detalle en `MATRIZ_RF_EVALUADOS_M2_2.csv`. Resumen:

#### Incremento 1 (8 evaluados)

| RF | Resultado | Lectura para M2.2 |
|---|---|---|
| RF-01 | **Aprobado parcial** | E2E negativos + redirect **Aprobados**; login válido **No ejecutado** (bloqueo secretos) |
| RF-02 | **Aprobado parcial** | Código + unit; E2E create **No ejecutado** |
| RF-03 | **Aprobado parcial** | Validación Zod/Pydantic en formularios clave |
| RF-04 | **Aprobado parcial** | Ubicación en detalle; GPS = APP |
| RF-05 | **Aprobado parcial** | Consulta según Decision B |
| RF-07 | **Aprobado parcial** | Gates/unit; RLS vivo = riesgo aceptado (no defecto confirmado) |
| RF-11 | **Aprobado parcial** | Drawer + timeline |
| RF-12 | **Aprobado parcial** | Roles/permisos unit |

#### Incremento 2 (3 evaluados)

| RF | Resultado | Lectura para M2.2 |
|---|---|---|
| RF-I2-01 | **Aprobado parcial** | Custodia API/UI + Zod |
| RF-I2-02 | **Aprobado parcial** | `transport_events` implementado post-remediación |
| RF-I2-04 | **Aprobado parcial** | Timeline FE consumiendo historial |

**Ningún RF evaluado de I1/I2 queda en estado Fallido** al cierre documentado.
**Ningún RF aplicable queda en No ejecutado total**: todos tienen al menos evidencia de código + unit/API o E2E parcial.

### 1.3 Incremento 3 (separado — no entra al TDF de I1/I2)

| Concepto | Estado |
|---|---|
| Catálogo RF-I3 oficial | **No definido / no formalizado** |
| Capacidades en código | Recepción, pesaje, balance calculado, alertas, auditoría, ML heurístico |
| Clasificación | Avance operativo **experimental**; **no mezclar** con resultados I1/I2 |
| Defectos M2.2 I3 | **No aplica** (no hay RF evaluados formalmente) |

---

## 2. Defectos funcionales encontrados

Registro completo: `REGISTRO_DEFECTOS_FUNCIONALES_M2_2.csv`.

### 2.1 Defectos funcionales confirmados (histórico de auditoría → remediados)

| ID | Inc. | RF | Severidad | Estado al cierre |
|---|---|---|---|---|
| WEB-DF-I1-001 (ex WEB-AUD-006) | 1 | RF-03 | Media | **Cerrado parcial** (Zod formularios principales) |
| WEB-DF-I2-001 (ex WEB-AUD-008) | 2 | RF-I2-02 | Media | **Cerrado** |
| WEB-DF-I2-002 (ex WEB-AUD-009) | 2 | RF-I2-04 / RF-11 | Media | **Cerrado** |

### 2.2 Defectos funcionales confirmados **abiertos** al consolidar M2.2

**Cero (0).**

Se declara expresamente:

> Se ejecutaron las suites funcionales/regresión documentadas (Pytest, Vitest, Playwright público/negativos) sobre el alcance WEB de los incrementos 1 y 2. **No se encuentran defectos funcionales confirmados abiertos** en el estado actual del repositorio. Los tres hallazgos funcionales históricos fueron corregidos o cerrados parcialmente antes del cierre PMV2.

### 2.3 Ítems explícitamente excluidos del numerador TDF

- Upload evidencias WEB (RF-05) → Decision B / APP.
- SEC-WEB-*, cobertura, Axe amplio, k6 negocio, RLS vivo, uptime → seguridad / técnica / no verificable.
- Funciones Inc. 3 sin RF formal → pendientes de desarrollo/formalización, no defectos.

---

## 3. Resultados de pruebas

| Suite / herramienta | Ejecutadas | Aprobadas | Fallidas | Omitidas / bloqueadas | Fecha | Evidencia |
|---|---:|---:|---:|---:|---|---|
| Pytest (backend) | 52 | 52 | 0 | 0 | 2026-11-03 | `audit/web_minera/test-reports/pytest/pytest-pmv2-summary.txt` |
| Vitest (frontend) | 22 | 22 | 0 | 0 | 2026-11-03 | `audit/web_minera/test-reports/vitest/vitest-pmv2-summary.txt` |
| Playwright (cierre PMV2) | 7 | 5 | 0 | 2 (login/logout OK sin secretos) | 2026-11-03 | `audit/web_minera/test-reports/playwright/playwright-cierre-stdout.txt` |
| Axe (login) | 1 flujo | 0 critical/serious | 0 | — | 2026-11-03 | `audit/web_minera/accessibility/axe/` (informe pruebas funcionales) |

**Commit de regresión de entrega:** documentado en `Document/INFORME_ENTREGA_FINAL_PMV2_WEB_MINERA.md` (cierre `bca96c2` + remediación).  
**Commit de consolidación M2.2:** `d0480fe` (2026-11-07) — sin reabrir defectos funcionales en dominio evaluado.

Fallos de suite automatizada atribuibles a defecto funcional de RF: **0**.

---

## 4. Cálculo TDF (por incremento, sin mezclar I3)

### Definiciones usadas

| Vista | Numerador | Denominador |
|---|---|---|
| **TDF cierre** (oficial para metas de entrega) | Defectos funcionales confirmados **abiertos** | RF WEB evaluados del incremento |
| **TDF histórico detectados** (transparencia) | Defectos confirmados hallados en auditoría (aunque luego cerrados) | RF WEB evaluados del incremento |

### Incremento 1

| Vista | Cálculo | TDF | Meta | ¿Cumple? |
|---|---|---:|---:|---|
| Cierre | \( 0 / 8 \) | **0,00** | ≤ 1,0 | **Sí** |
| Histórico detectados | \( 1 / 8 \) (WEB-DF-I1-001) | **0,125** | ≤ 1,0 | **Sí** |

### Incremento 2

| Vista | Cálculo | TDF | Meta | ¿Cumple? |
|---|---|---:|---:|---|
| Cierre | \( 0 / 3 \) | **0,00** | ≤ 0,2 | **Sí** |
| Histórico detectados | \( 2 / 3 \) (WEB-DF-I2-001, WEB-DF-I2-002) | **0,67** | ≤ 0,2 | No (informativo; remediados antes del cierre) |

### Agregado I1+I2 (referencia)

| Vista | Cálculo | TDF |
|---|---|---:|
| Cierre | \( 0 / 11 \) | **0,00** |
| Histórico | \( 3 / 11 \) | **0,27** |

**Valor reportado para GQM M2.2 en entrega de incrementos cerrados:**  
**TDF = 0,00 Def/RF** (0 defectos funcionales confirmados abiertos / 11 RF evaluados).

---

## 5. Entregables de este paquete

| Entregable | Ruta |
|---|---|
| Matriz RF evaluados | `audit/web_minera/gqm/M2_2/MATRIZ_RF_EVALUADOS_M2_2.csv` |
| Registro de defectos | `audit/web_minera/gqm/M2_2/REGISTRO_DEFECTOS_FUNCIONALES_M2_2.csv` |
| Este informe | `audit/web_minera/gqm/M2_2/INFORME_M2_2_TASA_DEFECTOS_FUNCIONALES.md` |
| Reportes de ejecución | `audit/web_minera/test-reports/pytest|vitest|playwright/` |
| Matriz de trazabilidad origen | `Document/MATRIZ_TRAZABILIDAD_WEB_MINERA.csv` |
| Hallazgos / remediación | `Document/AUDIT_WEB_MINERA_HALLAZGOS.md` |
| Decision RF-05 | `audit/web_minera/evidence/RF-05/DECISION_ALCANCE.md` |
| Informe pruebas | `Document/INFORME_PRUEBAS_FUNCIONALES_WEB_MINERA.md` |

### Limitación de evidencia fotográfica

Las fichas de `Document/informe-pruebas-funcionales-web.md` prevén capturas en `evidencias/web/`; esa carpeta **no está versionada** en el HEAD actual. La verificación M2.2 se sustenta en **reportes de suites automatizadas + matriz de trazabilidad + registro de hallazgos**, no en capturas UI formales (brecha conocida de M2.1).

---

## 6. Conclusión

| Incremento | RF evaluados | Defectos abiertos | TDF cierre | Dictamen |
|---|---:|---:|---:|---|
| 1 | 8 | 0 | **0,00** | Cumple meta ≤ 1,0 |
| 2 | 3 | 0 | **0,00** | Cumple meta ≤ 0,2 |
| 3 | 0 (no formal) | N/A | N/A | Solo avance; excluido del TDF I1/I2 |

Las pruebas correspondientes a los RF WEB de los incrementos 1 y 2 **fueron ejecutadas** (unitarias/API + E2E parcial). **No hay defectos funcionales confirmados abiertos** al consolidar esta métrica.
