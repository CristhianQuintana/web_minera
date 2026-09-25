from app.adapters.outbound.external.email_adapter import SmtpEmailAdapter
from app.adapters.outbound.ml.client import MLServiceAdapter
from app.adapters.outbound.supabase.client import SupabaseGateway
from app.application.services.platform import PlatformService
from app.infrastructure.configuration.settings import Settings, get_settings


class Container:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.gateway = SupabaseGateway(self.settings)
        self.email = SmtpEmailAdapter(self.settings)
        self.ml = MLServiceAdapter(self.settings)
        self.platform = PlatformService(self.gateway, self.settings, self.email, self.ml)


def build_container() -> Container:
    return Container()
