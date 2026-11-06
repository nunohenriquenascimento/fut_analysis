"""Context resolution: real auth, disposable schemas, and no Alembic execution."""
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
import json
import secrets
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import auth, statistics_service
from app.ai import context as context_service
from app.ai.schemas import AuthorizedMatchContext
from app.ai.tools import get_match_statistics
from app.database import Base, get_db
from app.enums import MatchStatus, UserRole
from app.main import app
from app.models import AuthSession, Match, Season, Team, User
from app.roster import CLUB_NAME, SEASON_NAME

ORIGIN = "http://localhost:3000"


def request_for(token=None, *, method="GET", csrf=None, origin=ORIGIN, forged=False):
    headers = [(b"origin", origin.encode())]
    if token is not None:
        headers.append((b"cookie", f"{auth.cookie_name()}={token}".encode()))
    if csrf is not None:
        headers.append((b"x-csrf-token", csrf.encode()))
    if forged:
        headers.extend([(b"x-role", b"ADMIN"), (b"x-team-id", b"999"), (b"x-season-id", b"999")])

    async def receive():
        return {"type": "http.request", "body": json.dumps({
            "team_id": 999, "season_id": 999, "role": "ADMIN", "permissions": ["*"],
        }).encode(), "more_body": False}

    return Request({"type": "http", "method": method, "path": "/internal/analysis",
                    "scheme": "http", "server": ("localhost", 8000), "client": ("127.0.0.1", 1),
                    "headers": headers, "query_string": (
                        b"team_id=999&season_id=999&role=ADMIN&permissions=*" if forged else b""
                    )}, receive=receive)


@pytest.fixture
def unit_session(monkeypatch):
    state = SimpleNamespace(db=object(), closed=False, arguments=None)

    @contextmanager
    def owned_session(**kwargs):
        state.arguments = kwargs
        try:
            yield state.db
        finally:
            state.closed = True

    monkeypatch.setattr(context_service, "Session", owned_session)
    return state


def test_delegates_auth_before_roster_and_closes_session(unit_session, monkeypatch):
    calls = []
    request, engine = request_for(), object()

    def authenticate(received_request, db):
        assert received_request is request and db is unit_session.db
        calls.append("auth")

    def roster(db):
        assert db is unit_session.db
        calls.append("roster")
        return SimpleNamespace(team_id=7, season_id=9)

    monkeypatch.setattr(auth, "current_user", authenticate)
    monkeypatch.setattr(statistics_service, "context", roster)
    result = context_service.resolve_match_context(request, engine=engine)
    assert result == AuthorizedMatchContext(team_id=7, season_id=9)
    assert calls == ["auth", "roster"]
    assert unit_session.closed
    assert unit_session.arguments == {"bind": engine, "autoflush": False}


@pytest.mark.parametrize("status", [401, 403])
def test_auth_denials_are_preserved_without_resolving_scope(unit_session, monkeypatch, status):
    # There is no read-denied active role today. Preserve a denial from the
    # authoritative auth implementation rather than inventing an AI role policy.
    def denied(*args):
        raise HTTPException(status, "Acesso recusado.")

    def forbidden_lookup(*args):
        pytest.fail("Unauthenticated/unauthorized callers must not discover roster configuration")

    monkeypatch.setattr(auth, "current_user", denied)
    monkeypatch.setattr(statistics_service, "context", forbidden_lookup)
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request_for(), engine=object())
    assert error.value.status_code == status
    assert error.value.detail == "Acesso recusado."
    assert unit_session.closed


@pytest.mark.parametrize("stage", ["auth", "roster"])
def test_database_errors_are_generic_and_release_session(unit_session, monkeypatch, stage):
    def unavailable(*args):
        raise SQLAlchemyError("private database URL or SQL details")

    monkeypatch.setattr(auth, "current_user", unavailable if stage == "auth" else lambda *_: None)
    monkeypatch.setattr(statistics_service, "context", unavailable)
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request_for(), engine=object())
    assert error.value.status_code == 503
    assert error.value.detail == "Contexto de análise indisponível."
    assert error.value.__suppress_context__
    assert unit_session.closed


@pytest.mark.parametrize("field", ["team_id", "season_id", "role", "permissions", "context", "user"])
def test_resolver_has_no_scope_or_identity_override_arguments(field):
    with pytest.raises(TypeError):
        context_service.resolve_match_context(request_for(), engine=None, **{field: 999})


@pytest.fixture
def context_database(postgres_schema):
    # Build current model tables in a new random schema. No migration fixture.
    engine = create_engine(postgres_schema(), pool_size=1, max_overflow=0, pool_timeout=1)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as db:
            other_team, team, opponent = (Team(name=name) for name in ["Other club", CLUB_NAME, "Opponent"])
            other_season = Season(name="Other season", starts_on=date(2025, 7, 1), ends_on=date(2026, 6, 30))
            season = Season(name=SEASON_NAME, starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
            db.add_all([other_team, team, opponent, other_season, season])
            db.flush()
            tokens, user_ids = {}, {}
            csrf = secrets.token_hex(32)
            for role in UserRole:
                user = User(name=role.value, email=f"{role.value.lower()}@context.test",
                            role=role, is_active=True)
                db.add(user)
                db.flush()
                token = secrets.token_urlsafe(32)
                db.add(AuthSession(token_hash=auth.digest(token), user_id=user.id,
                                   csrf_token=csrf, expires_at=auth.now() + timedelta(hours=1)))
                tokens[role] = token
                user_ids[role] = user.id
            matches = [Match(team_id=team_id, season_id=season_id, opponent_id=opponent.id,
                             matchday=1, kickoff_at=datetime(2026, 10, 4, 15, tzinfo=timezone.utc),
                             is_home=True, status=MatchStatus.FINISHED)
                       for team_id, season_id in [(team.id, season.id), (other_team.id, season.id),
                                                  (team.id, other_season.id)]]
            db.add_all(matches)
            db.flush()
            state = SimpleNamespace(engine=engine, tokens=tokens, csrf=csrf, user_ids=user_ids,
                                    team_id=team.id, season_id=season.id,
                                    match_ids=[match.id for match in matches])
            db.commit()
        yield state
    finally:
        engine.dispose()


@pytest.mark.parametrize("role", list(UserRole))
def test_all_existing_read_roles_resolve_configured_scope_and_use_tool(context_database, role):
    state = context_database
    context = context_service.resolve_match_context(request_for(state.tokens[role]), engine=state.engine)
    assert context == AuthorizedMatchContext(team_id=state.team_id, season_id=state.season_id)
    assert state.engine.pool.checkedout() == 0
    evidence = get_match_statistics(state.match_ids[0], context=context, engine=state.engine)
    assert evidence.scope.team_id == state.team_id and evidence.scope.season_id == state.season_id
    for match_id in state.match_ids[1:]:
        with pytest.raises(HTTPException) as error:
            get_match_statistics(match_id, context=context, engine=state.engine)
        assert error.value.status_code == 404
    with pytest.raises(ValidationError):
        context.team_id = 999


@pytest.mark.parametrize("case", ["absent", "malformed", "unknown", "expired", "revoked", "inactive"])
def test_missing_invalid_or_inactive_sessions_are_denied(context_database, case):
    state = context_database
    token = state.tokens[UserRole.VIEWER]
    with Session(state.engine) as db:
        session = db.get(AuthSession, auth.digest(token))
        if case == "expired":
            session.expires_at = auth.now() - timedelta(seconds=1)
        elif case == "revoked":
            db.delete(session)
        elif case == "inactive":
            db.get(User, state.user_ids[UserRole.VIEWER]).is_active = False
        db.commit()
    token = {"absent": None, "malformed": "bad", "unknown": "x" * 43}.get(case, token)
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request_for(token, forged=True), engine=state.engine)
    assert error.value.status_code == 401
    assert error.value.detail == "Sessão inexistente ou expirada."
    assert state.engine.pool.checkedout() == 0


@pytest.mark.parametrize("missing", ["team", "season"])
def test_unconfigured_roster_is_generic_and_never_falls_back(context_database, missing):
    state = context_database
    with Session(state.engine) as db:
        row = db.get(Team, state.team_id) if missing == "team" else db.get(Season, state.season_id)
        row.name = "Unconfigured identity"
        db.commit()
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request_for(state.tokens[UserRole.ADMIN]), engine=state.engine)
    assert error.value.status_code == 503
    assert error.value.detail == "Contexto de análise indisponível."
    assert state.engine.pool.checkedout() == 0


def test_request_body_query_and_claimed_role_cannot_change_scope(context_database):
    state = context_database
    request = request_for(state.tokens[UserRole.VIEWER], method="POST", csrf=state.csrf, forged=True)
    context = context_service.resolve_match_context(request, engine=state.engine)
    assert context.model_dump() == {"team_id": state.team_id, "season_id": state.season_id}
    assert state.engine.pool.checkedout() == 0
    with state.engine.connect() as connection:
        # current_user's POST advisory lock has already been released.
        assert connection.scalar(text("SELECT pg_try_advisory_xact_lock(620260006)"))


@pytest.mark.parametrize("case", ["missing_csrf", "invalid_csrf", "untrusted_origin"])
def test_post_keeps_existing_csrf_and_origin_protection(context_database, case):
    state = context_database
    request = request_for(state.tokens[UserRole.VIEWER], method="POST",
                          csrf=None if case == "missing_csrf" else "forged" if case == "invalid_csrf" else state.csrf,
                          origin="https://untrusted.example" if case == "untrusted_origin" else ORIGIN)
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request, engine=state.engine)
    assert error.value.status_code == 403
    assert state.engine.pool.checkedout() == 0
    with state.engine.connect() as connection:
        assert connection.scalar(text("SELECT pg_try_advisory_xact_lock(620260006)"))


def test_resolver_does_not_write_commit_or_retain_connection(context_database):
    state = context_database
    statements, commits = [], []

    def record(connection, cursor, statement, parameters, execution_context, executemany):
        statements.append(statement)

    def committed(connection):
        commits.append(True)

    event.listen(state.engine, "before_cursor_execute", record)
    event.listen(state.engine, "commit", committed)
    try:
        context_service.resolve_match_context(
            request_for(state.tokens[UserRole.COACH], method="POST", csrf=state.csrf), engine=state.engine,
        )
    finally:
        event.remove(state.engine, "before_cursor_execute", record)
        event.remove(state.engine, "commit", committed)
    assert not commits
    assert statements and all(statement.lstrip().startswith("SELECT") for statement in statements)
    assert state.engine.pool.checkedout() == 0


def test_session_revocation_is_seen_on_next_resolution(context_database):
    state = context_database
    token = state.tokens[UserRole.COACH]
    first = context_service.resolve_match_context(request_for(token), engine=state.engine)
    with Session(state.engine) as db:
        db.delete(db.get(AuthSession, auth.digest(token)))
        db.commit()
    with pytest.raises(HTTPException) as error:
        context_service.resolve_match_context(request_for(token), engine=state.engine)
    assert error.value.status_code == 401
    # A context is deliberately data, not a revocable bearer credential.
    assert first.team_id == state.team_id


@pytest.mark.parametrize("role", list(UserRole))
def test_existing_http_read_and_write_permissions_remain_unchanged(context_database, monkeypatch, role):
    state = context_database

    def database():
        with Session(state.engine) as db:
            yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, database)
    with TestClient(app) as client:
        headers = {"Cookie": f"{auth.cookie_name()}={state.tokens[role]}"}
        assert client.get("/auth/me", headers=headers).json()["user"]["role"] == role.value
        for path in [f"/matches/{state.match_ids[0]}/stats", f"/matches/{state.match_ids[0]}/live",
                     "/statistics/season", "/competitions"]:
            assert client.get(path, headers=headers).status_code == 200
        assert client.get(f"/matches/{state.match_ids[0]}/stats").status_code == 401
        if role == UserRole.VIEWER:
            denied = client.patch(f"/teams/{state.team_id}", json={"crest_path": None}, headers={
                **headers, "Origin": ORIGIN, "X-CSRF-Token": state.csrf,
            })
            assert denied.status_code == 403
    # Resolver and the existing stats handler use the same current_user rule.
    assert context_service.resolve_match_context(request_for(state.tokens[role]), engine=state.engine)
