"""Ollama-only settings; loading them never requires database configuration."""
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, StrictBool, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Thinking = StrictBool | Annotated[str, Field(min_length=1, max_length=32)] | None


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_", env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore", frozen=True, hide_input_in_errors=True,
    )

    base_url: str = "http://localhost:11434"
    # A configurable local default inherited from the prototype, not an installation check.
    model: str = Field(default="qwen3:8b", min_length=1, max_length=160)
    timeout_seconds: float = Field(default=180.0, gt=0, allow_inf_nan=False)
    connect_timeout_seconds: float = Field(default=5.0, gt=0, allow_inf_nan=False)
    think: Thinking = False
    max_response_bytes: int = Field(default=1_048_576, ge=1)

    @field_validator("base_url")
    @classmethod
    def safe_origin(cls, value: str) -> str:
        try:
            url = urlsplit(value)
            port = url.port
            valid = (url.scheme in {"http", "https"} and url.hostname
                     and url.username is None and url.password is None
                     and "?" not in value and "#" not in value and url.path in {"", "/"}
                     and (port is None or 1 <= port <= 65535)
                     and not any(char.isspace() or ord(char) < 32 for char in value))
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("Use an HTTP(S) origin without credentials, path, query or fragment")
        return value.rstrip("/")

    @field_validator("timeout_seconds", "connect_timeout_seconds", "max_response_bytes", mode="before")
    @classmethod
    def numeric_limits(cls, value):
        if isinstance(value, bool):
            raise ValueError("Invalid numeric limit")
        return value

    @field_validator("model")
    @classmethod
    def valid_model(cls, value: str) -> str:
        if not value.strip() or any(char.isspace() or ord(char) < 32 for char in value):
            raise ValueError("Invalid model name")
        return value

    @field_validator("think", mode="before")
    @classmethod
    def thinking_from_environment(cls, value):
        if isinstance(value, str):
            if value.casefold() in {"true", "1", "yes"}:
                return True
            if value.casefold() in {"false", "0", "no"}:
                return False
            if not value.strip() or any(char.isspace() for char in value):
                raise ValueError("Invalid thinking mode")
        return value
