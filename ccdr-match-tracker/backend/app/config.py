from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    database_url: SecretStr
    app_env: Literal["development", "production"] = "development"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    auth_cookie_secure: bool = False
    auth_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    auth_session_hours: int = 8
    auth_debug_logging: bool = False

    @field_validator("auth_session_hours")
    @classmethod
    def valid_session_hours(cls, value: int) -> int:
        if not 1 <= value <= 24:
            raise ValueError("AUTH_SESSION_HOURS must be between 1 and 24")
        return value

    @field_validator("cors_origins")
    @classmethod
    def explicit_origins(cls, value: list[str]) -> list[str]:
        if not value or any(urlsplit(origin).scheme not in {"http", "https"}
                            or not urlsplit(origin).netloc or "*" in origin or urlsplit(origin).username
                            or urlsplit(origin).path
                            or urlsplit(origin).query or urlsplit(origin).fragment for origin in value):
            raise ValueError("CORS_ORIGINS must contain explicit origins without paths")
        return value

    @field_validator("database_url")
    @classmethod
    def require_postgresql(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
        except Exception:
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL") from None
        if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"} or not url.database:
            raise ValueError("Use postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE")
        return SecretStr(url.set(drivername="postgresql+psycopg").render_as_string(hide_password=False))

    @model_validator(mode="after")
    def production_security(self):
        if self.auth_cookie_samesite == "none" and not self.auth_cookie_secure:
            raise ValueError("AUTH_COOKIE_SAMESITE=none requires AUTH_COOKIE_SECURE=true")
        if self.app_env == "production":
            if not self.auth_cookie_secure:
                raise ValueError("Production requires AUTH_COOKIE_SECURE=true")
            if not {"cors_origins", "auth_cookie_samesite"} <= self.model_fields_set:
                raise ValueError("Production requires explicit CORS_ORIGINS and AUTH_COOKIE_SAMESITE")
            if any(urlsplit(origin).scheme != "https" or urlsplit(origin).hostname in {"localhost", "127.0.0.1", "::1"}
                   for origin in self.cors_origins):
                raise ValueError("Production CORS_ORIGINS must use public HTTPS origins")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
