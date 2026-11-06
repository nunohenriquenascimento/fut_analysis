"""Resolve the server's roster scope through the existing authentication rules."""
from fastapi import HTTPException, Request
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import auth, statistics_service
from app.ai.schemas import AuthorizedMatchContext


def resolve_match_context(request: Request, *, engine: Engine) -> AuthorizedMatchContext:
    """Authenticate the request and return only the configured team/season IDs.

    No scope, role, user object or tool arguments are accepted. Authentication
    uses current_user exactly as existing statistics reads do: ADMIN, COACH and
    VIEWER can read. For POST requests its Origin/CSRF checks are preserved too.

    statistics_service.context resolves roster.py's server-owned names. This is
    the single-team policy boundary to replace when memberships are introduced;
    names or IDs from a request must never be forwarded to it.

    The owned session rolls back and closes before this function returns,
    releasing authentication locks/connections before any model invocation.
    The returned scope is a snapshot, not a credential: resolve again for each
    future dispatch, especially after a long-running model call. Call this at
    the server boundary without also opening a request-long auth transaction.
    """
    try:
        with Session(bind=engine, autoflush=False) as db:
            auth.current_user(request, db)
            try:
                roster = statistics_service.context(db)
            except HTTPException as exc:
                if exc.status_code != 404:
                    raise
                # Do not expose configured names, missing entities or seed commands.
                raise HTTPException(503, "Contexto de análise indisponível.") from None
            return AuthorizedMatchContext(team_id=roster.team_id, season_id=roster.season_id)
    except SQLAlchemyError:
        raise HTTPException(503, "Contexto de análise indisponível.") from None
