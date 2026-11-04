# Plan de remediación npm — 20 vulnerabilidades

Fuente: `VULNERABILIDADES_DETALLE.md` / `.csv` / `npm_audit_full.json`  
Commit auditado: `3792632418da5e24b209680dc30ad7f3552a95e9`

## Resumen severidades
| Severidad | Cantidad paquetes (npm audit) |
|---|---|
| critical | 2 (`tinypool`, `vitest`) |
| high | 2 (`postcss` transitivo via next, `zod`) |
| moderate | 16 (eslint stack, minimatch, next, @vitest/mocker, …) |
| **Total** | **20** |

## Plan por paquete prioritario

| Prioridad | Paquete | Severidad | Versión corregida (fixAvailable) | Acción | Riesgo | Owner | Estado |
|---|---|---|---|---|---|---|---|
| P0 | vitest (+ tinypool) | critical | vitest **3.2.7** (semver minor/patch fixAvailable) | Bump vitest a ≥3.2.7; re-correr vitest+playwright | Bajo-medio (ya se pinó 3.2.4 por oxc) | Dev FE | **Pendiente** |
| P0 | zod | high | **4.6.7** (major) | Rama aparte; migrar schemas Zod 3→4; regresión formularios | Alto (breaking) | Dev FE | **Pendiente** |
| P1 | postcss (via next) | high | next **16.4.5** (major) sugerido por npm | Evaluar Next 15.x parcheado vs salto 16; overrides postcss si seguro | Alto | Dev FE | **Pendiente** |
| P2 | next | moderate | 16.4.5 major | Incluido en plan postcss/Next | Alto | Dev FE | **Pendiente** |
| P2 | eslint / eslint-config-next / minimatch tree | moderate | npm sugiere eslint 4 / eslint-config-next 12 (ruido/major engañoso) | Actualizar toolchain ESLint alineado a Next 15; no bajar a eslint 4 | Medio | Dev FE | **Pendiente** |
| P2 | @vitest/mocker | moderate | via vitest 3.2.7 | Cae con bump vitest | Bajo | Dev FE | **Pendiente** |

## Procedimiento
1. Rama `fix/npm-audit-s11`.
2. Aplicar P0 vitest → `npm audit` + `npm test` + playwright smoke.
3. Evaluar zod 4 en rama separada.
4. Planificar Next/postcss con checklist de breaking.
5. Renovar excepciones formales solo con dueño, CVE listado y fecha de caducidad.
6. No marcar SEC-WEB-01 cerrado hasta `npm audit` sin critical/high **o** excepción firmada.

Detalle GHSA/CVE: ver `VULNERABILIDADES_DETALLE.csv`.
