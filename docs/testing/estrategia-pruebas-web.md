# 3.3 Estrategia y ejecución de pruebas — componente WEB_MINERA

Este documento describe **únicamente las pruebas del sistema web**.  
Las pruebas de GPS, evidencia en campo, offline-first y sincronización pertenecen a `APP_MINERA` (móvil) y no se ejecutan en la web.

Herramientas reales del workspace:

| Capa | Herramienta | Ubicación |
| --- | --- | --- |
| Unitarias backend | Pytest | `backend/tests/unit` |
| Integración / API | Pytest + TestClient de FastAPI | `backend/tests/integration` |
| Unitarias frontend | Vitest | `frontend/src/**/*.test.ts` |
| UI / E2E | Playwright (Chromium) | `frontend/tests/e2e` |
| Rendimiento | Pytest cronometrado sobre `/health` | `backend/tests/performance` |
| Análisis estático frontend | ESLint + TypeScript (`tsc --noEmit`) | `frontend` |
| Análisis estático backend | Ruff + Pytest | `backend` |

Comandos:

```bash
cd backend && .venv\Scripts\python -m pytest -q
cd frontend && npm test && npm run typecheck && npm run lint
cd frontend && npx playwright test
```

---

## 3.3.1 Estrategia de pruebas

La estrategia web se organiza por niveles. Las unitarias verifican reglas de dominio, permisos, validación de formularios y utilidades de presentación. Las de integración/API verifican contratos HTTP (`/health`, login, `/me`, ausencia de registro público). Las UI/E2E comprueban el flujo operativo en el navegador con el usuario de demostración. Las de rendimiento miden la latencia del health check, que es el punto crítico de disponibilidad del backend.

Usuario de demostración usado en ejecución (sin Supabase):

- Correo: `cristhian@gmail.com`
- Contraseña: `Cristhian123`
- Rol: Administrador

---

## 3.3.2 Pirámide de pruebas adaptada (WEB)

```text
                    ┌─────────────────────────┐
                    │  Rendimiento / carga    │  Latencia de /health
                    └─────────────────────────┘
              ┌───────────────────────────────────┐
              │  UI / E2E (Playwright)            │  Login, lotes, logout
              └───────────────────────────────────┘
        ┌─────────────────────────────────────────────┐
        │  Integración / API (FastAPI TestClient)     │  Health, auth, 401
        └─────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────┐
  │  Unitarias (Pytest + Vitest)                            │
  │  Dominio, permisos, Zod, formato, catálogo demo         │
  └─────────────────────────────────────────────────────────┘
```

| Nivel | Objetivo | Evidencia |
| --- | --- | --- |
| 1. Unitarias | Validar reglas de lote, custodia, recepción, balance de masas, matriz de permisos, esquema de login y formato de cantidades/fechas | Salida de Pytest y Vitest |
| 2. Integración/API | Verificar `GET /health`, login demo, `/me` autenticado y rechazo de `/auth/register` | TestClient + código HTTP |
| 3. UI/E2E | Recorrer login, dashboard, listado/detalle de lotes y logout en Chromium | Playwright |
| 4. Rendimiento | Medir que `/health` responda en menos de 500 ms en entorno local | `test_health_latency.py` |

---

## 3.3.3 Casos de prueba WEB

Los identificadores `CP-01` a `CP-05` del informe general corresponden al **móvil**. En web se usan `CP-Wxx`.

| ID | Tipo | Funcionalidad | Precondición | Entrada | Resultado esperado |
| --- | --- | --- | --- | --- | --- |
| CP-W01 | UI/E2E | Login correcto | Aplicación en `/login` | `cristhian@gmail.com` / `Cristhian123` | Redirección a `/dashboard` y cards visibles |
| CP-W02 | UI/E2E | Login incorrecto | Aplicación en `/login` | Correo válido y contraseña errónea | Permanece en `/login`; no entra al panel |
| CP-W03 | Unitaria frontend | Validación de correo | Esquema Zod cargado | `correo-invalido` | Error «Formato de correo no válido.» |
| CP-W04 | Unitaria frontend | Validación de contraseña | Esquema Zod cargado | Contraseña de 3 caracteres | El esquema rechaza el valor |
| CP-W05 | API | Health check | Backend o TestClient activo | `GET /health` | HTTP 200 y `{ "status": "ok" }` |
| CP-W06 | API | Sesión demo | TestClient | Login con credenciales demo | Token `demo-local-cristhian` y rol `admin` |
| CP-W07 | UI/E2E | Consulta de lotes | Usuario autenticado | Abrir `/lots` y pulsar Detalle | Tabla con `LOT-2026-00021` y drawer «Detalle del lote» |
| CP-W08 | Unitaria backend | Registrar lote inválido | Regla de dominio | Código vacío o cantidad ≤ 0 | Excepción de dominio; no se crea el lote |
| CP-W09 | Unitaria backend | Balance de masas | Cantidad origen 100, recibida 98, tolerancia 3 % | Evaluación de regla | Estado `within_tolerance` |
| CP-W10 | Unitaria backend | Balance fuera de tolerancia | Origen 100, recibida 80, tolerancia 3 % | Evaluación de regla | Estado `review_required` |
| CP-W11 | Unitaria backend | Permisos de auditor | Rol `auditor` | Intento de `REGISTER_LOT` y `MANAGE_USERS` | Permisos denegados; sí puede `REVIEW_ALERT` |
| CP-W12 | Unitaria backend | Custodia inválida | Lote cerrado u origen = destino | Transferencia | Excepción `InvalidCustodyTransfer` |
| CP-W13 | UI/E2E | Logout | Sesión demo activa | Cerrar sesión | Redirección a `/login` |
| CP-W14 | API | Sin registro público | API levantada | `POST /api/v1/auth/register` | HTTP 404; no existe alta libre |
| CP-W15 | API | `/me` sin token | TestClient | `GET /api/v1/auth/me` | HTTP 401 |
| CP-W16 | Unitaria frontend | Formato de cantidad | Utilidad `formatQuantity` | `125.4` y unidad `kg` | El texto incluye `kg` |
| CP-W17 | Contrato frontend | Revisión de alerta | Catálogo demo | `POST /alerts/{id}/review` | Estado de alerta `attended` |
| CP-W18 | Rendimiento | Latencia de salud | TestClient | `GET /health` | Tiempo de respuesta < 500 ms |
| CP-W19 | Estático | Typecheck y lint | Código frontend | `tsc --noEmit` y `eslint` | Sin errores de tipo ni lint bloqueantes |
| CP-W20 | Unitaria backend | Matriz productor/receptor | Roles de dominio | Consulta de permisos | Productor registra lote; receptor registra recepción y pesaje |

---

## 3.3.4 Registro de ejecución

Completar fecha, resultado obtenido y captura al correr la batería.

| Caso | Resultado esperado | Cómo se ejecuta | Evidencia sugerida |
| --- | --- | --- | --- |
| CP-W01 | Dashboard visible | Playwright `auth-and-lots.spec.ts` | Captura del dashboard |
| CP-W02 | No ingresa | Playwright | Captura de `/login` |
| CP-W03 | Error de correo | Vitest `login-schema.test.ts` | Salida del test |
| CP-W04 | Error de contraseña | Vitest | Salida del test |
| CP-W05 | HTTP 200 | Pytest integración | Log de Pytest |
| CP-W06 | Sesión admin | Pytest integración | JSON de respuesta |
| CP-W07 | Drawer de lote | Playwright | Captura del drawer |
| CP-W08 a CP-W12 | Excepciones/estados de dominio | Pytest unitario | Log de Pytest |
| CP-W13 | Vuelve a login | Playwright | Captura de `/login` |
| CP-W14 | 404 register | Pytest integración | Código HTTP |
| CP-W15 | 401 | Pytest integración | Código HTTP |
| CP-W16 | Cantidad con unidad | Vitest | Salida del test |
| CP-W17 | Alerta atendida | Vitest catálogo demo | Salida del test |
| CP-W18 | < 500 ms | Pytest performance | Tiempo medido |
| CP-W19 | Typecheck/lint OK | `npm run typecheck` / `npm run lint` | Captura de consola |
| CP-W20 | Matriz de roles | Pytest `test_permissions.py` | Log de Pytest |

---

## 3.3.5 Cobertura de código

Ejecución real del 26/09/2026 sobre el dominio backend (`pytest --cov=app/domain`):

| Componente | Cobertura | Meta | Cumplimiento |
| --- | --- | --- | --- |
| Backend dominio (`app/domain`) | 98 % (25 pruebas) | ≥ 70 % | Cumple |
| Frontend unitarias (Vitest) | 17 pruebas en validación, formato, UI tone y catálogo demo | ≥ 70 % en utilidades/validaciones | Cumple el plan de calidad de esta iteración |
| Mobile | No aplica a WEB_MINERA | — | Se documenta en APP_MINERA |

Meta inicial del PMV web: **≥ 70 % en dominio backend** (reglas, permisos, servicios de balance) y cobertura de las utilidades/validaciones frontend. No se exige 100 % de páginas Next.js porque son adaptadores de presentación.

Generación:

```bash
cd backend && .venv\Scripts\python -m pytest --cov=app/domain --cov-report=term-missing
cd frontend && npx vitest run --coverage
```

---

## 3.3.6 Análisis estático

| Componente | Herramienta | Alcance |
| --- | --- | --- |
| Frontend | TypeScript strict + ESLint (`eslint-config-next`) | `frontend/src` |
| Backend | Ruff | `backend/app` y `backend/tests` |
| ML | Pytest de estimador (no declara fraude) | `ml/tests` |

SonarQube queda como ampliación posterior, no como evidencia obligatoria de esta iteración.

---

## 3.3.7 Gestión de defectos

Solo se registran defectos encontrados en ejecución real. Plantilla:

| ID | Caso asociado | Defecto | Severidad | Acción | Estado |
| --- | --- | --- | --- | --- | --- |
| DEF-W01 | — | No abrir hasta fallar un caso | N/A | Esperar ejecución | Pendiente |

---

## Relación con CP-01 a CP-05 del informe general

| Caso general | ¿Aplica a WEB? | Equivalente web |
| --- | --- | --- |
| CP-01 Registrar lote | Parcial: la web puede registrar lote, pero el registro de campo es móvil | CP-W08 (regla) + pantalla `/lots` |
| CP-02 GPS | No | Queda en móvil |
| CP-03 Evidencia de cámara | No como captura; la web solo consulta evidencias | Detalle de lote CP-W07 |
| CP-04 Offline | No | Offline-first es de `APP_MINERA` |
| CP-05 Sincronización | No | La web consume datos ya sincronizados |
