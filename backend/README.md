# Backend WEB_MINERA

API FastAPI con arquitectura hexagonal. FastAPI es un adaptador inbound.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/dev.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Pruebas:

```bash
pytest
```
