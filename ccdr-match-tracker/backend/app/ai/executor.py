"""Provider-independent execution of explicitly registered read-only tools."""
from collections.abc import Mapping
from datetime import datetime, timezone
from time import perf_counter
from types import MappingProxyType
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.ai.context import resolve_match_context
from app.ai.policy import ExecutionBudget, ExecutionPolicyError
from app.ai.registry import TOOLS as _TOOLS, ToolDefinition as _ToolDefinition
from app.ai.schemas import (
    ToolErrorCode, ToolExecutionError,
    ToolExecutionFailure, ToolExecutionMetadata, ToolExecutionRequest,
    ToolExecutionResult, ToolExecutionSuccess, ToolName,
)

_ERROR_MESSAGES: Mapping[ToolErrorCode, str] = MappingProxyType({
    "UNKNOWN_TOOL": "Ferramenta não disponível.",
    "INVALID_ARGUMENTS": "Argumentos da ferramenta inválidos.",
    "UNAUTHENTICATED": "Sessão inexistente ou expirada.",
    "FORBIDDEN": "Acesso recusado.",
    "NOT_FOUND": "Jogo não encontrado.",
    "UNAVAILABLE": "Serviço de análise indisponível.",
    "INTERNAL_ERROR": "Não foi possível executar a ferramenta.",
    "ARGUMENTS_TOO_LARGE": "Os argumentos excedem o tamanho permitido.",
    "EXECUTION_LIMIT_REACHED": "Limite de execução atingido.",
    "DEADLINE_EXCEEDED": "Prazo de execução excedido.",
})
_HTTP_ERRORS: Mapping[int, ToolErrorCode] = MappingProxyType({
    401: "UNAUTHENTICATED", 403: "FORBIDDEN", 404: "NOT_FOUND", 503: "UNAVAILABLE",
})


def execute_tool(
    tool_name: str, arguments: dict[str, Any], *, request: Request, engine: Engine,
    budget: ExecutionBudget | None = None,
) -> ToolExecutionResult:
    """Validate one proposal and reauthenticate immediately before dispatch.

    Only tool_name/arguments may originate from an LLM. request and engine are
    injected by trusted server code; neither credentials nor scope are accepted
    inside arguments. Invalid proposals never reach authentication or the DB.

    budget is also server-owned: share one per request to enforce aggregate
    limits. Omitting it creates a budget for this single call only. No round is
    started implicitly. Deadline checks do not interrupt in-flight operations.

    Both the resolver and tool own short sessions and close them before returning.
    No authentication context, result or session is cached between executions.
    There is no model call, HTTP endpoint, retry loop or external operation here.
    """
    execution_id = uuid4()
    started_at, started = datetime.now(timezone.utc), perf_counter()
    validated_name: ToolName | None = None

    def metadata() -> ToolExecutionMetadata:
        return ToolExecutionMetadata(
            execution_id=execution_id, started_at=started_at,
            duration_ms=(perf_counter() - started) * 1000,
        )

    def failure(code: ToolErrorCode) -> ToolExecutionFailure:
        return ToolExecutionFailure(
            tool_name=validated_name,
            error=ToolExecutionError(code=code, message=_ERROR_MESSAGES[code]),
            metadata=metadata(),
        )

    if budget is None:
        budget = ExecutionBudget()
    elif not isinstance(budget, ExecutionBudget):
        return failure("INTERNAL_ERROR")

    try:
        budget.reserve_call(arguments)
    except ExecutionPolicyError as exc:
        return failure(exc.code)

    try:
        proposal = ToolExecutionRequest(tool_name=tool_name, arguments=arguments)
        validated_name = proposal.tool_name
        definition = _TOOLS[validated_name]
        validated_arguments = definition.arguments_schema.model_validate(proposal.arguments)
    except ValidationError as exc:
        # Never return Pydantic inputs, error contexts or exception text.
        invalid_name = validated_name is None and any(
            error["loc"] == ("tool_name",) for error in exc.errors(include_input=False)
        )
        return failure("UNKNOWN_TOOL" if invalid_name else "INVALID_ARGUMENTS")
    except KeyError:
        return failure("UNKNOWN_TOOL")

    try:
        context = resolve_match_context(request, engine=engine)
        budget.check_deadline()
        evidence = definition.handler(**validated_arguments.model_dump(), context=context, engine=engine)
        budget.check_deadline()
        return ToolExecutionSuccess(tool_name=validated_name, evidence=evidence, metadata=metadata())
    except ExecutionPolicyError as exc:
        return failure(exc.code)
    except HTTPException as exc:
        return failure(_HTTP_ERRORS.get(exc.status_code, "INTERNAL_ERROR"))
    except SQLAlchemyError:
        return failure("UNAVAILABLE")
    except Exception:
        # Includes invalid tool output; it is not an input-validation error.
        return failure("INTERNAL_ERROR")
