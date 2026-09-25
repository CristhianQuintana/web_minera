from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = "https://oewpepqrtoezbvrxhrfe.supabase.co"
    supabase_anon_key: str = "sb_publishable_51MkYSgxXND4Sfqzhz1smA_pke0IOJY"
    supabase_service_role_key: str = ""
    jwt_secret: str = ""
    ml_service_url: str = "http://localhost:8001"
    frontend_origin: str = "http://localhost:3000"
    app_env: str = "development"
    invite_expiry_hours: int = 72
    invite_base_url: str = "http://localhost:3000/activate-account"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@webminera.local"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def has_service_role(self) -> bool:
        return bool(self.supabase_service_role_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
