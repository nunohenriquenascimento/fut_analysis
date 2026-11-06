"""Request-local Ollama orchestration; execution authority stays in executor.py."""
import re
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.engine import Engine

from app.ai import executor
from app.ai.catalog import get_tool_catalog
from app.ai.context import resolve_match_context
from app.ai.facts import build_response
from app.ai.ollama_client import OllamaClient, OllamaClientError
from app.ai.ollama_schemas import OllamaMessage
from app.ai.policy import ExecutionBudget, ExecutionPolicy, ExecutionPolicyError
from app.ai.prompts import FOOTBALL_ANALYST_PROMPT, tool_result_content
from app.ai.schemas import (
    AgentClarification, AgentError, AgentErrorCode, AgentFailure, AgentInput, AgentMetadata, AgentResult,
)

_ERRORS: dict[AgentErrorCode, str] = {
    "INVALID_QUESTION": "Indique uma pergunta válida com até 4000 caracteres.",
    "UNAUTHENTICATED": "Sessão inexistente ou expirada.",
    "FORBIDDEN": "Acesso recusado.",
    "UNAVAILABLE": "Serviço de análise indisponível.",
    "INTERNAL_ERROR": "Não foi possível concluir a análise.",
    "EXECUTION_LIMIT_REACHED": "Limite de execução atingido.",
    "DEADLINE_EXCEEDED": "Prazo de execução excedido.",
    "OLLAMA_TIMEOUT": "O Ollama excedeu o tempo de espera.",
    "OLLAMA_UNAVAILABLE": "Não foi possível obter uma resposta do Ollama.",
    "INVALID_MODEL_RESPONSE": "Resposta do modelo inválida ou incompleta.",
}
_AUTH_ERRORS = {401: "UNAUTHENTICATED", 403: "FORBIDDEN", 503: "UNAVAILABLE"}
_FATAL_TOOL_ERRORS = {
    "UNAUTHENTICATED", "FORBIDDEN", "UNAVAILABLE", "INTERNAL_ERROR",
    "EXECUTION_LIMIT_REACHED", "DEADLINE_EXCEEDED",
}


def run_agent(
    question: str, *, request: Request, engine: Engine, client: OllamaClient,
    policy: ExecutionPolicy | None = None,
) -> AgentResult:
    """Run one isolated analysis, with one shared budget and no persistent history.

    Server-owned dependencies/policy are never taken from the question or model.
    Four tool rounds may be followed by one model request for the final answer;
    a fifth proposal round is refused. Calls run sequentially in proposal order.

    Authenticate before sending any context to the model and before returning a
    final answer. The executor independently reauthenticates every admitted call.
    All of those owned DB sessions close before HTTP. This function must not be
    invoked inside an unrelated, long-lived transaction created by its caller.
    """
    started_at, started, execution_id = datetime.now(timezone.utc), perf_counter(), uuid4()
    budget = ExecutionBudget(policy)
    evidence, tool_errors = [], []
    model_requests = 0

    def metadata() -> AgentMetadata:
        return AgentMetadata(execution_id=execution_id, started_at=started_at,
            duration_ms=(perf_counter() - started) * 1000, rounds_used=budget.rounds_used,
            calls_used=budget.calls_used, model_requests=model_requests)

    def failure(code: AgentErrorCode) -> AgentFailure:
        # Revocation/denial must never release previously obtained private evidence.
        denied = code in {"UNAUTHENTICATED", "FORBIDDEN"}
        return AgentFailure(error=AgentError(code=code, message=_ERRORS[code]),
            evidence=[], tool_errors=[] if denied else tool_errors,
            metadata=metadata())

    try:
        parsed = AgentInput(question=question)
        if not parsed.question.strip():
            return failure("INVALID_QUESTION")
    except ValidationError:
        return failure("INVALID_QUESTION")

    # Explicit, conservative identification. Never let the model choose an arbitrary
    # game. This is question interpretation, not authorization; the executor still
    # authorizes every admitted call. Multiple/unsupported forms need clarification.
    identifiers = re.findall(r"\bjogo\s+#?([0-9]+)\b", parsed.question, re.IGNORECASE)
    identified = {int(value) for value in identifiers if len(value) <= 10}
    ambiguous_list = re.search(
        r"\bjogo\s+#?[0-9]+\s*(?:,|/|ou|e)\s*(?:o\s+)?(?:jogo\s+)?#?[0-9]+\b",
        parsed.question, re.IGNORECASE,
    )
    match_id = (next(iter(identified)) if len(identified) == 1 and not ambiguous_list
                and all(len(value) <= 10 for value in identifiers) else None)
    unsupported_metrics = bool(re.search(r"\b(xg|posse|precisão de passe)\b", parsed.question, re.IGNORECASE))
    try:
        budget.check_deadline()
        resolve_match_context(request, engine=engine)
        budget.check_deadline()
        if match_id is None or not 0 < match_id <= 2_147_483_647:
            return AgentClarification(metadata=metadata())
    except HTTPException as exc:
        return failure(_AUTH_ERRORS.get(exc.status_code, "INTERNAL_ERROR"))
    except ExecutionPolicyError as exc:
        return failure(exc.code)
    except Exception:
        return failure("INTERNAL_ERROR")

    messages = [OllamaMessage(role="system", content=FOOTBALL_ANALYST_PROMPT),
                OllamaMessage(role="user", content=parsed.question)]
    catalog = get_tool_catalog()
    try:
        while True:
            budget.check_deadline()
            resolve_match_context(request, engine=engine)  # Closed before inference.
            budget.check_deadline()
            model_requests += 1
            response = client.chat(messages, tools=catalog, stream=False, budget=budget)
            budget.check_deadline()
            if response.done_reason not in {None, "stop"}:
                return failure("INVALID_MODEL_RESPONSE")
            message = response.message
            messages.append(message)
            if message.tool_calls:
                budget.begin_round()
                for call in message.tool_calls:
                    proposed_id = call.function.arguments.get("match_id")
                    if (call.function.name == "get_match_statistics" and type(proposed_id) is int
                            and proposed_id != match_id):
                        return failure("INVALID_MODEL_RESPONSE")
                    result = executor.execute_tool(call.function.name, call.function.arguments,
                                                   request=request, engine=engine, budget=budget)
                    if result.status == "success":
                        evidence.append(result.evidence)
                    else:
                        tool_errors.append(result.error)
                        if result.error.code in _FATAL_TOOL_ERRORS:
                            return failure(result.error.code)
                    messages.append(OllamaMessage(role="tool", tool_name=call.function.name,
                        tool_call_id=call.id, content=tool_result_content(result)))
                continue

            resolve_match_context(request, engine=engine)  # Recheck after possibly long inference.
            budget.check_deadline()
            # Free model content (including empty content) is never returned or
            # parsed as facts, evidence, clarification, or authorization decisions.
            response = build_response(evidence, tool_errors, metadata(),
                                      unsupported_metrics=unsupported_metrics)
            budget.check_deadline()
            if response is None:
                return failure("INVALID_MODEL_RESPONSE")
            response.metadata = metadata()
            return response
    except HTTPException as exc:
        return failure(_AUTH_ERRORS.get(exc.status_code, "INTERNAL_ERROR"))
    except ExecutionPolicyError as exc:
        return failure(exc.code)
    except OllamaClientError as exc:
        if exc.code == "TIMEOUT":
            return failure("OLLAMA_TIMEOUT")
        if exc.code == "DEADLINE_EXCEEDED":
            return failure("DEADLINE_EXCEEDED")
        if exc.code in {"INVALID_RESPONSE", "RESPONSE_TOO_LARGE"}:
            return failure("INVALID_MODEL_RESPONSE")
        return failure("OLLAMA_UNAVAILABLE")
    except Exception:
        return failure("INTERNAL_ERROR")
