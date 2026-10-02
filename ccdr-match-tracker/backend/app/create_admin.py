"""Interactive first administrator bootstrap; no password in arguments or logs."""
from getpass import getpass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import hash_password, lock_users
from app.auth_schemas import UserCreate
from app.database import get_engine
from app.enums import UserRole
from app.models import User


def bootstrap(db: Session, payload: UserCreate) -> User:
    lock_users(db)
    if db.scalar(select(User.id).where(User.role == UserRole.ADMIN, User.is_active.is_(True),
                                      User.password_hash.is_not(None))) is not None:
        raise ValueError("Já existe um ADMIN ativo. Use a gestão de utilizadores.")
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    if user is not None and user.password_hash is not None:
        raise ValueError("Este email já tem credenciais. Use outro email.")
    if user is None:
        user = User(name=payload.name, email=payload.email)
        db.add(user)
    user.name = payload.name
    user.role = UserRole.ADMIN
    user.is_active = True
    user.password_hash = hash_password(payload.password.get_secret_value())
    db.flush()
    return user


def main():
    name, email = input("Nome do ADMIN: "), input("Email: ")
    password = getpass("Password (12 a 128 caracteres): ")
    if password != getpass("Confirmar password: "):
        raise SystemExit("As passwords não coincidem.")
    try:
        payload = UserCreate(name=name, email=email, password=password, role=UserRole.ADMIN)
        with Session(get_engine()) as db:
            bootstrap(db, payload)
            db.commit()
        print("Primeiro ADMIN criado. Pode iniciar sessão.")
    except ValueError as exc:
        # Validation errors hide passwords via the input model configuration.
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
