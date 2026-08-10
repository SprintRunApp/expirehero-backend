from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar
from pydantic import Field

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
    frontend_url: str = "https://www.expireheros.app"

    stripe_starter_price_id: str = "price_1Tr4CYAtG4cgBkJ8PZfCGQwx"
    stripe_pro_price_id: str = "price_1Tr4G8AtG4cgBkJ8CgLaAUfz"
    stripe_business_price_id: str = "price_1TrCwpAtG4cgBkJ8L3liLu01"

    # ✅ STAŁE (nie pola Pydantic)
    FREE_REMINDER_LIMIT: ClassVar[int] = 9999
    PRO_REMINDER_LIMIT: ClassVar[int | None] = None

    RESEND_API_KEY: str = "demo"
    RESEND_FROM_EMAIL: str = "ExpireHeroes <onboarding@resend.dev>"



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True   # 🔥 ważne dla aliasów
    )

    SENDGRID_API_KEY: str = Field(..., alias="SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL: str = Field(..., alias="SENDGRID_FROM_EMAIL")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def firebase_private_key_fixed(self) -> str:
        return self.firebase_private_key.replace("\\n", "\n")


settings = Settings()