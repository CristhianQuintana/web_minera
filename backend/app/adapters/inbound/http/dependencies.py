from fastapi import Cookie, Depends, Header, Request

from app.application.services.platform import PlatformService
from app.composition.container import Container
from app.domain.exceptions import UnauthorizedError
from app.infrastructure.security.auth_context import AuthContext


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_platform(container: Container = Depends(get_container)) -> PlatformService:
    return container.platform


def get_context(
    request: Request,
    platform: PlatformService = Depends(get_platform),
    authorization: str | None = Header(default=None),
    access_token: str | None = Cookie(default=None),
) -> AuthContext:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    token = token or access_token or request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
    return platform.resolve_context(token)
