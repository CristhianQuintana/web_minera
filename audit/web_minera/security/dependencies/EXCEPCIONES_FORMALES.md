# Excepciones formales de dependencias — post remediacion PMV2

Fecha: 2026-11-03

## Python
pip-audit sobre requirements/base.txt: **No known vulnerabilities found**
(tras actualizar fastapi 0.162.0, starlette 1.3.1, python-multipart 0.0.33, orjson 3.11.6; eliminar python-jose no usado).

## npm
Next actualizado a 15.5.28. Criticas Next RCE mitigadas respecto a 15.5.4.
Residuales documentados (no se aplica audit fix --force a Next 16 / Zod 4 por breaking change):
- zod <4.6.6 (high) — migracion Zod 4 requiere plan de regresion de formularios.
- postcss transitivo de next (high) — remediacion limpia exige Next 16.
- otras moderadas en toolchain eslint/vitest.

Responsable: Desarrollador WEB
Revision: 2026-11-17
Mitigacion: formularios con limites de tamano; no aceptar CSS no confiable en server; CI npm audit en cada PR.
