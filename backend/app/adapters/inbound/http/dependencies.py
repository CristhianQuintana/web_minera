"""Adaptador inbound FastAPI: traduce HTTP a puertos/casos de uso."""

from fastapi import Cookie, Depends, Header, Request

from app.application.auth_context import AuthContext
from app.application.services.platform import PlatformService
from app.application.use_cases import (
    ActivateAccountUseCase,
    AuthenticateUseCase,
    InviteUserUseCase,
    RegisterLotUseCase,
    ResolveSessionUseCase,
    ReviewAlertUseCase,
)
from app.composition.container import Container
from app.domain.exceptions import UnauthorizedError


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_platform(container: Container = Depends(get_container)) -> PlatformService:
    """Fachada de aplicación para operaciones aún no envueltas en un caso de uso dedicado."""
    return container.platform


def get_authenticate(container: Container = Depends(get_container)) -> AuthenticateUseCase:
    return container.authenticate


def get_register_lot(container: Container = Depends(get_container)) -> RegisterLotUseCase:
    return container.register_lot


def get_review_alert(container: Container = Depends(get_container)) -> ReviewAlertUseCase:
    return container.review_alert


def get_invite_user(container: Container = Depends(get_container)) -> InviteUserUseCase:
    return container.invite_user


def get_activate_account(container: Container = Depends(get_container)) -> ActivateAccountUseCase:
    return container.activate_account


def get_resolve_session(container: Container = Depends(get_container)) -> ResolveSessionUseCase:
    return container.resolve_session


def get_context(
    request: Request,
    resolve_session: ResolveSessionUseCase = Depends(get_resolve_session),
    authorization: str | None = Header(default=None),
    access_token: str | None = Cookie(default=None),
) -> AuthContext:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    token = token or access_token or request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError("Tu sesión ha expirado. Vuelve a iniciar sesión.")
    return resolve_session.execute(token)
