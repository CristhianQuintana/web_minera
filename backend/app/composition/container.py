"""Composition root: único lugar que conoce adaptadores concretos."""

from app.adapters.outbound.external.email_adapter import SmtpEmailAdapter
from app.adapters.outbound.ml.client import MLServiceAdapter
from app.adapters.outbound.supabase.client import SupabaseGateway
from app.application.services.platform import PlatformService
from app.application.use_cases import (
    ActivateAccountUseCase,
    AuthenticateUseCase,
    InviteUserUseCase,
    RegisterLotUseCase,
    ResolveSessionUseCase,
    ReviewAlertUseCase,
)
from app.infrastructure.configuration.settings import Settings, get_settings


class Container:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        # Adaptadores outbound (concretos) — solo aquí
        self.gateway = SupabaseGateway(self.settings)
        self.email = SmtpEmailAdapter(self.settings)
        self.ml = MLServiceAdapter(self.settings)
        # Aplicación: depende de puertos (tipado estructural)
        self.platform = PlatformService(self.gateway, self.settings, self.email, self.ml)
        # Casos de uso inbound expuestos a los adaptadores HTTP
        self.authenticate = AuthenticateUseCase(self.platform)
        self.register_lot = RegisterLotUseCase(self.platform)
        self.review_alert = ReviewAlertUseCase(self.platform)
        self.invite_user = InviteUserUseCase(self.platform)
        self.activate_account = ActivateAccountUseCase(self.platform)
        self.resolve_session = ResolveSessionUseCase(self.platform)


def build_container() -> Container:
    return Container()
