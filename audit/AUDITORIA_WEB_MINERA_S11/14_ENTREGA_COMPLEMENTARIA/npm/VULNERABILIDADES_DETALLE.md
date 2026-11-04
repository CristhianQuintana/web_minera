# Detalle npm audit — entrega complementaria S11

Resumen: {'info': 0, 'low': 0, 'moderate': 16, 'high': 2, 'critical': 2, 'total': 20}
Paquetes reportados: 20

## Plan de remediacion propuesto
1. Actualizar vitest a >=3.2.7 (o mayor que elimine tinypool vulnerable) sin pasar a breaking no validado.
2. Evaluar migracion Zod 3 -> 4.6.7 en rama aparte con regresion de formularios.
3. Next/postcss: planificar upgrade a linea parcheada compatible (evitar force a Next 16 sin plan).
4. Re-ejecutar `npm audit` tras cada bump; excepciones formales solo con dueno y fecha.

## 1. `tinypool` — severidad `critical`
- Directo: `False`
- Rango npm: `<=2.1.1`
- fixAvailable: `{'name': 'vitest', 'version': '3.2.7', 'isSemVerMajor': False}`
- nodes: `node_modules/tinypool`
- GHSA/CVE ref: `GHSA-5gmw-xhrv-c9v3` | Tinypool: Prototype Pollution gadget in worker options leads to Remote Code Execution | https://github.com/advisories/GHSA-5gmw-xhrv-c9v3 | sev=critical | range=<=2.1.0
- GHSA/CVE ref: `GHSA-85c8-ppgw-ccpr` | Tinypool: Prototype Pollution Gadget to RCE in run() options | https://github.com/advisories/GHSA-85c8-ppgw-ccpr | sev=critical | range=<2.1.2

## 2. `vitest` — severidad `critical`
- Directo: `True`
- Rango npm: `<=4.1.10`
- fixAvailable: `{'name': 'vitest', 'version': '3.2.7', 'isSemVerMajor': False}`
- nodes: `node_modules/vitest`
- GHSA/CVE ref: `@vitest/mocker` | @vitest/mocker |  | sev=critical | range=
- GHSA/CVE ref: `GHSA-5xrq-8626-4rwp` | When Vitest UI server is listening, arbitrary file can be read and executed | https://github.com/advisories/GHSA-5xrq-8626-4rwp | sev=critical | range=<3.2.6
- GHSA/CVE ref: `GHSA-82fw-gwwq-j7x9` | Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock | https://github.com/advisories/GHSA-82fw-gwwq-j7x9 | sev=moderate | range=>=2.1.0 <4.1.11
- GHSA/CVE ref: `tinypool` | tinypool |  | sev=critical | range=

## 3. `postcss` — severidad `high`
- Directo: `False`
- Rango npm: `<=8.5.22`
- fixAvailable: `{'name': 'next', 'version': '16.4.5', 'isSemVerMajor': True}`
- nodes: `node_modules/next/node_modules/postcss`
- GHSA/CVE ref: `GHSA-qx2v-qp2m-jg93` | PostCSS has XSS via Unescaped </style> in its CSS Stringify Output | https://github.com/advisories/GHSA-qx2v-qp2m-jg93 | sev=moderate | range=<8.5.10
- GHSA/CVE ref: `GHSA-6g55-p6wh-862q` | PostCSS: Arbitrary file read and information disclosure via attacker-controlled sourceMappingURL in CSS comments | https://github.com/advisories/GHSA-6g55-p6wh-862q | sev=high | range=<=8.5.11
- GHSA/CVE ref: `GHSA-fxqj-rqcc-2cmp` | PostCSS: incomplete fix of GHSA-6g55-p6wh-862q — attacker-controlled sourceMappingURL reads arbitrary .map files when `from` is unset | https://github.com/advisories/GHSA-fxqj-rqcc-2cmp | sev=moderate | range=<=8.5.22
- GHSA/CVE ref: `GHSA-r28c-9q8g-f849` | PostCSS: Path Traversal in Previous Source Map Auto-Loading (sourceMappingURL) leads to Arbitrary .map File Disclosure | https://github.com/advisories/GHSA-r28c-9q8g-f849 | sev=high | range=<=8.5.17

## 4. `zod` — severidad `high`
- Directo: `True`
- Rango npm: `<4.6.6`
- fixAvailable: `{'name': 'zod', 'version': '4.6.7', 'isSemVerMajor': True}`
- nodes: `node_modules/zod`
- GHSA/CVE ref: `GHSA-mrhx-c7xc-m3w5` | Zod can exhaust memory while validating oversized constrained collections | https://github.com/advisories/GHSA-mrhx-c7xc-m3w5 | sev=high | range=<4.6.6

## 5. `@eslint-community/eslint-utils` — severidad `moderate`
- Directo: `False`
- Rango npm: `*`
- fixAvailable: `{'name': 'eslint', 'version': '4.0.0', 'isSemVerMajor': True}`
- nodes: `node_modules/@eslint-community/eslint-utils`
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=

## 6. `@eslint/config-array` — severidad `moderate`
- Directo: `False`
- Rango npm: `*`
- fixAvailable: `{'name': 'eslint', 'version': '4.0.0', 'isSemVerMajor': True}`
- nodes: `node_modules/@eslint/config-array`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 7. `@eslint/eslintrc` — severidad `moderate`
- Directo: `True`
- Rango npm: `0.0.1 || >=0.1.1`
- fixAvailable: `{'name': '@eslint/eslintrc', 'version': '0.1.0', 'isSemVerMajor': True}`
- nodes: `node_modules/@eslint/eslintrc`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 8. `@typescript-eslint/eslint-plugin` — severidad `moderate`
- Directo: `False`
- Rango npm: `*`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/eslint-plugin`
- GHSA/CVE ref: `@typescript-eslint/parser` | @typescript-eslint/parser |  | sev=moderate | range=
- GHSA/CVE ref: `@typescript-eslint/type-utils` | @typescript-eslint/type-utils |  | sev=moderate | range=
- GHSA/CVE ref: `@typescript-eslint/utils` | @typescript-eslint/utils |  | sev=moderate | range=
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=

## 9. `@typescript-eslint/parser` — severidad `moderate`
- Directo: `False`
- Rango npm: `*`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/parser`
- GHSA/CVE ref: `@typescript-eslint/typescript-estree` | @typescript-eslint/typescript-estree |  | sev=moderate | range=
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=

## 10. `@typescript-eslint/type-utils` — severidad `moderate`
- Directo: `False`
- Rango npm: `>=5.9.2-alpha.0`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/type-utils`
- GHSA/CVE ref: `@typescript-eslint/typescript-estree` | @typescript-eslint/typescript-estree |  | sev=moderate | range=
- GHSA/CVE ref: `@typescript-eslint/utils` | @typescript-eslint/utils |  | sev=moderate | range=
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=

## 11. `@typescript-eslint/typescript-estree` — severidad `moderate`
- Directo: `False`
- Rango npm: `>=6.16.0`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/typescript-estree`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 12. `@typescript-eslint/utils` — severidad `moderate`
- Directo: `False`
- Rango npm: `*`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/utils`
- GHSA/CVE ref: `@eslint-community/eslint-utils` | @eslint-community/eslint-utils |  | sev=moderate | range=
- GHSA/CVE ref: `@typescript-eslint/typescript-estree` | @typescript-eslint/typescript-estree |  | sev=moderate | range=
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=

## 13. `@vitest/mocker` — severidad `moderate`
- Directo: `False`
- Rango npm: `<=4.1.11`
- fixAvailable: `{'name': 'vitest', 'version': '3.2.7', 'isSemVerMajor': False}`
- nodes: `node_modules/@vitest/mocker`
- GHSA/CVE ref: `GHSA-82fw-gwwq-j7x9` | Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock | https://github.com/advisories/GHSA-82fw-gwwq-j7x9 | sev=moderate | range=>=2.1.0 <4.1.11
- GHSA/CVE ref: `GHSA-qxg6-89mg-rqv8` | Vitest: Code injection via unauthenticated manual mock registration | https://github.com/advisories/GHSA-qxg6-89mg-rqv8 | sev=moderate | range=>=2.1.0-beta.7 <4.1.12

## 14. `eslint` — severidad `moderate`
- Directo: `True`
- Rango npm: `0.7.1 - 2.0.0-rc.1 || >=4.1.0`
- fixAvailable: `{'name': 'eslint', 'version': '4.0.0', 'isSemVerMajor': True}`
- nodes: `node_modules/eslint`
- GHSA/CVE ref: `@eslint-community/eslint-utils` | @eslint-community/eslint-utils |  | sev=moderate | range=
- GHSA/CVE ref: `@eslint/config-array` | @eslint/config-array |  | sev=moderate | range=
- GHSA/CVE ref: `@eslint/eslintrc` | @eslint/eslintrc |  | sev=moderate | range=
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 15. `eslint-config-next` — severidad `moderate`
- Directo: `True`
- Rango npm: `>=10.2.1-canary.2`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/eslint-config-next`
- GHSA/CVE ref: `@typescript-eslint/eslint-plugin` | @typescript-eslint/eslint-plugin |  | sev=moderate | range=
- GHSA/CVE ref: `@typescript-eslint/parser` | @typescript-eslint/parser |  | sev=moderate | range=
- GHSA/CVE ref: `eslint` | eslint |  | sev=moderate | range=
- GHSA/CVE ref: `eslint-plugin-import` | eslint-plugin-import |  | sev=moderate | range=
- GHSA/CVE ref: `eslint-plugin-jsx-a11y` | eslint-plugin-jsx-a11y |  | sev=moderate | range=
- GHSA/CVE ref: `eslint-plugin-react` | eslint-plugin-react |  | sev=moderate | range=

## 16. `eslint-plugin-import` — severidad `moderate`
- Directo: `False`
- Rango npm: `>=1.15.0`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/eslint-plugin-import`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 17. `eslint-plugin-jsx-a11y` — severidad `moderate`
- Directo: `False`
- Rango npm: `>=6.5.0`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/eslint-plugin-jsx-a11y`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 18. `eslint-plugin-react` — severidad `moderate`
- Directo: `False`
- Rango npm: `>=7.23.0`
- fixAvailable: `{'name': 'eslint-config-next', 'version': '12.0.4', 'isSemVerMajor': True}`
- nodes: `node_modules/eslint-plugin-react`
- GHSA/CVE ref: `minimatch` | minimatch |  | sev=moderate | range=

## 19. `minimatch` — severidad `moderate`
- Directo: `False`
- Rango npm: `<11.0.1`
- fixAvailable: `{'name': '@eslint/eslintrc', 'version': '0.1.0', 'isSemVerMajor': True}`
- nodes: `node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch, node_modules/minimatch`
- GHSA/CVE ref: `GHSA-g3hv-75wg-m249` | minimatch has potential denial of service via globparts amplification | https://github.com/advisories/GHSA-g3hv-75wg-m249 | sev=moderate | range=<11.0.1

## 20. `next` — severidad `moderate`
- Directo: `True`
- Rango npm: `9.3.4-canary.0 - 16.3.0-preview.10`
- fixAvailable: `{'name': 'next', 'version': '16.4.5', 'isSemVerMajor': True}`
- nodes: `node_modules/next`
- GHSA/CVE ref: `postcss` | postcss |  | sev=moderate | range=
