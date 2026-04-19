from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar


class Settings(BaseSettings):
    app_name: str = "Expire Hero API"
    environment: str = "development"
    debug: bool = True

    database_url: str
    redis_url: str | None = None

    cors_origins: str = "http://localhost:5173"

    firebase_project_id: str = "demo"
    firebase_client_email: str = "demo"
    firebase_private_key: str = "demo"

    stripe_secret_key: str = "demo"
    stripe_webhook_secret: str = "demo"
    frontend_url: str = "http://localhost:5173"

    # ✅ STAŁE (nie pola Pydantic)
    FREE_REMINDER_LIMIT: ClassVar[int] = 5
    PRO_REMINDER_LIMIT: ClassVar[int | None] = None

    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def firebase_private_key_fixed(self) -> str:
        return self.firebase_private_key.replace("\\n", "\n")


settings = Settings()