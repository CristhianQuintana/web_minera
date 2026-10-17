# Docker — WEB_MINERA

Despliegue local con Docker Compose:

```text
Browser → http://localhost → nginx:80
                              ├── /        → frontend:3000
                              ├── /api/    → backend:8000/api/
                              └── /api/health → backend:8000/health
```

```bash
# Desde la raíz WEB_MINERA, con Docker Desktop abierto:
copy .env.example .env   # completar variables
docker compose up -d --build
docker compose ps
```

Abrir http://localhost y http://localhost/api/health
