"""Server-owned request budgets; no loop, worker or cancellation is created."""
from collections.abc import Callable
import json
from threading import Lock
from time import monotonic
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.ai.schemas import ToolErrorCode


class ExecutionPolicy(BaseModel):
    """Configure in server code, never from a tool proposal or catalogue."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    max_rounds: int = Field(default=4, ge=1)
    max_calls: int = Field(default=6, ge=1)
    # Reserved for future multi-game tools; today's tool reads exactly one game.
    max_games_per_query: int = Field(default=20, ge=1)
    max_argument_bytes: int = Field(default=4096, ge=1)
    timeout_seconds: float = Field(default=60.0, gt=0, allow_inf_nan=False)


class ExecutionPolicyError(Exception):
    """A fixed code only: never retain arguments or exception details."""

    def __init__(self, code: ToolErrorCode):
        self.code = code
        super().__init__(code)


class ExecutionBudget:
    """One server-created budget per request, shared by all its tool proposals.

    Calls count attempts, including invalid/unauthenticated/failed proposals.
    The future caller must invoke begin_round once per model tool-calling round;
    dispatch does not invent rounds. Exceeding rounds/calls seals new admission.

    A monotonic deadline is checked at boundaries only. It cannot interrupt
    synchronous database work or cancel an external operation. No DB session,
    auth context or conversational memory is retained here.
    """

    def __init__(
        self, policy: ExecutionPolicy | None = None, *, clock: Callable[[], float] = monotonic,
    ):
        if policy is not None and not isinstance(policy, ExecutionPolicy):
            raise TypeError("policy must be a server-created ExecutionPolicy")
        self._policy = policy if policy is not None else ExecutionPolicy()
        self._clock = clock
        self._deadline = clock() + self._policy.timeout_seconds
        self._calls = 0
        self._rounds = 0
        self._blocked = False
        self._lock = Lock()

    @property
    def policy(self) -> ExecutionPolicy:
        return self._policy

    @property
    def calls_used(self) -> int:
        with self._lock:
            return self._calls

    @property
    def rounds_used(self) -> int:
        with self._lock:
            return self._rounds

    def check_deadline(self) -> None:
        self.remaining_seconds()

    def remaining_seconds(self) -> float:
        """Remaining cooperative budget, usable to cap an HTTP transport timeout."""
        remaining = self._deadline - self._clock()
        if remaining <= 0:
            raise ExecutionPolicyError("DEADLINE_EXCEEDED")
        return remaining

    def _check_admission(self) -> None:
        self.check_deadline()
        if self._blocked:
            raise ExecutionPolicyError("EXECUTION_LIMIT_REACHED")

    def begin_round(self) -> None:
        with self._lock:
            self._check_admission()
            if self._rounds >= self._policy.max_rounds:
                self._blocked = True
                raise ExecutionPolicyError("EXECUTION_LIMIT_REACHED")
            self._rounds += 1

    def reserve_call(self, arguments: Any) -> None:
        """Reserve an attempt, then bound canonical JSON argument bytes (UTF-8).

        This operates on already-decoded arguments, not HTTP bodies or raw model
        output. Incremental encoding stops when the limit is exceeded. Invalid
        JSON values, NaN/Infinity and circular/deep structures are rejected.
        """
        with self._lock:
            self._check_admission()
            if self._calls >= self._policy.max_calls:
                self._blocked = True
                raise ExecutionPolicyError("EXECUTION_LIMIT_REACHED")
            self._calls += 1
            size = 0
            try:
                encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":"))
                for chunk in encoder.iterencode(arguments):
                    size += len(chunk.encode("utf-8"))
                    if size > self._policy.max_argument_bytes:
                        raise ExecutionPolicyError("ARGUMENTS_TOO_LARGE")
            except (TypeError, ValueError, RecursionError):
                raise ExecutionPolicyError("INVALID_ARGUMENTS") from None
            self.check_deadline()
