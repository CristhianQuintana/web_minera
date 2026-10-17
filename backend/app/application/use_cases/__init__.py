"""Casos de uso. Reciben puertos, nunca instancian adaptadores concretos."""

from __future__ import annotations

from typing import Any

from app.application.auth_context import AuthContext
from app.application.dto import (
    ActivateCommand,
    AlertReviewCommand,
    InviteCommand,
    LoginCommand,
    RegisterLotCommand,
)
from app.application.services.platform import PlatformService


class AuthenticateUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, command: LoginCommand) -> dict[str, Any]:
        return self._platform.authenticate(command)


class RegisterLotUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx: AuthContext, command: RegisterLotCommand) -> dict[str, Any]:
        return self._platform.register_lot(ctx, command)


class ReviewAlertUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx: AuthContext, alert_id: str, command: AlertReviewCommand) -> dict[str, Any]:
        return self._platform.review_alert(ctx, alert_id, command)


class InviteUserUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx: AuthContext, command: InviteCommand) -> dict[str, Any]:
        return self._platform.invite_user(ctx, command)


class ActivateAccountUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, command: ActivateCommand) -> dict[str, Any]:
        return self._platform.activate_account(command)


class ResolveSessionUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, access_token: str) -> AuthContext:
        return self._platform.resolve_context(access_token)
