"""Casos de uso. Reciben puertos, nunca instancian adaptadores concretos."""

from app.application.services.platform import PlatformService


class RegisterLotUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx, command):
        return self._platform.register_lot(ctx, command)


class ReviewAlertUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx, alert_id, command):
        return self._platform.review_alert(ctx, alert_id, command)


class InviteUserUseCase:
    def __init__(self, platform: PlatformService) -> None:
        self._platform = platform

    def execute(self, ctx, command):
        return self._platform.invite_user(ctx, command)
