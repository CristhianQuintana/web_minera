<!-- Remediado en codigo: CORS ultimo, locks pip, Docker COPY explicito, CI/Docker --only-binary / npm ci --ignore-scripts. Ver commit asociado. -->

Add CORSMiddleware last in the middleware chain.

CORSMiddleware should be added last in the middleware chain python:S8414
Where is the issue?
Activity
backend/app/composition/application_factory/factory.py


See all issues in this file
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.inbound.http.errors import register_error_handlers
from app.adapters.inbound.http.rate_limit import RateLimitMiddleware
from app.adapters.inbound.http.routers import api_router, auth_router
from app.composition.container import build_container
from app.infrastructure.logging.logger import configure_logging
def create_app() -> FastAPI:
    configure_logging()
    container = build_container()
    settings = container.settings
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"
    openapi_url = None if settings.is_production else "/openapi.json"
    app = FastAPI(
        title="WEB_MINERA API",
        version="1.0.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    app.state.container = container
    origins: set[str] = {o for o in [settings.frontend_origin] if o}
    if not settings.is_production:
        origins.update(
            {
                "http://localhost",
                "http://localhost:3000",
                "http://127.0.0.1",
                "http://127.0.0.1:3000",
            }
        )
    extra = getattr(settings, "cors_extra_origins", "") or ""
    for origin in extra.split(","):
        cleaned = origin.strip()
        if cleaned:
            origins.add(cleaned)
    app.add_middleware(
Add CORSMiddleware last in the middleware chain.

        CORSMiddleware,
        allow_origins=sorted(origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware, limit=120, window=60)
    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(api_router)
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}
    return app

Copying recursively might inadvertently add sensitive data to the container. Make sure it is safe here.

Dockerfiles should not copy the build context using recursive or glob patterns docker:S6470
Where is the issue?
Activity
ml/Dockerfile


See all issues in this file
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
Copying recursively might inadvertently add sensitive data to the container. Make sure it is safe here.

ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "adapters.inbound.http.main:app", "--host", "0.0.0.0", "--port", "8001"]

Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation githubactions:S8541
Where is the issue?
Activity
.github/workflows/backend-ci.yml


See all issues in this file
name: backend-ci
on:
  push:
    paths: ["backend/**"]
  pull_request:
    paths: ["backend/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements/dev.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

      - run: ruff check app tests
      - run: pytest

Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions githubactions:S8544
Where is the issue?
Activity
.github/workflows/backend-ci.yml


See all issues in this file
name: backend-ci
on:
  push:
    paths: ["backend/**"]
  pull_request:
    paths: ["backend/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements/dev.txt
Using dependencies without locking resolved versions is security-sensitive.

      - run: ruff check app tests
      - run: pytest
      Omitting "--ignore-scripts" allows lifecycle scripts to run during package installation.

JavaScript package manager scripts should not be executed during installation githubactions:S6505
Where is the issue?
Activity
.github/workflows/frontend-ci.yml


See all issues in this file
name: frontend-ci
on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci
Omitting "--ignore-scripts" allows lifecycle scripts to run during package installation.

      - run: npm run lint
      - run: npx tsc --noEmit
      - run: npm test
      - run: npm run build
      "npx" can install packages on-demand and run their lifecycle scripts.

JavaScript package manager scripts should not be executed during installation githubactions:S6505
Where is the issue?
Activity
.github/workflows/frontend-ci.yml


See all issues in this file
name: frontend-ci
on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
"npx" can install packages on-demand and run their lifecycle scripts.

      - run: npm test
      - run: npm run build

Define exact package version to avoid installing unverified releases.

JavaScript dependencies should be locked to verified versions githubactions:S8543
Where is the issue?
Activity
.github/workflows/frontend-ci.yml


See all issues in this file
name: frontend-ci
on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
Define exact package version to avoid installing unverified releases.

      - run: npm test
      - run: npm run build

Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation githubactions:S8541
Where is the issue?
Activity
.github/workflows/integration-ci.yml


See all issues in this file
name: integration-ci
on:
  push:
  pull_request:
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements/dev.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

      - run: pytest backend/tests/unit
      - run: pip install -r ml/requirements.txt
      - run: pytest ml/tests
        env:
          PYTHONPATH: ml
          Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions githubactions:S8544
Where is the issue?
Activity
.github/workflows/integration-ci.yml


See all issues in this file
name: integration-ci
on:
  push:
  pull_request:
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements/dev.txt
Using dependencies without locking resolved versions is security-sensitive.

      - run: pytest backend/tests/unit
      - run: pip install -r ml/requirements.txt
      - run: pytest ml/tests
        env:
          PYTHONPATH: ml
          Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation githubactions:S8541
Where is the issue?
Activity
.github/workflows/integration-ci.yml


See all issues in this file
name: integration-ci
on:
  push:
  pull_request:
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements/dev.txt
      - run: pytest backend/tests/unit
      - run: pip install -r ml/requirements.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

      - run: pytest ml/tests
        env:
          PYTHONPATH: ml
          Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions githubactions:S8544
Where is the issue?
Activity
.github/workflows/integration-ci.yml


See all issues in this file
name: integration-ci
on:
  push:
  pull_request:
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements/dev.txt
      - run: pytest backend/tests/unit
      - run: pip install -r ml/requirements.txt
Using dependencies without locking resolved versions is security-sensitive.

      - run: pytest ml/tests
        env:
          PYTHONPATH: ml
          Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation githubactions:S8541
Where is the issue?
Activity
.github/workflows/ml-ci.yml


See all issues in this file
name: ml-ci
on:
  push:
    paths: ["ml/**"]
  pull_request:
    paths: ["ml/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ml
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

      - run: pytest
      Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions githubactions:S8544
Where is the issue?
Activity
.github/workflows/ml-ci.yml


See all issues in this file
name: ml-ci
on:
  push:
    paths: ["ml/**"]
  pull_request:
    paths: ["ml/**"]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ml
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
Using dependencies without locking resolved versions is security-sensitive.

      - run: pytest
      Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation docker:S8541
Where is the issue?
Activity
backend/Dockerfile


See all issues in this file
# WEB_MINERA backend — FastAPI (producción)
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements/base.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

COPY app app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions docker:S8544
Where is the issue?
Activity
backend/Dockerfile


See all issues in this file
# WEB_MINERA backend — FastAPI (producción)
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements/base.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
Using dependencies without locking resolved versions is security-sensitive.

COPY app app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Omitting "--ignore-scripts" allows lifecycle scripts to run during package installation.

JavaScript package manager scripts should not be executed during installation docker:S6505
Where is the issue?
Activity
frontend/Dockerfile


See all issues in this file
# WEB_MINERA frontend — Next.js 15 (producción)
# Node 22 alineado con el entorno de desarrollo del proyecto.
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps
Omitting "--ignore-scripts" allows lifecycle scripts to run during package installation.

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_* se incrustan en el build. Vacío = rutas relativas (/api/v1/...)
# vía Nginx en el mismo origen. No usar http://localhost:8000 ni /api (doble prefijo).
ARG NEXT_PUBLIC_API_URL=
ARG NEXT_PUBLIC_SUPABASE_URL=
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
COPY --from=build /app/package.json ./
COPY --from=build /app/package-lock.json ./
COPY --from=build /app/next.config.ts ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next
COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "run", "start", "--", "-H", "0.0.0.0", "-p", "3000"]
Assignee
Using dependencies without locking resolved versions is security-sensitive.

JavaScript dependencies should be locked to verified versions docker:S8543
Where is the issue?
Activity
frontend/Dockerfile


See all issues in this file
# WEB_MINERA frontend — Next.js 15 (producción)
# Node 22 alineado con el entorno de desarrollo del proyecto.
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps
Using dependencies without locking resolved versions is security-sensitive.

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_* se incrustan en el build. Vacío = rutas relativas (/api/v1/...)
# vía Nginx en el mismo origen. No usar http://localhost:8000 ni /api (doble prefijo).
ARG NEXT_PUBLIC_API_URL=
ARG NEXT_PUBLIC_SUPABASE_URL=
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
COPY --from=build /app/package.json ./
COPY --from=build /app/package-lock.json ./
COPY --from=build /app/next.config.ts ./
COPY --from=build /app/public ./public
COPY --from=build /app/.next ./.next
COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "run", "start", "--", "-H", "0.0.0.0", "-p", "3000"]

Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

Python package manager scripts should not be executed during installation docker:S8541
Where is the issue?
Activity
ml/Dockerfile


See all issues in this file
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
Omitting "--only-binary :all:" can lead to the execution of setup scripts. Make sure it is safe here.

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "adapters.inbound.http.main:app", "--host", "0.0.0.0", "--port", "8001"]

Using dependencies without locking resolved versions is security-sensitive.

Python dependencies should be locked to verified versions docker:S8544
Where is the issue?
Activity
ml/Dockerfile


See all issues in this file
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
Using dependencies without locking resolved versions is security-sensitive.

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "adapters.inbound.http.main:app", "--host", "0.0.0.0", "--port", "8001"]
