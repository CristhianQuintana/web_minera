# WEB_MINERA

Plataforma web de trazabilidad y cadena de custodia para pequeña minería responsable.

Workspace hexagonal independiente de `APP_MINERA`. Comparte el mismo proyecto Supabase.

## Arranque local

1. Aplicar en Supabase SQL Editor el archivo `database/supabase_compile.sql` (requiere que 0001, 0004 y 0005 de APP_MINERA ya estén aplicadas).
2. Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

3. ML (opcional, el backend tiene fallback):

```bash
cd ml
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn presentation.api.main:app --port 8001
```

4. Frontend:

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Abrir http://localhost:3000

## Credenciales Supabase (públicas)

Las mismas de la app móvil:

- URL: `https://oewpepqrtoezbvrxhrfe.supabase.co`
- Anon / publishable key: `sb_publishable_51MkYSgxXND4Sfqzhz1smA_pke0IOJY`

Nunca colocar `service_role` en el frontend. Si se configura `SUPABASE_SERVICE_ROLE_KEY` en el backend, se habilitan invitaciones Admin de Auth.

## Acceso

No hay registro público. Use un usuario existente de Auth (por ejemplo `productor.prueba@cooperativa.org`) o invite desde `/users` con un administrador.

## Docker

```bash
docker compose up --build
```
