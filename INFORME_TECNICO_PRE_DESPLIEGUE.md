# INFORME TÉCNICO PRE-DESPLIEGUE — WEB_MINERA

**Objetivo:** diagnóstico técnico para preparar despliegue en **Render Free**, sin ejecutar el despliegue ni modificar código.  
**Fecha de revisión:** 2026-10-30  
**Alcance:** estado actual del repositorio único en GitHub (`frontend` + `backend` + `ml`).  
**Condiciones respetadas:** sin secretos, sin inventar comandos, pendientes marcados explícitamente.

---

## 1. Estructura del repositorio

### 1.1 URL y rama

| Dato | Valor real |
|---|---|
| URL GitHub | `https://github.com/CristhianQuintana/web_minera.git` |
| Rama principal | `main` (tracking `origin/main`) |
| HEAD revisado | `4d9b0dd` — *Documentar el commit de evidencia en la auditoría hexagonal.* |

> **Nota:** el working tree local puede tener cambios no pusheados respecto a `origin/main`. El despliegue en Render debe basarse en lo que esté en GitHub tras el push correspondiente.

### 1.2 Estructura de carpetas principales

```text
web_minera/
├── .github/workflows/          # CI (backend, frontend, ml, integration)
├── backend/                    # API FastAPI (hexagonal)
│   ├── app/                    # código de aplicación
│   ├── requirements/           # base.txt, dev.txt
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml          # requires-python >=3.11
├── frontend/                   # Next.js
│   ├── src/
│   ├── public/
│   ├── package.json / package-lock.json
│   ├── next.config.ts
│   └── Dockerfile
├── ml/                         # servicio ML (FastAPI independiente)
│   ├── adapters/inbound/http/
│   ├── domain/services/
│   ├── requirements.txt
│   └── Dockerfile
├── database/                   # SQL / migraciones / bootstrap Supabase
├── docker/nginx/               # Nginx (compose local; no es servicio Render)
├── compose.yaml                # Docker Compose (frontend + backend + nginx; SIN ml)
├── contracts/
├── docs/ / Document/
├── infrastructure/
├── tests/
├── .env.example
└── README.md
```

### 1.3 Ubicación exacta de componentes

| Componente | Carpeta |
|---|---|
| Frontend | `frontend/` |
| Backend | `backend/` |
| ML | `ml/` |

### 1.4 Docker / Compose / despliegue

| Artefacto | Existe | Notas |
|---|---|---|
| `backend/Dockerfile` | Sí | Python 3.11-slim, puerto 8000 |
| `frontend/Dockerfile` | Sí | multi-stage Node 22, puerto 3000 |
| `ml/Dockerfile` | Sí | Python 3.11-slim, puerto 8001 |
| `compose.yaml` | Sí | `frontend` + `backend` + `nginx`; **ML no está en compose** |
| `docker-compose.yml` | No | eliminado / sustituido por `compose.yaml` |
| `docker/nginx/nginx.conf` | Sí | proxy `/` → frontend, `/api/` → backend |
| `render.yaml` / `Procfile` | **No** | pendiente para Render |

### 1.5 CI/CD (GitHub Actions)

| Workflow | Ruta | Qué hace |
|---|---|---|
| Backend CI | `.github/workflows/backend-ci.yml` | Python 3.11, Ruff, Pytest en `backend/` |
| Frontend CI | `.github/workflows/frontend-ci.yml` | Node, lint/test (según archivo) |
| ML CI | `.github/workflows/ml-ci.yml` | tests ML |
| Integration CI | `.github/workflows/integration-ci.yml` | unit backend + pytest ML |

No hay workflow de deploy a Render en el repositorio.

---

## 2. Información del frontend

### 2.1 Stack

| Ítem | Valor |
|---|---|
| Framework | **Next.js 15.5.4** (App Router) |
| React | 19.1.0 |
| TypeScript | ^5 |
| Node.js requerida | **No hay campo `engines` en `package.json`**. El Dockerfile usa **`node:22-alpine`** → referencia operativa: **Node 22** |
| Gestor de paquetes | **npm** (`package-lock.json`; sin pnpm/yarn) |
| Archivo de dependencias | `frontend/package.json` + `frontend/package-lock.json` |

### 2.2 Comandos reales

```bash
# Instalar (Dockerfile usa --legacy-peer-deps)
cd frontend
npm install --legacy-peer-deps

# Compilar
npm run build
# (equivale a: next build --turbopack)

# Iniciar producción
npm run start
# (equivale a: next start)
# En Docker: npm run start -- -H 0.0.0.0 -p 3000

# Desarrollo
npm run dev
```

### 2.3 Configuración Next.js

- Archivo: `frontend/next.config.ts` (configuración mínima / vacía de opciones extra).
- Scripts relevantes: `dev`, `build`, `start`, `lint`, `test`, `test:e2e`, `typecheck`.

### 2.4 Variables de entorno (frontend)

| Variable | Finalidad | Cuándo se aplica |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL del backend. Vacío = `fetch` relativo (`/api/v1/...`). Si no está definida en runtime de build, el código cae a `http://localhost:8000` | **Build-time** (Next embebe `NEXT_PUBLIC_*`) |
| `NEXT_PUBLIC_SUPABASE_URL` | URL del proyecto Supabase (cliente; hay fallback hardcodeado antiguo en `env.ts` si falta) | Build-time |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anon/publishable key (pública) | Build-time |

Definidas también como `ARG`/`ENV` en `frontend/Dockerfile`.

### 2.5 Cómo se configura la URL del backend

1. Código: `frontend/src/config/env.ts` → `env.apiUrl`.
2. Cliente HTTP: `frontend/src/adapters/outbound/api/http-client.ts` hace `fetch(\`${env.apiUrl}${path}\`)` con paths tipo `/api/v1/...`.
3. Local: suele usarse `NEXT_PUBLIC_API_URL=http://localhost:8000` en `.env.local`.
4. Docker+Nginx: `NEXT_PUBLIC_API_URL` vacío → mismo origen, Nginx reescribe `/api/` al backend.

### 2.6 Dependencias de localhost

| Ubicación | Dependencia |
|---|---|
| `frontend/src/config/env.ts` | Fallback `http://localhost:8000` si `NEXT_PUBLIC_API_URL` no está definida |
| Fallbacks de Supabase en `env.ts` | URL/anon key antiguas por defecto si faltan env (riesgo en prod si no se setean) |
| Modo demo | Login demo interceptado en cliente (`demo-catalog.ts`) sin necesidad de API |

---

## 3. Información del backend

### 3.1 Stack y entrada

| Ítem | Valor |
|---|---|
| Python | **≥ 3.11** (`pyproject.toml`); Docker **3.11-slim** |
| FastAPI | **0.115.12** (`requirements/base.txt`) |
| Uvicorn | 0.34.2 |
| Archivo principal | `backend/app/main.py` |
| Objeto ASGI | **`app`** (`app = create_app()`) |
| Factory | `backend/app/composition/application_factory/factory.py` → `create_app()` |

### 3.2 Dependencias y comandos

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements/base.txt          # producción
# o
pip install -r requirements/dev.txt           # incluye tests/lint

# Iniciar
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Local reload: uvicorn app.main:app --reload --port 8000
```

Dockerfile CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`  
**Puerto actual:** **8000**

### 3.3 Variables de entorno (backend)

Nombres según `Settings` (`pydantic-settings`) y `.env.example` / `compose.yaml`:

| Variable | Finalidad |
|---|---|
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_ANON_KEY` | Clave anon/publishable para Auth/REST |
| `SUPABASE_SERVICE_ROLE_KEY` | Rol servicio (admin/bypass RLS; invitaciones); opcional |
| `JWT_SECRET` | Reservado en settings; uso actual limitado |
| `ML_SERVICE_URL` | Base URL del servicio ML (default código: `http://localhost:8001`) |
| `FRONTEND_ORIGIN` | Origen CORS principal (URL del frontend en prod) |
| `APP_ENV` | `development` / `production` |
| `INVITE_EXPIRY_HOURS` | Caducidad de invitaciones (default 72) |
| `INVITE_BASE_URL` | URL base de activación de cuenta |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM` | Correo de invitaciones (opcional) |

### 3.4 CORS actual

En `create_app()` se permiten orígenes:

- `FRONTEND_ORIGIN` (settings)
- `http://localhost`, `http://localhost:3000`
- `http://127.0.0.1`, `http://127.0.0.1:3000`

`allow_credentials=True`, métodos y headers `*`.

**Para Render:** hay que poner `FRONTEND_ORIGIN` a la URL pública del frontend (p. ej. `https://….onrender.com`). Los localhost pueden permanecer, pero no bastan solos.

### 3.5 Health

| Endpoint | Respuesta |
|---|---|
| `GET /health` | `{"status":"ok"}` |

También OpenAPI: `/docs`, `/openapi.json` (activos por defecto FastAPI).

### 3.6 Conexión Supabase

- Adaptador: `backend/app/adapters/outbound/supabase/client.py` (`SupabaseGateway`).
- Usa HTTP (`httpx`) contra:
  - Auth: `{SUPABASE_URL}/auth/v1/...`
  - REST: `{SUPABASE_URL}/rest/v1/...`
  - Storage signed URLs: `{SUPABASE_URL}/storage/v1/...`
- Composition: `backend/app/composition/container.py` inyecta el gateway.

### 3.7 Dependencias de localhost

| Elemento | Detalle |
|---|---|
| Default `ML_SERVICE_URL` | `http://localhost:8001` |
| Default `FRONTEND_ORIGIN` | `http://localhost:3000` |
| Default `INVITE_BASE_URL` | `http://localhost:3000/activate-account` |
| CORS | incluye localhost/127.0.0.1 |
| Defaults de `Settings` | URL/anon Supabase antiguas en código si faltan env |
| Demo auth | bypass en `platform.py` (email demo) — **debe desactivarse en producción** |

---

## 4. Información del servicio ML

### 4.1 Ubicación y stack

| Ítem | Valor |
|---|---|
| Carpeta | `ml/` |
| Framework | FastAPI **0.115.12** + Uvicorn (mismas pins que backend API) |
| Python | 3.11 (Dockerfile) |
| Archivo de app canónico | `ml/adapters/inbound/http/main.py` → objeto **`app`** |
| Compat | `ml/presentation/api/main.py` reexporta `app` |
| Dependencias | `ml/requirements.txt` (fastapi, uvicorn, pydantic, pytest) |
| Env ejemplo | `ml/.env.example` (`MLFLOW_TRACKING_URI`, `MODEL_REGISTRY_URI`, `MODEL_VERSION`) — **no usadas** por el estimador actual |

### 4.2 Ejecución

```bash
cd ml
pip install -r requirements.txt
set PYTHONPATH=.          # Windows
# export PYTHONPATH=.     # Linux
uvicorn adapters.inbound.http.main:app --host 0.0.0.0 --port 8001
```

Dockerfile CMD: `uvicorn adapters.inbound.http.main:app --host 0.0.0.0 --port 8001`  
**Puerto:** **8001**  
Health: `GET /health`  
Inferencia: `POST /inference/estimate`

### 4.3 Modelos

| Pregunta | Respuesta real |
|---|---|
| Modelos ML pesados (.pkl/.pt/…) | **No existen** en el repo |
| Implementación | Regla heurística en `ml/domain/services/estimator.py` (`ExpectedQuantityEstimator`, versión `1.0.0`) |
| Tamaño | Código &lt; 1 KB del estimador; sin artefactos de pesos |
| CPU / RAM | Muy bajo (API ligera); estimado **&lt; 512 MB** suficiente en Free |
| ¿Necesita servicio independiente? | **Arquitecturalmente sí es API HTTP aparte**; **operativamente opcional**: el backend tiene **fallback local** en `MLServiceAdapter` si ML no responde |

### 4.4 Comunicación con el backend

- Backend → ML: HTTP POST `{ML_SERVICE_URL}/inference/estimate` (`backend/app/adapters/outbound/ml/client.py`).
- Si falla la red/ML: retorna estimación `1.0.0-fallback` sin tumbar la API.
- **No** es un módulo importado por el backend; es **servicio independiente**.
- `compose.yaml` **no** levanta ML hoy; en local se asume proceso aparte o solo fallback.

**Recomendación Render Free:** desplegar **frontend + backend** primero; ML como tercer Web Service solo si se requiere; o dejar `ML_SERVICE_URL` vacío/inválido y usar fallback (comportamiento actual ante error).

---

## 5. Supabase y base de datos

### 5.1 Servicios usados

| Servicio Supabase | Uso en WEB_MINERA |
|---|---|
| Auth | Login, refresh, recover, create/invite user |
| PostgreSQL (PostgREST) | Tablas de negocio vía REST |
| Storage | URLs firmadas bucket `evidencias` |
| RLS | Políticas en migraciones SQL |

### 5.2 PostgreSQL / migraciones

| Ítem | Estado |
|---|---|
| Ubicación migraciones | `database/migrations/` (`0001`, `0004`, `0005`, `0006`) |
| Compile web | `database/supabase_compile.sql` |
| Bootstrap proyecto vacío | `database/bootstrap_full.sql` + `database/APLICAR_EN_SUPABASE.md` |
| Seeds | `database/seeds/promote_admin.sql` |
| Estado en cloud | **Pendiente de verificación continua**: en revisiones previas el proyecto configurado localmente **no tenía tablas** hasta ejecutar el bootstrap manualmente. Debe confirmarse en el SQL Editor / Table Editor antes del go-live. |

### 5.3 RLS

Definidas en SQL (enable RLS + `create policy` sobre `organizations`, `profiles`, `lots`, custodia, transportes, evidencias, `audit_log`, tablas web, storage).  
Estado en instancia remota: **pendiente** hasta aplicar scripts.

### 5.4 Auth

- Sin registro público en la API (`POST /api/v1/auth/register` → 404).
- Flujo: login → sesión; invitaciones/activación vía backend + Supabase Auth.
- Demo local bypass (no producción).

### 5.5 Storage

- Bucket referenciado: `evidencias`.
- Operación: `signed_url` desde gateway.

### 5.6 Variables (solo nombres)

`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`,  
`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

### 5.7 Cambios para producción

1. Ejecutar `bootstrap_full.sql` (o migraciones en orden) en el proyecto Supabase de prod.  
2. Crear usuario Auth + profile admin.  
3. Configurar env de Render **sin** defaults de desarrollo.  
4. Desactivar demo login.  
5. Revisar bucket Storage y políticas.  
6. No versionar `.env` reales (ya en `.gitignore`).

---

## 6. Dependencias y compatibilidad para producción

| Pregunta | Respuesta |
|---|---|
| ¿Tres componentes independientes? | **Sí** (procesos/HTTP separados). Compose hoy solo FE+BE+nginx. |
| ¿Dependencias compartidas FE/BE/ML? | No de runtime. BE y ML comparten pins FastAPI/uvicorn en requirements distintos. |
| ¿Rutas absolutas / localhost? | Sí: defaults en `settings.py`, `env.ts`, CORS, `ML_SERVICE_URL`. |
| ¿Archivos pesados? | No se hallaron pesos ML ni binarios &gt; 5 MB fuera de `node_modules`/`.venv`/`.next` (artefactos locales no van al deploy si el build usa el repo limpio). |
| ¿Procesos permanentes? | Sí: 2–3 Web Services (FE, BE, opcional ML). |
| ¿Colas / cron / background? | **No** hay Celery/RQ/APScheduler en el código revisado. |
| ¿Restricciones memoria? | ML ligero. Next build puede ser pesado en Free (build minutes / RAM). Backend slim. |
| ¿Linux? | Dockerfiles Alpine/slim → pensados para Linux. Compatible con Render. |

**Límite Render Free relevante:** servicios duermen por inactividad; cold start; 3 servicios Free típicos → priorizar FE+BE; ML opcional.

---

## 7. Configuración necesaria para producción (sin implementar aún)

| Área | Modificación necesaria |
|---|---|
| URLs | Setear `NEXT_PUBLIC_API_URL` a URL pública del backend **en el build** del frontend, **o** usar proxy/mismo dominio. En Render Free separado: URL absoluta `https://<backend>.onrender.com`. |
| CORS | `FRONTEND_ORIGIN=https://<frontend>.onrender.com` |
| FE ↔ BE | Paths `/api/v1/...` + base URL correcta; cookies/`credentials` si se usan |
| BE ↔ ML | `ML_SERVICE_URL=https://<ml>.onrender.com` o omitir y aceptar fallback |
| Env | Todas las de las tablas §§2–5; `APP_ENV=production` |
| Demo | Condicionar/eliminar bypass `DEMO_*` en producción |
| Health | Usar `GET /health` (backend y ML) como health check Render |
| Secretos | Solo env de Render; nunca en git; regenerar si se filtraron |
| Disco efímero | No depender de filesystem local; evidencias en Supabase Storage |

---

## 8. Estado de pruebas (real / documentado)

| Prueba | Estado | Resultado / notas |
|---|---|---|
| Compilación frontend | **Ejecutada** (histórico local) | `npm run build` completó (Next 15.5.4); en esta sesión no se re-ejecutó |
| Ejecución backend | **Ejecutada** | `uvicorn` + `GET /health` → `ok` (sesión local 2026-10-30) |
| Ejecución ML | **Parcial** | Tests unitarios del estimador existen; servicio HTTP no verificado en esta sesión |
| Conexión Supabase | **Ejecutada (fallida en tablas)** | Auth/REST alcanzables; tablas ausentes hasta aplicar SQL (revisión previa) |
| Comunicación FE↔BE | **Ejecutada** | Login demo UI → dashboard; API login demo OK |
| Comunicación BE↔ML | **No ejecutada end-to-end en esta sesión** | Código con fallback si ML cae |
| AuthZ | **Ejecutada (automatizada)** | Tests unitarios permisos / isolation; demo auth OK |
| Registro/consulta datos | **Parcial** | Demo catalog UI OK; persistencia real pendiente de tablas Supabase |
| Carga/recuperación archivos | **No ejecutada** de forma verificada en esta revisión | Código de signed URL existe |

Errores conocidos documentados:

- Supabase sin esquema → 404 PostgREST en tablas.  
- Login Auth real sin usuario → `invalid_credentials`.  
- Backend demo: `/me` OK; algunos listados vía API real pueden 500 si no hay tablas (el frontend demo evita esto con catálogo local).

---

## 9. Problemas identificados (pre-Render)

1. **Sin `render.yaml` / Blueprint** — hay que definir 2–3 Web Services a mano.  
2. **`NEXT_PUBLIC_*` en build** — hay que pasar env en build de Render (o rebuild al cambiar API URL).  
3. **Fallbacks localhost / Supabase antiguos en código** — riesgo si faltan env.  
4. **Demo credentials en código** — inadecuado en prod.  
5. **CORS** anclado a localhost + un solo `FRONTEND_ORIGIN`.  
6. **ML no está en `compose.yaml`** — coherente con opcionalidad, pero debe decidirse en Render.  
7. **SQL no auto-aplicado** — requiere paso manual en Supabase.  
8. **Cold start Free** — primer request lento; health checks deben tolerarlo.  
9. **CVEs de dependencias** (auditorías previas npm/pip) — plan de bump antes o justo después del deploy.  
10. **OpenAPI `/docs` abierto** por defecto — conviene cerrarlo en prod.

---

## 10. Mapa sugerido de servicios Render Free (orientativo)

| Servicio Render | Root Directory | Build | Start | Health |
|---|---|---|---|---|
| `web-minera-frontend` | `frontend` | `npm install --legacy-peer-deps && npm run build` | `npm run start -- -H 0.0.0.0 -p $PORT` | HTTP `/login` o `/` |
| `web-minera-backend` | `backend` | `pip install -r requirements/base.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | `GET /health` |
| `web-minera-ml` (opcional) | `ml` | `pip install -r requirements.txt` | `PYTHONPATH=. uvicorn adapters.inbound.http.main:app --host 0.0.0.0 --port $PORT` | `GET /health` |

> Render inyecta `PORT`; no fijar 8000/3000/8001 en start de producción.

---

## 11. Archivos de configuración de verificación (adjuntos por referencia)

| Archivo | Para verificar |
|---|---|
| `compose.yaml` | Orquestación local FE+BE+nginx |
| `backend/Dockerfile` | Imagen y CMD backend |
| `frontend/Dockerfile` | Node 22, build args `NEXT_PUBLIC_*` |
| `ml/Dockerfile` | CMD ML puerto 8001 |
| `backend/requirements/base.txt` | Pins Python |
| `frontend/package.json` | Scripts y Next 15.5.4 |
| `backend/app/main.py` | Objeto `app` |
| `backend/app/infrastructure/configuration/settings.py` | Env backend |
| `frontend/src/config/env.ts` | Env frontend / fallbacks |
| `backend/app/composition/application_factory/factory.py` | CORS + `/health` |
| `backend/app/adapters/outbound/ml/client.py` | Fallback ML |
| `.env.example` | Nombres de variables (sin secretos) |
| `database/bootstrap_full.sql` | Esquema + RLS |
| `.github/workflows/*.yml` | CI actual |

---

## 12. Conclusión

El repositorio **sí está preparado arquitectónicamente** para desplegar **frontend y backend por separado** (y ML como tercer servicio opcional) desde un monorepo, usando root directories en Render.

**Bloqueantes / previos al procedimiento de despliegue:**

1. Aplicar SQL en Supabase y crear usuario real.  
2. Definir variables de entorno de producción (sin localhost).  
3. Decidir si se despliega ML o se usa solo el fallback del backend.  
4. Configurar build del frontend con la URL pública del backend.  
5. Desactivar demo en producción.  
6. (Recomendado) Remediación de vulnerabilidades de dependencias detectadas en auditorías previas.

**No se ha realizado el despliegue en Render.** Este documento es únicamente el diagnóstico técnico solicitado.

---

*INFORME_TECNICO_PRE_DESPLIEGUE.md — WEB_MINERA — 2026-10-30*
