"""Controlled dispatch using real sessions and disposable PostgreSQL schemas."""
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from types import MappingProxyType

import pytest
from fastapi import HTTPException
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import auth
from app.ai import executor, tools
from app.ai.schemas import (
    AuthorizedMatchContext, MatchStatisticsInput, ToolExecutionFailure,
    ToolExecutionRequest, ToolExecutionResult, ToolExecutionSuccess,
)
from app.enums import UserRole
from app.models import AuthSession, Match, Season, User
from app.statistics_service import match_statistics
from test_auth_ai_context import context_database, request_for  # noqa: F401 -- isolated fixture, no migrations


def replace_handler(monkeypatch, handler):
    monkeypatch.setattr(executor, "_TOOLS", MappingProxyType({
        "get_match_statistics": executor._ToolDefinition(MatchStatisticsInput, handler),
    }))


def test_registry_is_explicit_and_immutable():
    assert tuple(executor._TOOLS) == ("get_match_statistics",)
    definition = executor._TOOLS["get_match_statistics"]
    assert definition.arguments_schema is MatchStatisticsInput
    assert definition.handler is tools.get_match_statistics
    with pytest.raises(TypeError):
        executor._TOOLS["delete_match"] = definition
    with pytest.raises(FrozenInstanceError):
        definition.handler = lambda **_: None


@pytest.mark.parametrize("tool_name", [
    "unknown", "delete_match", "app.ai.tools.get_match_statistics", "__import__('os').system",
    "SELECT * FROM users", "private-secret-tool", "", None, 1, ["get_match_statistics"],
])
def test_unknown_tools_never_authenticate_or_execute(monkeypatch, tool_name):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid proposals must not access authentication or a database")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    result = executor.execute_tool(tool_name, {"match_id": 1}, request=request_for(), engine=None)
    assert isinstance(result, ToolExecutionFailure)
    assert result.error.code == "UNKNOWN_TOOL"
    assert result.tool_name is None
    assert result.error.message == "Ferramenta não disponível."
    assert "private-secret" not in result.model_dump_json()


@pytest.mark.parametrize("arguments", [
    {}, {"match_id": 0}, {"match_id": -1}, {"match_id": 2_147_483_648},
    {"match_id": True}, {"match_id": "1"}, {"match_id": 1.0}, {"match_id": None},
    {"match_id": []}, None, [], [["match_id", 1]], '{"match_id":1}', 1,
])
def test_invalid_arguments_never_authenticate_or_execute(monkeypatch, arguments):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid proposals must not access authentication or a database")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    result = executor.execute_tool("get_match_statistics", arguments, request=request_for(), engine=None)
    assert result.status == "error" and result.error.code == "INVALID_ARGUMENTS"
    assert result.error.message == "Argumentos da ferramenta inválidos."


@pytest.mark.parametrize("field", [
    "team_id", "season_id", "role", "permissions", "engine", "context", "request",
    "tool_name", "sql", "extra",
])
def test_additional_arguments_and_permission_injection_are_rejected(monkeypatch, field):
    def forbidden(*args, **kwargs):
        pytest.fail("Injected arguments must be rejected before resolving scope")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    result = executor.execute_tool("get_match_statistics", {"match_id": 1, field: "private-secret"},
                                   request=request_for(), engine=None)
    assert result.status == "error" and result.error.code == "INVALID_ARGUMENTS"
    assert "private-secret" not in result.model_dump_json()


def test_execution_envelope_forbids_additional_fields():
    proposal = ToolExecutionRequest(tool_name="get_match_statistics", arguments={"match_id": 1})
    assert proposal.model_dump() == {"tool_name": "get_match_statistics", "arguments": {"match_id": 1}}
    with pytest.raises(ValidationError):
        ToolExecutionRequest.model_validate({**proposal.model_dump(), "context": {"team_id": 999}})


@pytest.mark.parametrize("status, code", [
    (401, "UNAUTHENTICATED"), (403, "FORBIDDEN"), (404, "NOT_FOUND"),
    (503, "UNAVAILABLE"), (500, "INTERNAL_ERROR"), (422, "INTERNAL_ERROR"),
])
def test_authentication_errors_are_sanitized_and_prevent_dispatch(monkeypatch, status, code):
    def denied(*args, **kwargs):
        raise HTTPException(status, {"secret": "private-secret"}, headers={"X-Secret": "private-secret"})

    def forbidden(**kwargs):
        pytest.fail("Failed authentication must prevent dispatch")

    monkeypatch.setattr(executor, "resolve_match_context", denied)
    replace_handler(monkeypatch, forbidden)
    result = executor.execute_tool("get_match_statistics", {"match_id": 1}, request=request_for(), engine=None)
    assert result.status == "error" and result.error.code == code
    assert "private-secret" not in result.model_dump_json()


@pytest.mark.parametrize("stage", ["resolver", "handler"])
@pytest.mark.parametrize("kind, code", [("database", "UNAVAILABLE"), ("unexpected", "INTERNAL_ERROR")])
def test_internal_exceptions_are_sanitized(monkeypatch, stage, kind, code):
    def fail(*args, **kwargs):
        error = SQLAlchemyError if kind == "database" else RuntimeError
        raise error("private-secret connection string or SQL")

    monkeypatch.setattr(executor, "resolve_match_context", fail if stage == "resolver" else
                        lambda *_args, **_kwargs: AuthorizedMatchContext(team_id=1, season_id=1))
    replace_handler(monkeypatch, fail)
    result = executor.execute_tool("get_match_statistics", {"match_id": 1}, request=request_for(), engine=None)
    assert result.status == "error" and result.error.code == code
    assert "private-secret" not in result.model_dump_json()
    assert TypeAdapter(ToolExecutionResult).validate_json(result.model_dump_json()) == result


def test_invalid_tool_output_is_an_internal_error_not_an_argument_error(monkeypatch):
    monkeypatch.setattr(executor, "resolve_match_context",
                        lambda *_args, **_kwargs: AuthorizedMatchContext(team_id=1, season_id=1))
    replace_handler(monkeypatch, lambda **_: {"private-secret": "invalid evidence"})
    result = executor.execute_tool("get_match_statistics", {"match_id": 1}, request=request_for(), engine=None)
    assert result.status == "error" and result.error.code == "INTERNAL_ERROR"
    assert "private-secret" not in result.model_dump_json()


@pytest.mark.parametrize("role", list(UserRole))
def test_valid_execution_reuses_service_and_returns_evidence_and_metadata(context_database, role):
    state = context_database
    with Session(state.engine) as db:
        expected = match_statistics(db, state.match_ids[0])
    before = datetime.now(timezone.utc)
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request_for(state.tokens[role]), engine=state.engine)
    assert isinstance(result, ToolExecutionSuccess)
    assert result.tool_name == "get_match_statistics"
    assert result.evidence.statistics == expected
    assert result.evidence.scope.team_id == state.team_id
    assert result.evidence.scope.season_id == state.season_id
    assert before <= result.metadata.started_at <= result.evidence.queried_at <= datetime.now(timezone.utc)
    assert result.metadata.started_at.utcoffset().total_seconds() == 0
    assert result.metadata.duration_ms >= 0 and result.metadata.execution_id.version == 4
    assert TypeAdapter(ToolExecutionResult).validate_json(result.model_dump_json()) == result
    assert state.tokens[role] not in result.model_dump_json()
    assert state.csrf not in result.model_dump_json()
    assert state.engine.pool.checkedout() == 0


@pytest.mark.parametrize("case", ["absent", "malformed", "unknown", "expired", "revoked", "inactive"])
def test_missing_invalid_and_inactive_sessions_are_denied_before_tool(context_database, monkeypatch, case):
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

    def forbidden(**kwargs):
        pytest.fail("An invalid session must not execute tools")

    replace_handler(monkeypatch, forbidden)
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request_for(token), engine=state.engine)
    assert result.status == "error" and result.error.code == "UNAUTHENTICATED"
    assert result.error.message == "Sessão inexistente ou expirada."
    assert state.engine.pool.checkedout() == 0


@pytest.mark.parametrize("target", ["missing", "other_team", "other_season"])
def test_nonexistent_and_out_of_scope_matches_have_identical_errors(context_database, target):
    state = context_database
    match_id = {"missing": 2_147_483_647, "other_team": state.match_ids[1],
                "other_season": state.match_ids[2]}[target]
    result = executor.execute_tool("get_match_statistics", {"match_id": match_id},
                                   request=request_for(state.tokens[UserRole.ADMIN]), engine=state.engine)
    assert result.status == "error" and result.error.code == "NOT_FOUND"
    assert result.error.message == "Jogo não encontrado."
    assert "evidence" not in result.model_dump()
    assert state.engine.pool.checkedout() == 0


@pytest.mark.parametrize("case", ["valid", "missing_csrf", "invalid_csrf", "untrusted_origin"])
def test_post_preserves_csrf_and_origin_and_releases_auth_lock(context_database, case):
    state = context_database
    request = request_for(state.tokens[UserRole.VIEWER], method="POST",
                          csrf=None if case == "missing_csrf" else "forged" if case == "invalid_csrf" else state.csrf,
                          origin="https://untrusted.example" if case == "untrusted_origin" else "http://localhost:3000")
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request, engine=state.engine)
    assert result.status == ("success" if case == "valid" else "error")
    if case != "valid":
        assert result.error.code == "FORBIDDEN"
    assert state.engine.pool.checkedout() == 0
    with state.engine.connect() as connection:
        assert connection.scalar(text("SELECT pg_try_advisory_xact_lock(620260006)"))


def test_each_execution_reauthenticates_even_with_same_request(context_database):
    state = context_database
    token = state.tokens[UserRole.COACH]
    request = request_for(token)
    first = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                  request=request, engine=state.engine)
    assert first.status == "success"
    with Session(state.engine) as db:
        db.delete(db.get(AuthSession, auth.digest(token)))
        db.commit()
    second = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request, engine=state.engine)
    assert second.status == "error" and second.error.code == "UNAUTHENTICATED"
    assert first.metadata.execution_id != second.metadata.execution_id
    assert state.engine.pool.checkedout() == 0


def test_dispatch_closes_auth_before_tool_and_executes_only_reads(context_database, monkeypatch):
    state = context_database
    statements, commits = [], []

    def record(connection, cursor, statement, parameters, execution_context, executemany):
        statements.append(statement)

    def committed(connection):
        commits.append(True)

    def checked_handler(*, match_id, context, engine):
        assert engine is state.engine and state.engine.pool.checkedout() == 0
        assert context == AuthorizedMatchContext(team_id=state.team_id, season_id=state.season_id)
        return tools.get_match_statistics(match_id, context=context, engine=engine)

    replace_handler(monkeypatch, checked_handler)
    event.listen(state.engine, "before_cursor_execute", record)
    event.listen(state.engine, "commit", committed)
    try:
        result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
            request=request_for(state.tokens[UserRole.COACH], method="POST", csrf=state.csrf), engine=state.engine)
    finally:
        event.remove(state.engine, "before_cursor_execute", record)
        event.remove(state.engine, "commit", committed)
    assert result.status == "success" and not commits
    assert statements and all(statement.lstrip().split()[0].upper() in {"SELECT", "SET"}
                              for statement in statements)
    assert state.engine.pool.checkedout() == 0


def test_database_rejects_accidental_tool_write_and_executor_sanitizes_error(context_database, monkeypatch):
    state = context_database

    def accidental_write(db, match_id):
        db.execute(text("UPDATE matches SET venue = 'private-secret' WHERE id = :id"), {"id": match_id})
        pytest.fail("Read-only transaction must reject writes")

    monkeypatch.setattr(tools, "match_statistics", accidental_write)
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request_for(state.tokens[UserRole.COACH]), engine=state.engine)
    assert result.status == "error" and result.error.code == "UNAVAILABLE"
    assert "private-secret" not in result.model_dump_json()
    assert state.engine.pool.checkedout() == 0
    with Session(state.engine) as db:
        assert db.get(Match, state.match_ids[0]).venue is None


def test_missing_server_configuration_is_sanitized(context_database):
    state = context_database
    with Session(state.engine) as db:
        db.get(Season, state.season_id).name = "Unconfigured identity"
        db.commit()
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request_for(state.tokens[UserRole.ADMIN]), engine=state.engine)
    assert result.status == "error" and result.error.code == "UNAVAILABLE"
    assert result.error.message == "Serviço de análise indisponível."
