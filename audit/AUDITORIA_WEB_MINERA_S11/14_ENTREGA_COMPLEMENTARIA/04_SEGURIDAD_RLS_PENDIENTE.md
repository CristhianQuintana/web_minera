# Seguridad multi-tenant (RLS) — PENDIENTE

Commit: `3792632418da5e24b209680dc30ad7f3552a95e9` | Fecha: 2026-11-03T23:50:00-05:00

## Declaración expresa
La verificación de **RLS con JWT de dos organizaciones** (org A vs org B) y la **autorización por roles** permanece **PENDIENTE / NO VERIFICABLE** en S11.

## Qué SÍ se ejecutó (insuficiente para cierre)
- Rechazo sin JWT: `audit/AUDITORIA_WEB_MINERA_S11/05_SEGURIDAD_RLS/seguridad_probes_sin_jwt_usuario_2026-11-03.txt`
- Políticas SQL / permisos de dominio en código y unit tests (no sustituyen prueba viva multi-org)

## Qué NO se ejecutó (bloqueante WEB-AUD-012 / S11-H-002)
1. Usuario JWT org A lee/escribe solo datos org A.
2. Usuario JWT org B **no** accede a recursos org A (API + Storage evidencias).
3. Matriz rol × acción (admin/operador/consulta) en UI y API.
4. Manipulación de `organization_id` en payload con sesión válida → denegación.

## Condición de cierre
Disponer de dos usuarios reales (o de staging) con JWT distintos por organización, ejecutar la matriz y adjuntar logs/capturas por caso. Hasta entonces: **Pendiente**.
