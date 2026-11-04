# GQM y trazabilidad histórica S9 — complemento

Commit código: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## 1. Documentos S9 disponibles (incorporados por referencia; no reconstruidos)

| Documento | Ruta exacta | Uso en S11 |
|---|---|---|
| Matriz métricas GQ (Actividad 3) | `Document/actividad-3-matriz-metricas-gq-web.md` | Baseline histórico M1.x/M2.x/M3.x (fecha doc 2026-10-25) |
| Evaluación arquitectura hexagonal (Act. 4) | `Document/actividad-4-evaluacion-arquitectura-hexagonal.md` | Antecedente M1.x |
| Informe pruebas funcionales web (S9) | `Document/informe-pruebas-funcionales-web.md` | Antecedente funcional |
| Informe pruebas funcionales PMV2 | `Document/INFORME_PRUEBAS_FUNCIONALES_WEB_MINERA.md` | S10/PMV2 |
| Matriz trazabilidad entrega | `Document/MATRIZ_TRAZABILIDAD_WEB_MINERA.md` (+ `.csv`) | Histórico |
| Auditoría Factor S arquitectura | `Document/auditoria-factor-s-arquitectura-hexagonal.md` | Antecedente |

## 2. Métricas S11 (solo con insumos reales de esta corrida)

| Métrica | Valor S11 | Fuente exacta | ¿Completada? |
|---|---|---|---|
| M1.1 Contaminación dominio | **0%** (0/9) | `02_ARQUITECTURA/backend/domain_contamination_s11.txt` | Sí |
| M1.2 Isolation tests | BE 5/5 (+ FE isolation en suite) | `02_ARQUITECTURA/backend/isolation_s11.txt` | Parcial vs inventario 100% módulos |
| M2.1 Cobertura funcional estricta | **0%** (0/12 aplicables Aprobado) | Matrices RF complemento | Sí (resultado crítico) |
| M2.2 Defectos abiertos | Ver hallazgos | `12_HALLAZGOS_RIESGOS/HALLAZGOS_S11.md` | Parcial |
| **M3.1 Brechas AS-IS** | **No medido** | Falta matriz AS-IS oficial revalidada archivo a archivo en S11 | **No completada** |
| **M3.2 Impacto valor** | **No medido** | Sin línea base operativa cuantitativa en insumos S11 | **No completada** |

## 3. Regla aplicada
**No se reconstruyen** valores M3.x por suposición ni se copian % de S9/S10 como si fueran medidos el 2026-11-03T23:50:00-05:00.  
M3.x permanece **No medido** hasta disponer de insumos AS-IS/valor actualizados y auditables.
