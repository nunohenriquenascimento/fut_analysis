from typing import Annotated

from pydantic import ConfigDict, Field, SecretStr, StringConstraints, field_validator, model_validator

from app.enums import UserRole
from app.schemas import InputModel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Email = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=254)]


def normalize_email(value: str) -> str:
    value = value.strip().lower()
    if value.count("@") != 1 or any(char.isspace() for char in value):
        raise ValueError("Indique um email válido.")
    local, domain = value.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("Indique um email válido.")
    return value


class Login(InputModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    email: Email
    password: SecretStr = Field(min_length=1, max_length=128)
    _email = field_validator("email")(normalize_email)


class UserCreate(InputModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    name: Name
    email: Email
    password: SecretStr = Field(min_length=12, max_length=128)
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    _email = field_validator("email")(normalize_email)


class UserUpdate(InputModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    name: Name | None = None
    email: Email | None = None
    password: SecretStr | None = Field(default=None, min_length=12, max_length=128)
    role: UserRole | None = None
    is_active: bool | None = None
    _email = field_validator("email")(lambda value: normalize_email(value) if value is not None else value)

    @model_validator(mode="after")
    def supplied_fields(self):
        if not self.model_fields_set or any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Indique campos não nulos para atualizar.")
        return self


class UserRead(InputModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool


class AuthRead(InputModel):
    user: UserRead
    csrf_token: str
