from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.http.errors import register_error_handlers
from app.adapters.inbound.http.routers import api_router, auth_router
from app.composition.container import build_container
from app.infrastructure.logging.logger import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    container = build_container()
    app = FastAPI(title="WEB_MINERA API", version="1.0.0")
    app.state.container = container
    origins = {
        container.settings.frontend_origin,
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
    }
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(o for o in origins if o),
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
