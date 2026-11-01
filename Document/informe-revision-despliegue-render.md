# Informe de revisión y corrección — Despliegue Render (WEB_MINERA)

**Fecha:** 2026-11-01  
**Repo:** https://github.com/CristhianQuintana/web_minera  
**Rama:** `main`

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

## Validaciones locales

| Prueba | Resultado |
|---|---|
| `python --version` (venv backend) | 3.11.9 |
| `pip install -r requirements/base.txt` | Ver evidencia en commit/CI |
| `GET /health` | Esperado `{"status":"ok"}` |
| `npm run build` (frontend) | Ver evidencia local |
| Supabase tablas/Auth real | **Pendiente** si el proyecto remoto aún no tiene bootstrap SQL |
| Deploy Live en Render | **Pendiente** tras push + Root Directory frontend |

## Acción manual obligatoria en Render Dashboard

1. Backend Root Directory: `backend` (ya debería estar).  
2. Frontend Root Directory: **`frontend`**.  
3. Env de producción configuradas (sin localhost).  
4. Redeploy tras el nuevo commit.
