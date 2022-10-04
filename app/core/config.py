import sys
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):

    PROJECT_NAME: str = "ArgiBlockAPI"
    SENTRY_DSN: Optional[HttpUrl] = None
    API_PATH: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    # The following variables need to be defined in environment
    DATABASE_URL: PostgresDsn
    ASYNC_DATABASE_URL: Optional[PostgresDsn]
    STATIC_PATH: str = "./static"

    @validator("DATABASE_URL", pre=True)
    def change_database_url(cls, v: Optional[str], values: Dict[str, Any]):  
        """Replace postgres with postgresql"""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        return v

    @validator("ASYNC_DATABASE_URL")
    def build_async_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        """Builds ASYNC_DATABASE_URL from DATABASE_URL."""
        v = values["DATABASE_URL"]
        return v.replace("postgresql", "postgresql+asyncpg") if v else v

    SECRET_KEY: str
    #  END: required environment variables
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    PAGING_DEFAULT_SKIP: int = 0
    PAGING_DEFAULT_LIMIT: int = 10
    FIREBASE_CERT: dict = {}
    SERVER_NAME: str = ""
    SERVER_HOST: AnyHttpUrl = ""
    MEDIA_HOSTS: dict = {}

    @validator("MEDIA_HOSTS", check_fields=False)
    def get_media_hosts(cls, v: Optional[str], values: Dict[str, Any]) -> dict:
        return {"local": values["SERVER_HOST"], "s3": "", "youtube": ""}


settings = Settings()
