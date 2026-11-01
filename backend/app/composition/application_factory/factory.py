from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.http.errors import register_error_handlers
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
        CORSMiddleware,
        allow_origins=sorted(origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(auth_router)
    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
