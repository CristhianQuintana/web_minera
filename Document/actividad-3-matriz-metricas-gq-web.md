# ACTIVIDAD 3: Matriz Operativa de Métricas e Indicadores (Nivel M — Metrics)

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Alcance medido:** **WEB_MINERA** (backend FastAPI, frontend Next.js, ML auxiliar, SQL/RLS del repo)  
**Fuera de alcance:** APP_MINERA (móvil) — no se incluye en los porcentajes  
**Repositorio:** https://github.com/CristhianQuintana/web_minera  
**Fecha de medición:** 2026-10-25  
**Fuentes:** código GitHub, pruebas automatizadas, `Document/informe-pruebas-funcionales-web.md`, auditoría hexagonal Factor S

---

## 1. Cómo se interpreta el avance

Para cada métrica se reporta:

| Campo | Significado |
|---|---|
| **Valor actual** | Lo medido hoy en WEB_MINERA |
| **Meta Inc. 1 / Inc. 2** | Umbral de la matriz GQ |
| **% avance vs meta Inc. 1** | Qué tan cerca estamos del objetivo del Incremento 1 |
| **% avance vs meta Inc. 2** | Idem Incremento 2 |
| **Estado** | Cumple / Parcial / No medible / No cumple |

**% de avance global del Nivel M (WEB)** = promedio simple de los % de avance vs meta Inc. 1 de las 6 métricas.

---

## 2. Matriz 3.1 — Definición GQ + medición WEB_MINERA

### G-01 — Arquitectura limpia / hexagonal

#### M1.1 — Índice de contaminación del dominio

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-01 / Q1.1 |
| Fórmula | \(\frac{\text{N.º clases/módulos de dominio que importan frameworks externos}}{\text{Total módulos de dominio}} \times 100\) |
| Fuente | `backend/app/domain/**`, análisis estático / `test_architecture_isolation.py` |
| Valor meta Inc. 1 | **0,0 %** |
| Valor meta Inc. 2 | **0,0 %** |
| **Valor actual WEB** | **0,0 %** |
| Evidencia | Módulos canónicos (`entities`, `value_objects`, `rules`, `services`, `exceptions`): **0/5** importan FastAPI, Supabase, SQLAlchemy, httpx o adapters. Pytest de aislamiento en verde. |
| % avance vs Inc. 1 | **100 %** |
| % avance vs Inc. 2 | **100 %** |
| Estado | **Cumple** |

> Nota: el docstring de `domain/__init__.py` menciona “FastAPI/Supabase” solo como texto; no es un import. No cuenta como contaminación.

---

#### M1.2 — Conformidad de módulos hexagonales

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-01 / Q1.2 |
| Fórmula | \(\frac{\text{Módulos conformes}}{\text{Total módulos evaluados}} \times 100\) |
| Fuente | Repositorio GitHub + matriz Factor S |
| Valor meta Inc. 1 | **100 %** |
| Valor meta Inc. 2 | **100 %** |
| **Valor actual WEB** | **100 %** (15/15) |
| Módulos evaluados | BE: domain/model, domain/service, ports inbound/outbound, adapters inbound/outbound, composition · FE: domain, ports outbound, adapters outbound, application, composition · ML: domain, ports inbound, adapters inbound |
| Evidencia | `Document/auditoria-factor-s-arquitectura-hexagonal.md`; código real (no carpetas vacías) |
| % avance vs Inc. 1 | **100 %** |
| % avance vs Inc. 2 | **100 %** |
| Estado | **Cumple** (ML outbound N/A en PMV; no se cuenta como no conforme) |

---

### G-02 — Calidad funcional verificable

#### M2.1 — Cobertura funcional con capturas

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-02 / Q2.1 |
| Fórmula | \(\frac{\text{RF con captura aprobada}}{\text{Total RF del incremento aplicables}} \times 100\) |
| Fuente | Fichas en `Document/informe-pruebas-funcionales-web.md` + carpeta `evidencias/web/` |
| Valor meta Inc. 1 | **100 %** |
| Valor meta Inc. 2 | **100 %** |
| **Valor actual WEB** | **0 %** |
| Desglose | RF planificados en informe: **14** · No aplicables a web: **3** (RF-08, RF-09, RF-I2-03) · **Aplicables: 11** · Capturas aprobadas en `evidencias/web/`: **0** (carpeta inexistente / vacía) · Evaluaciones de fichas: aún “Pendiente de ejecución” |
| Evidencia parcial | Existen fichas y pruebas automatizadas (Pytest/Vitest/Playwright), pero **no sustituyen** capturas fotográficas aprobadas exigidas por la métrica |
| % avance vs Inc. 1 | **0 %** |
| % avance vs Inc. 2 | **0 %** |
| Estado | **No cumple** (documentación lista; ejecución/capturas pendientes) |

---

#### M2.2 — Tasa de defectos funcionales

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-02 / Q2.2 |
| Fórmula | \(\frac{\text{N.º defectos funcionales detectados}}{\text{Total RF funcionales evaluados}}\) |
| Fuente | GitHub Issues + informes QA |
| Valor meta Inc. 1 | **≤ 1,0 Def/RF** |
| Valor meta Inc. 2 | **≤ 0,2 Def/RF** |
| **Valor actual WEB** | **0 Def / RF evaluados por automatización** (provisional) |
| Alcance medido | Suite automatizada reciente: backend ~30 tests OK, frontend Vitest 21 OK; E2E Playwright definidos. **No** hay Issues de defectos funcionales abiertos documentados en este workspace para WEB. |
| Limitación | Los RF de las fichas **aún no están cerrados con capturas**; la tasa formal de QA manual está **incompleta**. |
| % avance vs Inc. 1 | **70 %** (meta numérica provisionalmente cumplida en automatización; cierre QA formal pendiente) |
| % avance vs Inc. 2 | **50 %** (umbral más estricto; falta evaluación formal Inc. 2 con capturas) |
| Estado | **Parcial** |

---

### G-03 — Cierre de brechas y valor

#### M3.1 — Cobertura de brechas resueltas

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-03 / Q1? → Q3.1 |
| Fórmula | \(\frac{\text{Brechas AS-IS resueltas y verificadas}}{\text{Total brechas identificadas}} \times 100\) |
| Fuente | Matriz de trazabilidad AS-IS / TO-BE |
| Valor meta Inc. 1 | **≥ 60 %** |
| Valor meta Inc. 2 | **≥ 90 %** |
| **Valor actual WEB** | **No medible en repo** (sin matriz AS-IS/TO-BE formal versionada en `Document/` o `docs/`) |
| Avance cualitativo | WEB aporta consulta de lotes, auth, custodia/transporte, alertas, balance, usuarios — contribución al TO-BE digital, pero **sin inventario numerado de brechas** no se puede calcular el índice |
| % avance vs Inc. 1 | **0 %** (dato faltante = métrica no consolidada) |
| % avance vs Inc. 2 | **0 %** |
| Estado | **No medible / pendiente de baseline** |

---

#### M3.2 — Índice de impacto en el valor

| Campo | Contenido |
|---|---|
| Goal / Pregunta | G-03 / Q3.2 |
| Fórmula | Comparación de indicadores de valor de usuario vs línea base |
| Fuente | Dashboard, registros operativos, encuestas de satisfacción |
| Valor meta Inc. 1 | **Mejora ≥ 50 %** |
| Valor meta Inc. 2 | **Mejora ≥ 80 %** |
| **Valor actual WEB** | **No medido** (no hay línea base ni encuesta/KPI operativo registrado en el repositorio) |
| % avance vs Inc. 1 | **0 %** |
| % avance vs Inc. 2 | **0 %** |
| Estado | **No medible / pendiente** |

---

## 3. Resumen ejecutivo — % de avance WEB_MINERA

| Cód. | Métrica | Valor actual | Meta I1 | Meta I2 | Avance I1 | Avance I2 | Estado |
|---|---|---|---|---|---|---|---|
| M1.1 | Contaminación del dominio | 0,0 % | 0,0 % | 0,0 % | **100 %** | **100 %** | Cumple |
| M1.2 | Conformidad hexagonal | 100 % | 100 % | 100 % | **100 %** | **100 %** | Cumple |
| M2.1 | Cobertura funcional con capturas | 0 % | 100 % | 100 % | **0 %** | **0 %** | No cumple |
| M2.2 | Tasa defectos funcionales | ~0 Def/RF (prov.) | ≤ 1,0 | ≤ 0,2 | **70 %** | **50 %** | Parcial |
| M3.1 | Brechas AS-IS resueltas | N/D | ≥ 60 % | ≥ 90 % | **0 %** | **0 %** | No medible |
| M3.2 | Impacto en el valor | N/D | ≥ 50 % | ≥ 80 % | **0 %** | **0 %** | No medible |

### Índice de avance del Nivel M (WEB_MINERA)

\[
\text{Avance}_{I1} = \frac{100 + 100 + 0 + 70 + 0 + 0}{6} = \mathbf{45{,}0\,\%}
\]

\[
\text{Avance}_{I2} = \frac{100 + 100 + 0 + 50 + 0 + 0}{6} = \mathbf{41{,}7\,\%}
\]

| Vista | % avance |
|---|---|
| **Nivel M vs Incremento 1** | **≈ 45 %** |
| **Nivel M vs Incremento 2** | **≈ 42 %** |
| Solo G-01 (arquitectura) | **100 %** |
| Solo G-02 (funcional/QA) | **≈ 35 %** (I1) |
| Solo G-03 (brechas/valor) | **0 %** (falta baseline) |

---

## 4. Lectura gerencial

**Lo más avanzado:** arquitectura hexagonal y dominio limpio (G-01) — metas de Inc. 1 e Inc. 2 **cumplidas** en WEB_MINERA.

**Principal brecha del Nivel M:** G-02 M2.1 (capturas aprobadas) y G-03 (matriz AS-IS + medición de valor). Sin esas evidencias el Nivel Metrics no puede declararse cerrado aunque el software funcione.

**No declarar 100 % del Nivel M** hasta:

1. Ejecutar fichas y archivar capturas en `evidencias/web/` (M2.1 → 100 %).  
2. Registrar defectos/Issues y cerrar RF evaluados (M2.2 formal).  
3. Publicar matriz AS-IS/TO-BE con brechas numeradas y estado (M3.1).  
4. Definir línea base + indicador de valor (encuesta o KPI operativo) (M3.2).

---

## 5. Plan corto para subir el %

| Prioridad | Métrica | Acción | Efecto estimado en Avance I1 |
|---|---|---|---|
| Alta | M2.1 | Tomar 11×2 capturas de RF aplicables y marcar Aprobado | +16,7 pp (0→100 en M2.1) → avance global **≈ 61,7 %** |
| Alta | M3.1 | Crear matriz AS-IS/TO-BE y marcar brechas web resueltas (≥60 %) | +10 pp → **≈ 55–62 %** según cobertura |
| Media | M2.2 | Cerrar QA formal sin defectos abiertos | Consolida el 70→100 en M2.2 |
| Media | M3.2 | Encuesta corta o KPI (tiempo de consulta de lote) vs baseline | Desbloquea G-03 |

---

## 6. Conclusión

Para **WEB_MINERA**, el Nivel M (Metrics) tiene un avance aproximado del **45 %** respecto a las metas del **Incremento 1** y **42 %** respecto al **Incremento 2**.  
La arquitectura (G-01) está al **100 %**; el retraso está en **evidencia funcional con capturas** y en **métricas de brecha/valor** aún no instrumentadas.

---

*Actividad 3 — Matriz operativa GQ · medición WEB_MINERA · 2026-10-25.*
