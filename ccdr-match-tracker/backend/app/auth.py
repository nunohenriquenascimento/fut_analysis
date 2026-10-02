"""Opaque, revocable sessions. No identity or role is accepted from the client."""
from datetime import datetime, timezone
import hashlib
import hmac
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.enums import UserRole
from app.models import AuthSession, User
from app import auth_debug

Database = Annotated[Session, Depends(get_db)]


def now() -> datetime:
    return datetime.now(timezone.utc)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def cookie_name() -> str:
    return "__Host-ccdr_session" if get_settings().auth_cookie_secure else "ccdr_session"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    result = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**17, r=8, p=1,
                            maxmem=256 * 1024 * 1024, dklen=32)
    return f"scrypt$131072$8$1${salt}${result.hex()}"


def verify_password(password: str, encoded: str | None) -> bool:
    # Same work for nonexistent/legacy accounts; avoid an account-existence oracle.
    candidate = encoded or "scrypt$131072$8$1$" + "00" * 16 + "$" + "00" * 32
    try:
        kind, n, r, p, salt, expected = candidate.split("$")
        if (kind, n, r, p) != ("scrypt", "131072", "8", "1"):
            return False
        result = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p),
                                maxmem=256 * 1024 * 1024, dklen=32)
        return hmac.compare_digest(result.hex(), expected) and encoded is not None
    except (ValueError, TypeError):
        return False


def lock_users(db: Session) -> None:
    # One ordering for role changes, bootstrap and authorized mutations.
    db.execute(text("SELECT pg_advisory_xact_lock(620260006)"))


def trusted_origin(request: Request) -> None:
    auth_debug.fields(request, origin_validation_passed=request.headers.get("origin") in get_settings().cors_origins)
    if request.headers.get("origin") not in get_settings().cors_origins:
        auth_debug.fields(request, reason='origin_not_allowed')
        raise HTTPException(403, "Origem do pedido não autorizada.")


def session_user(db: Session, token: str | None, *, lock: bool = False) -> tuple[AuthSession, User]:
    if not token or len(token) != 43:
        raise HTTPException(401, "Sessão inexistente ou expirada.")
    query = select(AuthSession, User).join(User, User.id == AuthSession.user_id).where(
        AuthSession.token_hash == digest(token), AuthSession.expires_at > now(), User.is_active.is_(True))
    if lock:
        query = query.with_for_update(of=(AuthSession, User))
    row = db.execute(query).first()
    if row is None:
        raise HTTPException(401, "Sessão inexistente ou expirada.")
    return row


def current_user(request: Request, db: Database) -> User:
    token = request.cookies.get(cookie_name())
    if not token or len(token) != 43:
        auth_debug.fields(request, reason="session_cookie_missing" if not token else "session_cookie_invalid",
                          session_found=False, session_revoked=None, session_expired=None, user_found=None, user_active=None)
        raise HTTPException(401, "Sessão inexistente ou expirada.")
    writing = request.method not in {"GET", "HEAD", "OPTIONS"}
    if writing:
        lock_users(db)
    try:
        session, user = session_user(db, token, lock=writing)
    except HTTPException:
        if get_settings().auth_debug_logging and auth_debug.backend_path(request) == '/auth/me':
            # Observe only after the authoritative validation failed. No policy changes.
            try:
                row = db.get(AuthSession, digest(token))
                user_row = db.get(User, row.user_id) if row else None
                revoked = auth_debug.known_revoked(digest(token)) if row is None else False
                expired = row.expires_at <= now() if row else None
                reason = ('session_revoked' if revoked else 'session_not_found') if row is None else (
                    'session_expired' if expired else 'user_not_found' if user_row is None else 'user_inactive' if not user_row.is_active else 'validation_inconsistent')
                auth_debug.fields(request, reason=reason, session_found=row is not None, session_revoked=True if revoked else None if row is None else False,
                                  session_expired=expired, user_found=user_row is not None if row else None,
                                  user_active=user_row.is_active if user_row else None)
            except Exception:
                auth_debug.fields(request, reason='diagnostic_lookup_failed')
        raise
    auth_debug.fields(request, reason='authenticated', session_found=True, session_revoked=False,
                      session_expired=False, user_found=True, user_active=True, user_id=user.id, role=user.role.value)
    if writing:
        trusted_origin(request)
        if not hmac.compare_digest(request.headers.get("x-csrf-token", "").encode(), session.csrf_token.encode()):
            raise HTTPException(403, "Token CSRF inválido.")
    request.state.auth_session = session
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_editor(user: CurrentUser) -> User:
    if user.role not in {UserRole.ADMIN, UserRole.COACH}:
        raise HTTPException(403, "Esta ação requer ADMIN ou COACH.")
    return user


def require_admin(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Esta ação requer ADMIN.")
    return user


Editor = Annotated[User, Depends(require_editor)]
Admin = Annotated[User, Depends(require_admin)]
