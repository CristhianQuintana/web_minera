# Arquitectura S11

Commit: `﻿3792632418da5e24b209680dc30ad7f3552a95e9`

## Backend
- Contaminacion dominio: **0 hits / 9 archivos = 0%** (evidencia `backend/domain_contamination_s11.txt`)
- Isolation pytest: **5 passed**
- Capas: domain / application / ports / adapters / composition verificadas por estructura e isolation test

## Frontend
- Isolation Vitest: **4 tests passed** (architecture/isolation.test.ts dentro de 22 Vitest)
- Zod en login + lotes/custodia/transporte

## ML
- Estimador **heuristico** + fallback `1.0.0-fallback`
- No dataset train/test; no MAE/RMSE/R2
- No declarar ML validado

## Conformidad hexagonal (estimacion)
Modulos evaluados BE+FE isolation: conformes en pruebas automaticas. Porcentaje formal M1.2: isolation suites OK; inventario exhaustivo de "todos los modulos" no recontado archivo a archivo en S11 → reportar **conforme en capas criticas verificadas**, no 100% absoluto sin inventario completo.
