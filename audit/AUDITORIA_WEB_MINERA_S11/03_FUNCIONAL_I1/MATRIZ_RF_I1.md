# Matriz funcional Incremento 1 — S11

Commit: `﻿3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: ﻿fecha_iso=2026-11-03T23:31:00-05:00

| RF | Estado S11 | Tipo de evidencia | Notas |
|---|---|---|---|
| RF-01 Autenticacion | **Parcial** | E2E negativo + redirect + probes prod 401 | Login valido/logout/expiracion: **No ejecutado** (sin E2E_EMAIL/PASSWORD) |
| RF-02 Lotes UI->DB | **No ejecutado** | Solo codigo + unit schemas | Falta E2E autenticado create/consulta |
| RF-03 Validacion FE+BE | **Parcial** | Vitest Zod + Pydantic BE | No E2E/request manipulado autenticado |
| RF-04 Geografia/mapa | **Parcial** | UI muestra lat/lon en detalle | Mapa interactivo: no evidenciado; GPS captura N/A APP |
| RF-05 Evidencias | **Parcial** | Decision B documentada; URL firmada en API | Flujo autenticado consulta/denegacion: No ejecutado |
| RF-06 QR | **N/A** (escaneo fisico APP) / consulta web **Parcial** | qr_payload en lote | Generar/escanear QR web no demostrado |
| RF-07 Lotes por rol/org | **No verificable** | Permisos dominio unit + RLS SQL | JWT multi-org vivo: No ejecutado |
| RF-08 Sync web | **N/A** | Alcance APP_MINERA offline/sync | Justificado |
| RF-09 Persistencia | **Parcial** | API/unit; sin E2E UI autenticado | Consistencia UI/API/DB no demostrada end-to-end |
| RF-10 Control acceso | **Parcial** | PermissionGate + require(); probes 401 | Matriz rol E2E: No ejecutado |
| RF-11 Detalle/timeline | **Parcial** | Codigo timeline FE + API | E2E autenticado No ejecutado |

**Cobertura funcional estricta Aprobado:** 0 / 11 aplicables (si RF-06/08 N/A y RF-06 consulta no cuenta como aplicable escaneo).
Aplicables netos I1 (excl. N/A 06 escaneo, 08): RF-01..05,07,09,10,11 = 9 → Aprobados 0.
