# Informe de revisión y corrección — Despliegue Render (WEB_MINERA)

**Fecha:** 2026-11-01  
**Repo:** https://github.com/CristhianQuintana/web_minera  
**Rama:** `main`  
**Commit publicado:** `4c0a9ce` — *fix: corregir configuración de despliegue en Render*

## Problemas identificados en Render (commit `4d9b0dd`)

| Servicio | Causa | Corrección |
|---|---|---|
| Backend | Render usaba **Python 3.14** → fallo `pydantic-core` / maturin | `backend/.python-version` + `backend/runtime.txt` → **3.11.11** |
| Frontend | Build en raíz del monorepo → no encuentra `package.json` | Root Directory en Render = **`frontend`** (configuración Dashboard) |

## Correcciones en código (este commit)

1. Pin de Python 3.11.11 para Render.  
2. Demo auth **deshabilitado** cuando `APP_ENV=production` (backend + frontend).  
3. CORS: en producción solo `FRONTEND_ORIGIN` (+ `CORS_EXTRA_ORIGINS` opcional).  
4. `/docs` y OpenAPI deshabilitados en producción.  
5. Eliminados fallbacks hardcodeados de Supabase en `settings.py` y `env.ts`.  
6. Checklist: `docs/deployment/render-checklist.md`.

## Validaciones locales (ejecutadas 2026-11-01)

| Prueba | Resultado |
|---|---|
| `python --version` (venv backend) | **3.11.9** |
| `pip install -r requirements/base.txt` | **OK** |
| Pytest isolation + health + auth demo | **12 passed** |
| Vitest demo + isolation | **9 passed** |
| `npm run build` (frontend) | **OK** (22 rutas generadas) |
| Supabase tablas/Auth real | **Pendiente** (aplicar `database/bootstrap_full.sql` + usuario Auth) |
| Deploy Live en Render | **Pendiente** — redeploy commit `4c0a9ce` + Root Directory `frontend` |

## Acción manual obligatoria en Render Dashboard

1. Backend Root Directory: `backend` (ya debería estar).  
2. Frontend Root Directory: **`frontend`**.  
3. Env de producción configuradas (sin localhost).  
4. Redeploy tras el nuevo commit.
