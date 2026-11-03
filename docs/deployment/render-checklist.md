# Checklist de despliegue en Render (Free)

## Backend (`web-minera-backend`)

| Parámetro | Valor |
|---|---|
| Root Directory | `backend` |
| Runtime | Python (usa `backend/.python-version` → **3.11.11**) |
| Build | `pip install -r requirements/base.txt` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Variables mínimas:

```env
APP_ENV=production
SUPABASE_URL=https://<proyecto>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
FRONTEND_ORIGIN=https://<frontend>.onrender.com
INVITE_BASE_URL=https://<frontend>.onrender.com/activate-account
```

Opcionales: `SUPABASE_SERVICE_ROLE_KEY`, `ML_SERVICE_URL`, SMTP, `JWT_SECRET`, `CORS_EXTRA_ORIGINS`.

**Importante:** no definir `ALLOW_DEMO_AUTH` ni ningún bypass de autenticación. La API solo acepta JWT emitidos por Supabase Auth.

### Servicio ML (`web-minera-ml`)

| Parámetro | Valor |
|---|---|
| Root Directory | `ml` |
| Build | `pip install -r requirements.txt` |
| Start | `PYTHONPATH=. uvicorn adapters.inbound.http.main:app --host 0.0.0.0 --port $PORT` |
| Health | `GET /health` |

En el backend: `ML_SERVICE_URL=https://<web-minera-ml>.onrender.com` (sin `/` final).  
Además, en Supabase hay que crear las tablas con `database/seeds/APPLY_FIX_BALANCE_ML_DEMO.sql` (Balance + ML + limpieza DEMO).

## Frontend (`web-minera-frontend`)

| Parámetro | Valor |
|---|---|
| Root Directory | **`frontend`** (obligatorio; monorepo) |
| Runtime | Node 22 |
| Build | `npm install --legacy-peer-deps && npm run build` |
| Start | `npm run start -- -H 0.0.0.0 -p $PORT` |

Variables de **build**:

```env
NEXT_PUBLIC_API_URL=https://<backend>.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://<proyecto>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
```

No definir `NEXT_PUBLIC_ENABLE_DEMO_AUTH`. Tras cambiar `NEXT_PUBLIC_*`, forzar **Clear build cache + Redeploy**.

## Usuario real

1. Crear el usuario en **Supabase Auth → Users**.
2. Ejecutar el SQL de bootstrap (`database/bootstrap_full.sql`) si las tablas aún no existen.
3. Asignar perfil y organización con `database/seeds/promote_admin.sql` (ajustar correo).
4. Verificar login en producción con ese usuario (sin tokens `demo-*`).
