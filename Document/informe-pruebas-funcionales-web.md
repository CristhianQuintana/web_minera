# Informe de Pruebas Funcionales — Aplicación Web

**Proyecto:** Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable  
**Componente:** `WEB_MINERA` — Next.js/TypeScript y backend FastAPI/Python  
**Persistencia:** PostgreSQL/Supabase (y catálogo demo local sin Supabase)  
**Incrementos:** Incremento 1 (PMV) e Incremento 2  
**Destinatario:** Desarrollador web/backend y QA  
**Estado:** Plan de ejecución — completar estados, fechas y capturas **después** de ejecutar.  
**Repositorio:** https://github.com/CristhianQuintana/web_minera  
**Evidencias fotográficas (carpeta de entrega):** `evidencias/web/` (crear localmente; no versionar secretos)

---

## 1. Objetivo y límites

Definir y ejecutar pruebas funcionales de la interfaz web y su integración con FastAPI para:

- autenticación y sesión;
- permisos por rol;
- consulta de lotes;
- flujos web de custodia y transporte **implementados**.

### Límites obligatorios

| Regla | Aplicación en WEB_MINERA |
|---|---|
| El frontend no accede a PostgreSQL para negocio | Opera vía API (`/api/v1/...`) o catálogo demo detrás de `PlatformPort`. |
| Validaciones y permisos también en backend | Comprobar UI **y** llamada API / tests de dominio. |
| Capturas reales | Pantallas de la app en ejecución; no mockups. |
| Offline-first | Capacidad **móvil** (`APP_MINERA`). En web: **No aplicable** si no existe cola offline. |
| QR / GPS / evidencia de campo solo móvil | Marcar **No aplicable a la interfaz web** y referenciar ficha móvil (`CP-M-…`). |
| Códigos `RF-I2-*` | Provisionales hasta contrastar con el catálogo oficial. |

### Alcance real implementado (referencia rápida)

| Función | ¿En web? | Dónde |
|---|---|---|
| Login / logout / sesión | Sí | `/login`, API `/api/v1/auth/*` |
| Perfil, rol, organización | Sí | `/api/v1/auth/me`, shell de app |
| Autorización por rol | Sí (backend + UI) | Matriz de permisos + `PermissionGate` |
| Listado y detalle de lotes | Sí | `/lots` |
| Formularios de creación (lote/custodia/transporte) | Parcial | Depende de `canCreate` / formularios en páginas; validación Zod en login |
| Ubicación del lote | Parcial | Campos `latitude`/`longitude` en detalle si vienen de API/demo |
| Evidencias del lote | Parcial (consulta) | Detalle / API evidencias; captura/subida es móvil |
| QR | No (móvil) | No aplicable web |
| Sincronización offline | No (móvil) | No aplicable web |
| Custodia | Sí (consulta; registro según permiso/formulario) | `/custody` |
| Transporte | Sí (consulta; registro según permiso/formulario) | `/transport` |
| Cadena / timeline | Sí | Timeline de lote / auditoría |

---

## 2. Datos sugeridos y datos reales de demo

### 2.1 Datos sugeridos por la actividad (QA)

| Tipo | Valor sugerido | Nota |
|---|---|---|
| Usuarios | `admin.qa`, `auditor.qa`, `productor.qa` | Crear en Supabase Auth + `profiles` si se prueba multi-rol real |
| Lotes | `LOTE-QA-001`, `LOTE-QA-002` | O usar códigos del entorno |
| Vehículo | `VEH-QA-001` | Para transporte |
| Evidencia / QR | Sintéticos | QR: solo móvil |

### 2.2 Datos reales del PMV demo (listos sin Supabase)

| Campo | Valor |
|---|---|
| Correo | `cristhian@gmail.com` |
| Contraseña | `Cristhian123` |
| Rol | `admin` |
| Token demo | `demo-local-cristhian` |
| Lote demo | `LOT-2026-00021` (y `LOT-2026-00022`) |
| URL local Docker | http://localhost |
| URL local Next | http://localhost:3000 |
| Health API | http://localhost/api/health o http://localhost:8000/health |

> **Seguridad:** no incluir contraseñas ni tokens en capturas entregables. En evidencias, ofuscar campos sensibles.

---

## 3. Mapeo de casos (actividad ↔ proyecto)

| RF | Resultado esperado (actividad) | ID interno WEB | ¿Aplicable web? |
|---|---|---|---|
| RF-01 | CP-W-I1-01 | CP-W01 / CP-W02 | Sí |
| RF-02 | CP-W-I1-02 | CP-W06 + `/me` | Sí |
| RF-03 | CP-W-I1-03 | CP-W11 / CP-W15 | Sí |
| RF-04 | CP-W-I1-04 | CP-W07 | Sí |
| RF-05 | CP-W-I1-05 | CP-W03 / CP-W04 / CP-W08 | Sí (login + dominio; registro lote según UI) |
| RF-06 | CP-W-I1-06 | — | Parcial / consultar detalle |
| RF-07 | CP-W-I1-07 | — | Parcial (consulta); captura = móvil |
| RF-08 | CP-W-I1-08 | CP-M-I1-08 | **No aplicable web** |
| RF-09 | CP-W-I1-09 | CP-M (sync) | **No aplicable web** |
| RF-12 | CP-W-I1-10 | CP-W07 + permisos | Sí |
| RF-I2-01 | CP-W-I2-01 | CP-W12 + `/custody` | Sí |
| RF-I2-02 | CP-W-I2-02 | `/transport` | Sí |
| RF-I2-03 | CP-W-I2-03 | CP-M-I2-03 | **No aplicable web** |
| RF-I2-04 | CP-W-I2-04 | Timeline / custody | Sí |

---

## 4. Fichas de prueba funcional (Incremento 1 — PMV)

### Ficha CP-W-I1-01 — Autenticación web (RF-01)

| Campo | Contenido |
|---|---|
| Proyecto | Plataforma para Trazabilidad y Formalización de Pequeña Minería Responsable |
| Componente | WEB_MINERA (Next.js + FastAPI) |
| Incremento | Incremento 1 (PMV) |
| Código RF | RF-01 |
| Nombre | Autenticación web |
| ID caso | CP-W-I1-01 |
| Tipo | Funcional UI/aceptación + API |

**Criterio (Given-When-Then)**  
Dado que el usuario tiene credenciales válidas y cuenta habilitada  
Cuando ingresa credenciales e inicia sesión  
Entonces accede a páginas autorizadas y la sesión se gestiona según el diseño  

**Precondiciones:** Frontend y backend disponibles (Docker o local).  

**Pasos:**
1. Abrir `/login`.
2. Ingresar `cristhian@gmail.com` / `Cristhian123` → Ingresar.
3. Verificar redirección a `/dashboard`.
4. (Negativo) Repetir con contraseña incorrecta → permanece en login.
5. Contrastar API: `POST /api/v1/auth/login`.

**Resultado esperado:** Sesión válida; rechazo controlado con credenciales incorrectas.  
**Resultado obtenido:** \[Completar después de ejecutar\]  

**Evidencias fotográficas**
- Captura 1 (entrada): `evidencias/web/RF-01_paso1_entrada.png` — pantalla login.
- Captura 2 (resultado): `evidencias/web/RF-01_paso2_resultado.png` — dashboard o mensaje de error.

**Evaluación:** Pendiente de ejecución / Aprobado / Fallido / Bloqueado  
**Fecha:** \[DD/MM/AAAA\] · **Evaluador:** \[Nombre\]  
**Observaciones:** \[Completar\]

---

### Ficha CP-W-I1-02 — Recuperar perfil, rol y organización (RF-02)

| Campo | Contenido |
|---|---|
| Código RF | RF-02 |
| ID caso | CP-W-I1-02 |
| Tipo | Funcional UI + API |

**Criterio**  
Dado que el usuario inició sesión  
Cuando la web carga su perfil/contexto  
Entonces el perfil y organización corresponden a la identidad y al backend  

**Pasos:**
1. Iniciar sesión (CP-W-I1-01).
2. Observar nombre/rol en el shell (cabecera / menú).
3. Contrastar `GET /api/v1/auth/me` con Bearer demo o cookie.
4. (Negativo, si hay usuario QA) cuenta inactiva → mensaje de cuenta inactiva.

**Resultado esperado:** Perfil, rol `admin` (demo) y organización coherentes con API.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:**  
`evidencias/web/RF-02_paso1_entrada.png` · `evidencias/web/RF-02_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-03 — Autorización por rol (RF-03)

| Campo | Contenido |
|---|---|
| Código RF | RF-03 |
| ID caso | CP-W-I1-03 |
| Tipo | Autorización UI + API + unitaria backend |

**Criterio**  
Dado que hay usuarios con permisos diferentes  
Cuando cada uno intenta operaciones permitidas y restringidas  
Entonces el backend autoriza solo las permitidas (también por API directa)  

**Pasos:**
1. Con usuario admin demo: verificar menús de usuarios/configuración visibles.
2. Con rol `auditor`/`productor` (QA Supabase) o prueba unitaria de matriz de permisos: intentar operación no permitida.
3. API sin token: `GET /api/v1/auth/me` → 401.
4. API con token pero sin permiso: endpoint restringido → 403.

**Resultado esperado:** Rechazo 401/403; UI no expone acciones sin permiso.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-03_paso1_entrada.png` · `evidencias/web/RF-03_paso2_resultado.png`  
**Complemento técnico:** salida de `pytest tests/unit/test_permissions.py`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-04 — Consultar datos del lote (RF-04)

| Campo | Contenido |
|---|---|
| Código RF | RF-04 |
| ID caso | CP-W-I1-04 |
| Tipo | Funcional UI + contraste API |

**Criterio**  
Dado que existe un lote registrado  
Cuando un usuario autorizado abre listado y detalle  
Entonces la web presenta datos consistentes con la API  

**Pasos:**
1. Login → `/lots`.
2. Verificar fila `LOT-2026-00021` (demo) u otro lote QA.
3. Abrir **Detalle**.
4. Contrastar con `GET /api/v1/lots` y `GET /api/v1/lots/{id}`.

**Resultado esperado:** Código, mineral, cantidad, estado alineados API↔UI.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-04_paso1_entrada.png` · `evidencias/web/RF-04_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-05 — Validar formulario web (RF-05)

| Campo | Contenido |
|---|---|
| Código RF | RF-05 |
| ID caso | CP-W-I1-05 |
| Tipo | Validación UI + dominio backend |

**Criterio**  
Dado que la web ofrece formulario  
Cuando se envían campos vacíos o inválidos  
Entonces la UI informa errores y el backend no persiste datos inválidos  

**Pasos:**
1. En `/login`: correo inválido / contraseña corta → mensajes Zod.
2. Si existe formulario de alta de lote en web con permiso: enviar vacío → error UI; verificar que no hay POST exitoso.
3. Complemento: regla de dominio backend (código vacío / cantidad ≤ 0) vía `pytest` (`CP-W08`).

**Resultado esperado:** Errores visibles; sin persistencia inválida.  
**Resultado obtenido:** \[Completar\]  
**Si no hay alta de lote en web:** documentar que el registro de lote en campo es móvil y que la validación de negocio se prueba en backend (no inventar flujo web).

**Evidencias:** `evidencias/web/RF-05_paso1_entrada.png` · `evidencias/web/RF-05_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-06 — Visualizar ubicación del lote (RF-06)

| Campo | Contenido |
|---|---|
| Código RF | RF-06 |
| ID caso | CP-W-I1-06 |
| Tipo | Funcional UI |

**Criterio**  
Dado un lote con ubicación válida (o sin ella)  
Cuando el usuario abre el detalle  
Entonces se muestra ubicación disponible o estado vacío controlado  

**Pasos:**
1. Abrir detalle de `LOT-2026-00021` (demo incluye lat/lng).
2. Abrir lote sin coordenadas (`LOT-2026-00022` o QA).
3. Verificar que no hay crash; mensaje vacío controlado si aplica.

**Resultado esperado:** Coordenadas visibles o vacío controlado (mapa embebido no es obligatorio en PMV).  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-06_paso1_entrada.png` · `evidencias/web/RF-06_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-07 — Consultar evidencia del lote (RF-07)

| Campo | Contenido |
|---|---|
| Código RF | RF-07 |
| ID caso | CP-W-I1-07 |
| Tipo | Funcional UI + API autorizada |

**Criterio**  
Dado que existe evidencia y el usuario tiene permiso  
Cuando abre la sección de evidencias  
Entonces se muestra/descarga mediante mecanismo autorizado  

**Pasos:**
1. Detalle de lote con evidencia (demo `ev-1`).
2. Si hay URL firmada: `GET` evidencia vía API autorizada.
3. (Negativo) usuario sin permiso → 403 / UI oculta.

**Resultado esperado:** Evidencia correcta por canal autorizado; captura en campo = móvil.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-07_paso1_entrada.png` · `evidencias/web/RF-07_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I1-08 — Visualizar/resolver QR (RF-08)

| Campo | Contenido |
|---|---|
| Código RF | RF-08 |
| ID caso | CP-W-I1-08 |
| Tipo | — |

**Criterio**  
Dado QR y función web implementada…  

**Estado de aplicabilidad:** **No aplicable a la interfaz web.**  
La lectura/resolución de QR pertenece a `APP_MINERA`. Referenciar ficha móvil **CP-M-I1-08**.

**Resultado esperado:** N/A  
**Resultado obtenido:** No aplicable — función exclusiva móvil.  
**Evidencias:** No se simulan capturas web. Opcional: captura de menú web sin opción QR para justificar N/A → `evidencias/web/RF-08_no_aplicable.png`

**Evaluación:** No aplicable  
**Observaciones:** Offline/QR/GPS no se atribuyen a WEB_MINERA.

---

### Ficha CP-W-I1-09 — Estado de sincronización (RF-09)

| Campo | Contenido |
|---|---|
| Código RF | RF-09 |
| ID caso | CP-W-I1-09 |

**Estado de aplicabilidad:** **No aplicable a la interfaz web.**  
La cola offline-first y su sincronización son de `APP_MINERA`. No afirmar que la web implementa esa cola.

**Resultado obtenido:** No aplicable — referenciar prueba móvil de sync.  
**Evidencia opcional:** `evidencias/web/RF-09_no_aplicable.png`

**Evaluación:** No aplicable

---

### Ficha CP-W-I1-10 — Consultar lotes autorizados (RF-12)

| Campo | Contenido |
|---|---|
| Código RF | RF-12 |
| ID caso | CP-W-I1-10 |
| Tipo | Funcional + autorización / aislamiento org |

**Criterio**  
Dado sesión y permiso  
Cuando abre listado, busca y consulta detalle  
Entonces solo accede a lotes autorizados y coinciden con API  

**Pasos:**
1. Login → `/lots` → buscar código.
2. Detalle autorizado OK.
3. (QA multi-org) intentar lote de otra organización → 403/404 o vacío; no filtrar solo en UI.

**Resultado esperado:** Alcance por autorización backend.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-12_paso1_entrada.png` · `evidencias/web/RF-12_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

## 5. Fichas de prueba funcional (Incremento 2 — Custodia y transporte)

### Ficha CP-W-I2-01 — Registrar o consultar transferencia de custodia (RF-I2-01)

| Campo | Contenido |
|---|---|
| Código RF | RF-I2-01 (provisional) |
| ID caso | CP-W-I2-01 |
| Tipo | Funcional UI + API |

**Criterio**  
Dado lote y autorización  
Cuando registra transferencia (si el flujo web existe) o consulta una existente  
Entonces se presentan origen, destino, responsable, fecha/hora, estado y evidencia vinculada  

**Pasos:**
1. Login → `/custody`.
2. Listar transferencias; abrir detalle.
3. Si hay formulario de alta y permiso `transfer_custody`: registrar con datos válidos; contrastar `POST /api/v1/custody`.
4. Negativo: usuario sin permiso o campos incompletos.

**Resultado esperado:** Consulta/registro coherente con API; vínculo al lote.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-I2-01_paso1_entrada.png` · `evidencias/web/RF-I2-01_paso2_resultado.png`  
**Complemento:** `pytest` custodia inválida (`CP-W12`).

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I2-02 — Registrar o consultar evento de transporte (RF-I2-02)

| Campo | Contenido |
|---|---|
| Código RF | RF-I2-02 (provisional) |
| ID caso | CP-W-I2-02 |

**Criterio**  
Dado lote/transferencia válida  
Cuando registra evento (si existe) o abre uno existente  
Entonces se muestran vehículo/transportista, origen, destino; nuevos registros vinculados al lote  

**Pasos:**
1. `/transport` → listado y detalle.
2. Si hay alta web: registrar con `VEH-QA-001` o placa demo; contrastar API.
3. Negativo: datos incompletos / lote inexistente.

**Resultado esperado:** Evento visible y persistido vía API.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-I2-02_paso1_entrada.png` · `evidencias/web/RF-I2-02_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

### Ficha CP-W-I2-03 — Resolver QR en web (RF-I2-03)

| Campo | Contenido |
|---|---|
| Código RF | RF-I2-03 (provisional) |
| ID caso | CP-W-I2-03 |

**Estado de aplicabilidad:** **No aplicable a la interfaz web.**  
Referenciar **CP-M-I2-03** (móvil).

**Evaluación:** No aplicable  
**Evidencia opcional:** `evidencias/web/RF-I2-03_no_aplicable.png`

---

### Ficha CP-W-I2-04 — Consultar cadena de custodia (RF-I2-04)

| Campo | Contenido |
|---|---|
| Código RF | RF-I2-04 (provisional) |
| ID caso | CP-W-I2-04 |

**Criterio**  
Dado lote con transferencias y eventos  
Cuando el usuario autorizado consulta el historial  
Entonces la web muestra secuencia con responsables, fechas/horas, estados y evidencia/ubicación disponibles  

**Pasos:**
1. Detalle de lote → timeline / custodia asociada.
2. O módulo auditoría `/audit` / caso de auditoría.
3. Contrastar API timeline del lote.
4. Negativo: lote sin historial (vacío controlado); usuario sin permiso.

**Resultado esperado:** Cadena cronológica coherente con API.  
**Resultado obtenido:** \[Completar\]  

**Evidencias:** `evidencias/web/RF-I2-04_paso1_entrada.png` · `evidencias/web/RF-I2-04_paso2_resultado.png`

**Evaluación:** Pendiente · **Fecha:** · **Evaluador:** · **Observaciones:**

---

## 6. Evidencia técnica complementaria del backend

Adjuntar en `evidencias/web/api/` (sin secretos):

| Evidencia | Cómo obtenerla |
|---|---|
| Health | `GET /health` → 200 `{"status":"ok"}` |
| Login demo | `POST /api/v1/auth/login` |
| Perfil | `GET /api/v1/auth/me` |
| Lotes | `GET /api/v1/lots` |
| Custodia / transporte | `GET /api/v1/custody`, `GET /api/v1/transport` |
| Sin permiso / sin token | 401/403 |
| Sin registro público | `POST /api/v1/auth/register` → 404 |
| Pytest | Volcado de terminal `30 passed` (o ejecución actual) |

Esta evidencia **complementa** las capturas de UI; no las sustituye.

---

## 7. Resumen de ejecución

| Métrica | Resultado |
|---|---|
| Casos principales planificados | 14 |
| Ejecutados | \[Completar\] |
| Aprobados | \[Completar\] |
| Fallidos | \[Completar\] |
| No aplicables a web | 3 (RF-08, RF-09, RF-I2-03) — confirmar tras revisión |
| Bloqueados / no implementados | \[Completar\] |
| Defectos abiertos / críticos | \[Completar\] |

**Tasa de aprobación sugerida** = aprobados / ejecutados × 100.  
Reportar por separado: no aplicables y no ejecutados.

---

## 8. Criterio de cierre

- [ ] Cada RF aplicable tiene ficha + captura real en `evidencias/web/`.
- [ ] Casos N/A justificados (móvil).
- [ ] Persistencia/relaciones contrastadas con API.
- [ ] Defectos con pasos, esperado vs obtenido.
- [ ] Sin contraseñas/tokens visibles en capturas.
- [ ] Entregar este informe + `evidencias/web/` + hallazgos técnicos.

---

## 9. Comandos para ejecutar (y capturar evidencias)

> Ejecutar desde la raíz del repo:  
> `c:\Users\USER\OneDrive\Documentos\Proyectos\web_minera`  
> En PowerShell. Crear carpeta de evidencias:  
> `mkdir evidencias\web -Force`

### 9.1 Levantar el sistema (recomendado: Docker)

```powershell
# Docker Desktop debe estar abierto
copy .env.example .env
# Completar SUPABASE_* si usará datos reales; el login demo funciona sin Supabase

docker compose up -d --build
docker compose ps

# Health
curl http://localhost/api/health
# o
Invoke-RestMethod http://localhost/api/health
```

Abrir navegador: **http://localhost** → login → capturar pantallas de cada ficha.

### 9.2 Alternativa sin Docker (frontend + backend locales)

```powershell
# Terminal 1 — Backend
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
copy .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Abrir **http://localhost:3000**.

### 9.3 Contraste API (PowerShell) — para evidencia técnica

```powershell
# Health
Invoke-RestMethod http://localhost:8000/health

# Login demo
$login = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"cristhian@gmail.com","password":"Cristhian123"}'
$login | ConvertTo-Json -Depth 6

# Perfil
Invoke-RestMethod http://localhost:8000/api/v1/auth/me `
  -Headers @{ Authorization = "Bearer $($login.access_token)" }

# Lotes
Invoke-RestMethod "http://localhost:8000/api/v1/lots?page=1&page_size=20" `
  -Headers @{ Authorization = "Bearer $($login.access_token)" }

# Login incorrecto (debe fallar)
try {
  Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/auth/login `
    -ContentType "application/json" `
    -Body '{"email":"cristhian@gmail.com","password":"clave-incorrecta"}'
} catch { $_.Exception.Response.StatusCode.value__ }

# Sin token → 401
try {
  Invoke-RestMethod http://localhost:8000/api/v1/auth/me
} catch { $_.Exception.Response.StatusCode.value__ }

# No hay registro público → 404
try {
  Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/auth/register `
    -ContentType "application/json" -Body '{"email":"x@y.com"}'
} catch { $_.Exception.Response.StatusCode.value__ }
```

Guardar salidas (sin secretos) en `evidencias/web/api/`.

### 9.4 Pruebas automatizadas (captura de terminal)

```powershell
# Backend (unit + integration + performance)
cd backend
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/performance -q
# Captura: evidencias/web/pytest_backend.png (o .txt)

# Solo aislamiento hexagonal
.\.venv\Scripts\python.exe -m pytest tests/unit/test_architecture_isolation.py -q

# Frontend unitarias (Vitest)
cd frontend
npx vitest run
# Captura: evidencias/web/vitest.png

# E2E Playwright (login, lotes, logout) — ideal para video/capturas
cd frontend
npx playwright install chromium
npx playwright test --headed
# o un caso:
npx playwright test tests/e2e/auth-and-lots.spec.ts --headed
```

### 9.5 Rutas UI a recorrer para capturas manuales

| Ficha | Ruta / acción |
|---|---|
| RF-01 | `/login` → dashboard; login fallido |
| RF-02 | Shell con nombre/rol; opcional `/profile` |
| RF-03 | Menús admin vs rol restringido; API 401 |
| RF-04 / RF-12 | `/lots` → Detalle |
| RF-05 | Login con datos inválidos |
| RF-06 / RF-07 | Detalle de lote (ubicación / evidencias) |
| RF-08 / RF-09 / RF-I2-03 | Justificar N/A (sin pantalla de QR/sync) |
| RF-I2-01 | `/custody` |
| RF-I2-02 | `/transport` |
| RF-I2-04 | Detalle lote / timeline / `/audit` |

### 9.6 Apagar Docker (opcional)

```powershell
docker compose down
```

---

## 10. Relación con otros documentos

| Documento | Uso |
|---|---|
| `docs/testing/estrategia-pruebas-web.md` | Estrategia y matriz CP-Wxx automatizados |
| `docs/architecture/hexagonal-architecture-audit.md` | Arquitectura (no sustituye este informe funcional) |
| `Document/actividad-4-evaluacion-arquitectura-hexagonal.md` | Actividad 4 hexagonal |
| Este archivo | **Informe de pruebas funcionales web Inc. 1 y 2** |

---

*Plantilla lista para ejecución QA. Completar “Resultado obtenido”, evaluación, fecha y rutas reales de capturas tras la corrida.*
