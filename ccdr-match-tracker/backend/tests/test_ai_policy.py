"""Budget mechanics with fake clocks; no loop, sleeping or database needed."""
from concurrent.futures import ThreadPoolExecutor
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.ai.policy import ExecutionBudget, ExecutionPolicy, ExecutionPolicyError


def assert_code(code, operation):
    with pytest.raises(ExecutionPolicyError) as error:
        operation()
    assert error.value.code == code


def test_defaults_are_validated_and_immutable():
    policy = ExecutionPolicy()
    assert policy.model_dump() == dict(max_rounds=4, max_calls=6, max_games_per_query=20,
                                       max_argument_bytes=4096, timeout_seconds=60.0)
    with pytest.raises(ValidationError):
        policy.max_calls = 100
    with pytest.raises(TypeError):
        ExecutionBudget({"max_calls": 100})
    budget = ExecutionBudget(policy)
    assert budget.policy is policy and budget.calls_used == budget.rounds_used == 0
    with pytest.raises(AttributeError):
        budget.policy = ExecutionPolicy(max_calls=100)


@pytest.mark.parametrize("field", ["max_rounds", "max_calls", "max_games_per_query", "max_argument_bytes"])
@pytest.mark.parametrize("value", [0, -1, True, "4", 1.5])
def test_integer_limits_are_positive_and_strict(field, value):
    with pytest.raises(ValidationError):
        ExecutionPolicy(**{field: value})


@pytest.mark.parametrize("value", [0, -1, True, "60", float("inf"), float("nan")])
def test_timeout_is_positive_finite_and_numeric(value):
    with pytest.raises(ValidationError):
        ExecutionPolicy(timeout_seconds=value)


def test_policy_forbids_unknown_fields():
    with pytest.raises(ValidationError):
        ExecutionPolicy(permissions=["*"])


def test_call_and_round_limits_are_independent_and_cumulative():
    budget = ExecutionBudget(ExecutionPolicy(max_calls=3, max_rounds=2))
    budget.begin_round()
    budget.reserve_call({"match_id": 1})
    budget.reserve_call({"match_id": 2})
    budget.begin_round()
    budget.reserve_call({"match_id": 3})
    assert budget.calls_used == 3 and budget.rounds_used == 2
    assert_code("EXECUTION_LIMIT_REACHED", lambda: budget.reserve_call({"match_id": 4}))
    assert_code("EXECUTION_LIMIT_REACHED", budget.begin_round)
    assert budget.calls_used == 3 and budget.rounds_used == 2


def test_default_round_limit_seals_further_dispatch_without_inventing_rounds():
    budget = ExecutionBudget()
    for _ in range(4):
        budget.begin_round()
    assert_code("EXECUTION_LIMIT_REACHED", budget.begin_round)
    assert_code("EXECUTION_LIMIT_REACHED", lambda: budget.reserve_call({"match_id": 1}))
    assert budget.rounds_used == 4 and budget.calls_used == 0
    direct = ExecutionBudget()
    direct.reserve_call({"match_id": 1})
    assert direct.rounds_used == 0  # Dispatch is not a model-calling round.


def test_default_six_call_limit_is_atomic_under_concurrent_admission():
    budget = ExecutionBudget()

    def attempt(_):
        try:
            budget.reserve_call({"match_id": 1})
            return "accepted"
        except ExecutionPolicyError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(attempt, range(32)))
    assert outcomes.count("accepted") == budget.calls_used == 6
    assert outcomes.count("EXECUTION_LIMIT_REACHED") == 26


def test_argument_limit_counts_utf8_bytes_at_exact_boundary():
    arguments = {"text": "é⚽"}
    size = len(json.dumps(arguments, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    exact = ExecutionBudget(ExecutionPolicy(max_argument_bytes=size))
    exact.reserve_call(arguments)
    smaller = ExecutionBudget(ExecutionPolicy(max_argument_bytes=size - 1))
    assert_code("ARGUMENTS_TOO_LARGE", lambda: smaller.reserve_call(arguments))
    assert exact.calls_used == smaller.calls_used == 1


@pytest.mark.parametrize("arguments", [object(), {"secret": object()}, {"values": {1, 2}},
                                       {"value": float("nan")}, {"value": float("inf")}])
def test_non_json_arguments_are_controlled_and_still_count(arguments):
    budget = ExecutionBudget()
    assert_code("INVALID_ARGUMENTS", lambda: budget.reserve_call(arguments))
    assert budget.calls_used == 1


def test_circular_and_deep_arguments_are_controlled():
    circular = []
    circular.append(circular)
    deep = []
    for _ in range(1500):
        deep = [deep]
    budget = ExecutionBudget(ExecutionPolicy(max_argument_bytes=100_000))
    for arguments in [circular, deep]:
        assert_code("INVALID_ARGUMENTS", lambda: budget.reserve_call(arguments))
    assert budget.calls_used == 2


def test_deadline_is_monotonic_and_checked_without_sleeping():
    clock = SimpleNamespace(now=100.0)
    budget = ExecutionBudget(clock=lambda: clock.now)
    clock.now = 159.999
    budget.check_deadline()
    clock.now = 160.0
    assert_code("DEADLINE_EXCEEDED", budget.check_deadline)
    assert_code("DEADLINE_EXCEEDED", budget.begin_round)
    assert_code("DEADLINE_EXCEEDED", lambda: budget.reserve_call({"match_id": 1}))
    assert budget.calls_used == budget.rounds_used == 0
