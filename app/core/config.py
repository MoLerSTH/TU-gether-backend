# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Literal

class Settings(BaseSettings):
    PROJECT_NAME: str = "TU-Gether"
    ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = True

    API_PREFIX: str = "/api"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    CORS_ORIGINS: List[str] = ["*"]

    SESSION_SECRET: str = "CHANGE_ME_SESSION_SECRET"  # ใส่ใน .env ใน production
    COOKIE_NAME: str = "session"
    COOKIE_SECURE: bool = False    # True เมื่อรันหลัง HTTPS
    COOKIE_SAMESITE: str = "lax"   # "none" ถ้าข้ามโดเมนและใช้ HTTPS

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def is_debug(self) -> bool:
        return self.DEBUG and self.ENV != "prod"

settings = Settings()
