from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Sin valores de proyecto embebidos: deben venir de variables de entorno.
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    jwt_secret: str = ""
    ml_service_url: str = ""
    frontend_origin: str = "http://localhost:3000"
    app_env: str = "development"
    invite_expiry_hours: int = 72
    invite_base_url: str = "http://localhost:3000/activate-account"
    # auto | true | false — en producción el demo solo se activa con "true" explícito
    allow_demo_auth: str = "auto"
    cors_extra_origins: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@webminera.local"

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"

    @property
    def has_service_role(self) -> bool:
        return bool(self.supabase_service_role_key.strip())

    @property
    def demo_auth_enabled(self) -> bool:
        """Demo login: auto=off en production; true fuerza PMV; false desactiva siempre."""
        flag = (self.allow_demo_auth or "auto").strip().lower()
        if flag in {"1", "true", "yes", "on"}:
            return True
        if flag in {"0", "false", "no", "off"}:
            return False
        return not self.is_production


@lru_cache
def get_settings() -> Settings:
    return Settings()
