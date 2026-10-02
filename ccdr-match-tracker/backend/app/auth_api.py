from datetime import timedelta
import secrets

from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from app.auth import Admin, CurrentUser, Database, cookie_name, digest, hash_password, lock_users, now, trusted_origin, verify_password
from app.auth_schemas import AuthRead, Login, UserCreate, UserRead, UserUpdate
from app.config import get_settings
from app.enums import UserRole
from app.models import AuthSession, LoginThrottle, User
from app import auth_debug

router = APIRouter(tags=["authentication"])


def no_cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"


@router.post("/auth/login", response_model=AuthRead)
def login(payload: Login, request: Request, response: Response, db: Database):
    auth_debug.fields(request, email_masked='***')
    trusted_origin(request)
    if request.headers.get("x-requested-with") != "CCDR":
        auth_debug.fields(request, reason='login_request_invalid')
        raise HTTPException(403, "Pedido de login inválido.")
    lock_users(db)
    instant = now()
    # Durable limits apply across workers. Never trust X-Forwarded-For here.
    buckets = [("email:" + payload.email, 10), ("ip:" + (request.client.host if request.client else "unknown"), 30)]
    for value, limit in buckets:
        key = digest(value)
        bucket = db.get(LoginThrottle, key)
        if bucket is None:
            bucket = LoginThrottle(key=key, attempts=0, resets_at=instant + timedelta(minutes=15))
            db.add(bucket)
        elif bucket.resets_at <= instant:
            bucket.attempts = 0
            bucket.resets_at = instant + timedelta(minutes=15)
        if bucket.attempts >= limit:
            auth_debug.fields(request, reason='login_throttled')
            db.rollback()
            raise HTTPException(429, "Demasiadas tentativas. Tente novamente dentro de 15 minutos.", headers={"Retry-After": "900"})
        bucket.attempts += 1
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email))
    valid = verify_password(payload.password.get_secret_value(), user.password_hash if user else None)
    if not valid or user is None or not user.is_active:
        auth_debug.fields(request, credentials_valid=False, reason='credentials_rejected')
        db.commit()
        raise HTTPException(401, "Email ou password inválidos.")
    # Replace the browser's previous session; never reuse an identifier from a request.
    previous = request.cookies.get(cookie_name())
    replaced_hashes = []
    if previous:
        deletion = delete(AuthSession).where(AuthSession.token_hash == digest(previous))
        if get_settings().auth_debug_logging:
            replaced_hashes = list(db.scalars(deletion.returning(AuthSession.token_hash)))
        else:
            db.execute(deletion)
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= instant))
    db.execute(delete(LoginThrottle).where(LoginThrottle.resets_at <= instant))
    token, csrf = secrets.token_urlsafe(32), secrets.token_hex(32)
    hours = get_settings().auth_session_hours
    db.add(AuthSession(token_hash=digest(token), user_id=user.id, csrf_token=csrf,
                       expires_at=instant + timedelta(hours=hours)))
    result = AuthRead(user=UserRead.model_validate(user), csrf_token=csrf)
    db.commit()
    auth_debug.remember_revoked(replaced_hashes)
    response.set_cookie(cookie_name(), token, max_age=hours * 3600, httponly=True,
                        secure=get_settings().auth_cookie_secure, samesite=get_settings().auth_cookie_samesite, path="/")
    auth_debug.fields(request, credentials_valid=True, session_created=True, user_id=user.id, role=user.role.value,
                      reason='authenticated', cookie_max_age_present=True, cookie_expires_present=False,
                      session_db_id_logged=False)
    no_cache(response)
    return result


@router.get("/auth/me", response_model=AuthRead)
def me(request: Request, response: Response, user: CurrentUser):
    no_cache(response)
    return AuthRead(user=UserRead.model_validate(user), csrf_token=request.state.auth_session.csrf_token)


@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response, db: Database, user: CurrentUser):
    revoked_hash = request.state.auth_session.token_hash
    db.delete(request.state.auth_session)
    db.commit()
    auth_debug.remember_revoked([revoked_hash])
    response.delete_cookie(cookie_name(), path="/", secure=get_settings().auth_cookie_secure, httponly=True, samesite=get_settings().auth_cookie_samesite)
    no_cache(response)


@router.get("/users", response_model=list[UserRead])
def users(db: Database, admin: Admin):
    return db.scalars(select(User).order_by(User.name, User.id)).all()


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Database, admin: Admin):
    values = payload.model_dump(exclude={"password"})
    user = User(**values, password_hash=hash_password(payload.password.get_secret_value()))
    db.add(user)
    try:
        db.flush()
        result = UserRead.model_validate(user)
        db.commit()
        return result
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Este email já está registado.") from None


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Database, admin: Admin):
    # current_user holds the same advisory lock as bootstrap and all writers.
    try:
        revoked_hashes = []
        user = db.scalar(select(User).where(User.id == user_id).with_for_update())
        if user is None:
            raise HTTPException(404, "Utilizador não encontrado.")
        role = payload.role if "role" in payload.model_fields_set else user.role
        active = payload.is_active if "is_active" in payload.model_fields_set else user.is_active
        if user.role == UserRole.ADMIN and user.is_active and user.password_hash and (role != UserRole.ADMIN or not active):
            count = db.scalar(select(func.count()).select_from(User).where(
                User.role == UserRole.ADMIN, User.is_active.is_(True), User.password_hash.is_not(None)))
            if count <= 1:
                raise HTTPException(409, "Não pode desativar ou despromover o último ADMIN ativo.")
        values = payload.model_dump(exclude_unset=True, exclude={"password"})
        for field, value in values.items():
            setattr(user, field, value)
        if payload.password is not None:
            user.password_hash = hash_password(payload.password.get_secret_value())
        if payload.model_fields_set & {"password", "role", "is_active", "email"}:
            if get_settings().auth_debug_logging:
                revoked_hashes = list(db.scalars(select(AuthSession.token_hash).where(AuthSession.user_id == user.id).limit(1024)))
            db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
        db.flush()
        result = UserRead.model_validate(user)
        db.commit()
        auth_debug.remember_revoked(revoked_hashes)
        return result
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Este email já está registado.") from None
    except Exception:
        db.rollback()
        raise
