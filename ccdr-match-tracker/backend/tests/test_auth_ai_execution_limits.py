"""Actual dispatch budgets, with isolated PostgreSQL and no model integration."""
from types import MappingProxyType, SimpleNamespace

import pytest

from app.ai import executor, tools
from app.ai.policy import ExecutionBudget, ExecutionPolicy, ExecutionPolicyError
from app.enums import UserRole
from test_auth_ai_context import context_database, request_for  # noqa: F401 -- no migration fixture


def test_shared_budget_caps_real_executions_and_closes_connections(context_database, monkeypatch):
    state = context_database
    budget = ExecutionBudget(ExecutionPolicy(max_calls=2))
    auth_calls = []
    real_resolver = executor.resolve_match_context

    def resolve(request, *, engine):
        auth_calls.append(True)
        return real_resolver(request, engine=engine)

    monkeypatch.setattr(executor, "resolve_match_context", resolve)
    request = request_for(state.tokens[UserRole.VIEWER])
    for _ in range(2):
        assert executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                     request=request, engine=state.engine, budget=budget).status == "success"
        assert state.engine.pool.checkedout() == 0
    rejected = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                     request=request, engine=state.engine, budget=budget)
    assert rejected.error.code == "EXECUTION_LIMIT_REACHED"
    assert budget.calls_used == len(auth_calls) == 2


def test_failed_proposals_consume_attempts_without_authentication(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Invalid or exhausted proposals must not authenticate")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    budget = ExecutionBudget(ExecutionPolicy(max_calls=2))
    for name, args, code in [("unknown", {"match_id": 1}, "UNKNOWN_TOOL"),
                             ("get_match_statistics", {"match_id": False}, "INVALID_ARGUMENTS"),
                             ("get_match_statistics", {"match_id": 1}, "EXECUTION_LIMIT_REACHED")]:
        result = executor.execute_tool(name, args, request=None, engine=None, budget=budget)
        assert result.error.code == code
    assert budget.calls_used == 2


def test_explicit_round_limit_prevents_further_real_execution(context_database):
    state = context_database
    budget = ExecutionBudget(ExecutionPolicy(max_rounds=1))
    budget.begin_round()
    request = request_for(state.tokens[UserRole.COACH])
    assert executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                 request=request, engine=state.engine, budget=budget).status == "success"
    with pytest.raises(ExecutionPolicyError) as error:
        budget.begin_round()
    assert error.value.code == "EXECUTION_LIMIT_REACHED"
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
                                   request=request, engine=state.engine, budget=budget)
    assert result.error.code == "EXECUTION_LIMIT_REACHED"
    assert budget.calls_used == budget.rounds_used == 1


def test_argument_bytes_are_enforced_before_auth_and_are_configurable(context_database, monkeypatch):
    state = context_database
    request = request_for(state.tokens[UserRole.COACH])
    exact = ExecutionBudget(ExecutionPolicy(max_argument_bytes=len('{"match_id":1}')))
    assert state.match_ids[0] == 1
    assert executor.execute_tool("get_match_statistics", {"match_id": 1}, request=request,
                                 engine=state.engine, budget=exact).status == "success"

    def forbidden(*args, **kwargs):
        pytest.fail("Oversized arguments must not authenticate")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    for arguments, budget in [({"match_id": 1}, ExecutionBudget(ExecutionPolicy(max_argument_bytes=13))),
                               ({"match_id": 1, "secret": "private" * 1000}, ExecutionBudget())]:
        result = executor.execute_tool("get_match_statistics", arguments, request=None, engine=None, budget=budget)
        assert result.error.code == "ARGUMENTS_TOO_LARGE"
        assert "private" not in result.model_dump_json()


@pytest.mark.parametrize("field", ["policy", "budget", "max_calls", "timeout_seconds"])
def test_llm_cannot_supply_policy_or_budget(monkeypatch, field):
    def forbidden(*args, **kwargs):
        pytest.fail("Policy injection must not authenticate")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    result = executor.execute_tool("get_match_statistics", {"match_id": 1, field: 999},
                                   request=None, engine=None)
    assert result.error.code == "INVALID_ARGUMENTS"


def test_untrusted_budget_dictionary_is_not_accepted():
    result = executor.execute_tool("get_match_statistics", {"match_id": 1}, request=None,
                                   engine=None, budget={"max_calls": 999})
    assert result.error.code == "INTERNAL_ERROR"


def test_expired_budget_rejects_before_authentication(monkeypatch):
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(clock=lambda: clock.now)
    clock.now = 60.0

    def forbidden(*args, **kwargs):
        pytest.fail("Expired budget must not authenticate")

    monkeypatch.setattr(executor, "resolve_match_context", forbidden)
    result = executor.execute_tool("get_match_statistics", {"match_id": 1}, request=None,
                                   engine=None, budget=budget)
    assert result.error.code == "DEADLINE_EXCEEDED" and budget.calls_used == 0


def test_deadline_after_authentication_prevents_tool_start(context_database, monkeypatch):
    state = context_database
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(clock=lambda: clock.now)
    real_resolver = executor.resolve_match_context

    def slow_resolver(request, *, engine):
        context = real_resolver(request, engine=engine)
        clock.now = 60.0
        return context

    def forbidden(**kwargs):
        pytest.fail("Tool must not start after the budget deadline")

    monkeypatch.setattr(executor, "resolve_match_context", slow_resolver)
    monkeypatch.setattr(executor, "_TOOLS", MappingProxyType({
        "get_match_statistics": executor._ToolDefinition(
            executor._TOOLS["get_match_statistics"].arguments_schema, forbidden,
        ),
    }))
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
        request=request_for(state.tokens[UserRole.VIEWER]), engine=state.engine, budget=budget)
    assert result.error.code == "DEADLINE_EXCEEDED"
    assert state.engine.pool.checkedout() == 0


def test_deadline_after_tool_discards_result_without_claiming_cancellation(context_database, monkeypatch):
    state = context_database
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(clock=lambda: clock.now)
    completed = []

    def slow_handler(**kwargs):
        evidence = tools.get_match_statistics(**kwargs)
        completed.append(True)  # Work completed: no cancellation is claimed.
        clock.now = 60.0
        return evidence

    monkeypatch.setattr(executor, "_TOOLS", MappingProxyType({
        "get_match_statistics": executor._ToolDefinition(
            executor._TOOLS["get_match_statistics"].arguments_schema, slow_handler,
        ),
    }))
    result = executor.execute_tool("get_match_statistics", {"match_id": state.match_ids[0]},
        request=request_for(state.tokens[UserRole.VIEWER]), engine=state.engine, budget=budget)
    assert result.error.code == "DEADLINE_EXCEEDED"
    assert "evidence" not in result.model_dump() and completed == [True]
    assert state.engine.pool.checkedout() == 0
