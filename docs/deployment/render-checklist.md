# Checklist de despliegue en Render (Free)

## Backend (`web-minera-backend`)

| Parámetro | Valor |
|---|---|
| Root Directory | `backend` |
| Runtime | Python (usa `backend/.python-version` → **3.11.11**) |
| Build | `pip install -r requirements/base.txt` |
| Start | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Variables mínimas: `APP_ENV=production`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `FRONTEND_ORIGIN`, `INVITE_BASE_URL`.  
Opcionales: `SUPABASE_SERVICE_ROLE_KEY`, `ML_SERVICE_URL`, SMTP, `JWT_SECRET`, `CORS_EXTRA_ORIGINS`.

En producción el login demo queda **deshabilitado** automáticamente (`APP_ENV=production`).

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

No definir `NEXT_PUBLIC_ENABLE_DEMO_AUTH=true` en producción.

Tras cambiar `NEXT_PUBLIC_*`, forzar **Clear build cache + Redeploy**.
