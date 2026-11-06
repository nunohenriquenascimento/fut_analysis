"""Bounded native Ollama HTTP transport. No tools, auth sessions or DB access."""
from collections.abc import Iterator
from contextlib import contextmanager
import json
from typing import Any, Literal, overload

import httpx
from pydantic import ValidationError

from app.ai.ollama_config import OllamaSettings, Thinking
from app.ai.ollama_schemas import (
    OllamaChatRequest, OllamaChatResponse, OllamaMessage, OllamaToolDefinition,
)
from app.ai.policy import ExecutionBudget, ExecutionPolicyError

OllamaErrorCode = Literal[
    "INVALID_CONFIG", "INVALID_REQUEST", "TIMEOUT", "UNAVAILABLE", "HTTP_ERROR",
    "INVALID_RESPONSE", "RESPONSE_TOO_LARGE", "REMOTE_ERROR", "DEADLINE_EXCEEDED",
]
_ERRORS: dict[OllamaErrorCode, str] = {
    "INVALID_CONFIG": "Configuração do Ollama inválida.",
    "INVALID_REQUEST": "Pedido ao Ollama inválido.",
    "TIMEOUT": "O Ollama excedeu o tempo de espera.",
    "UNAVAILABLE": "Ollama indisponível.",
    "HTTP_ERROR": "O Ollama recusou o pedido.",
    "INVALID_RESPONSE": "Resposta do Ollama inválida ou incompleta.",
    "RESPONSE_TOO_LARGE": "A resposta do Ollama excede o tamanho permitido.",
    "REMOTE_ERROR": "O Ollama não conseguiu concluir a resposta.",
    "DEADLINE_EXCEEDED": "Prazo de execução excedido.",
}


class OllamaClientError(Exception):
    def __init__(self, code: OllamaErrorCode, *, status_code: int | None = None):
        self.code = code
        self.status_code = status_code
        super().__init__(_ERRORS[code])


class OllamaClient:
    """A reusable, explicitly closed client with injectable HTTPX transport.

    Streaming yields validated native chunks, preserving call order and optional
    IDs/indices. It does not merge calls, execute them or build conversation state.
    HTTP timeouts bound connect/read/write/pool waits, not total wall-clock time.
    A supplied budget caps those waits at its current remaining time and checks
    the deadline at I/O boundaries; it cannot forcibly cancel synchronous work.
    """

    def __init__(self, settings: OllamaSettings | None = None, *, transport: httpx.BaseTransport | None = None):
        try:
            if settings is not None and not isinstance(settings, OllamaSettings):
                raise ValueError("Invalid settings type")
            self.settings = settings if settings is not None else OllamaSettings()
        except (ValidationError, ValueError):
            raise OllamaClientError("INVALID_CONFIG") from None
        self._client = httpx.Client(transport=transport, trust_env=False, follow_redirects=False)

    def __enter__(self) -> "OllamaClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @overload
    def chat(self, messages: list[OllamaMessage | dict[str, Any]], *,
             tools: list[OllamaToolDefinition | dict[str, Any]] | None = None,
             stream: Literal[False] = False, think: Thinking = None,
             budget: ExecutionBudget | None = None) -> OllamaChatResponse: ...

    @overload
    def chat(self, messages: list[OllamaMessage | dict[str, Any]], *,
             tools: list[OllamaToolDefinition | dict[str, Any]] | None = None,
             stream: Literal[True], think: Thinking = None,
             budget: ExecutionBudget | None = None) -> Iterator[OllamaChatResponse]: ...

    def chat(self, messages, *, tools=None, stream=False, think=None, budget=None):
        try:
            payload = OllamaChatRequest(
                model=self.settings.model, messages=messages, tools=tools, stream=stream,
                think=self.settings.think if think is None else think,
            ).model_dump(mode="json", exclude_none=True)
        except (ValidationError, ValueError, TypeError):
            raise OllamaClientError("INVALID_REQUEST") from None
        if budget is not None and not isinstance(budget, ExecutionBudget):
            raise OllamaClientError("INVALID_REQUEST")
        return self._stream(payload, budget) if stream else self._complete(payload, budget)

    def _remaining(self, budget: ExecutionBudget | None) -> float:
        try:
            return min(self.settings.timeout_seconds, budget.remaining_seconds()) if budget else self.settings.timeout_seconds
        except ExecutionPolicyError:
            raise OllamaClientError("DEADLINE_EXCEEDED") from None

    @contextmanager
    def _response(self, payload: dict, budget: ExecutionBudget | None):
        wait = self._remaining(budget)
        timeout = httpx.Timeout(wait, connect=min(wait, self.settings.connect_timeout_seconds),
                                write=min(wait, 5.0), pool=min(wait, 5.0))
        # Construct directly: never merge client cookies, auth or default headers.
        try:
            request = httpx.Request(
                "POST", self.settings.base_url + "/api/chat", json=payload,
                headers={"Accept": "application/x-ndjson" if payload["stream"] else "application/json",
                         "Accept-Encoding": "identity"},
                extensions={"timeout": timeout.as_dict()},
            )
        except (TypeError, ValueError):
            raise OllamaClientError("INVALID_REQUEST") from None
        response = None
        try:
            response = self._client.send(request, stream=True, auth=None, follow_redirects=False)
            self._remaining(budget)
            if not 200 <= response.status_code < 300:
                raise OllamaClientError("HTTP_ERROR", status_code=response.status_code)
            if response.headers.get("content-encoding", "identity").lower() != "identity":
                raise OllamaClientError("INVALID_RESPONSE")
            length = response.headers.get("content-length")
            if length is not None and int(length) > self.settings.max_response_bytes:
                raise OllamaClientError("RESPONSE_TOO_LARGE")
            yield response
        except httpx.TimeoutException:
            raise OllamaClientError("TIMEOUT") from None
        except httpx.RequestError:
            raise OllamaClientError("UNAVAILABLE") from None
        except (ValueError, UnicodeError, RecursionError, ValidationError):
            raise OllamaClientError("INVALID_RESPONSE") from None
        finally:
            if response is not None:
                response.close()

    def _chunks(self, response: httpx.Response, budget: ExecutionBudget | None) -> Iterator[bytes]:
        total = 0
        for chunk in response.iter_bytes():
            self._remaining(budget)
            total += len(chunk)
            if total > self.settings.max_response_bytes:
                raise OllamaClientError("RESPONSE_TOO_LARGE")
            yield chunk
        self._remaining(budget)

    @staticmethod
    def _parse(data: bytes) -> OllamaChatResponse:
        def invalid_constant(value):
            raise ValueError("Invalid JSON constant")

        decoded = json.loads(data.decode("utf-8"), parse_constant=invalid_constant)
        if isinstance(decoded, dict) and "error" in decoded:
            raise OllamaClientError("REMOTE_ERROR")
        return OllamaChatResponse.model_validate(decoded)

    def _complete(self, payload: dict, budget: ExecutionBudget | None) -> OllamaChatResponse:
        with self._response(payload, budget) as response:
            data = bytearray()
            for chunk in self._chunks(response, budget):
                data.extend(chunk)
            parsed = self._parse(bytes(data))
            self._remaining(budget)
            if not parsed.done:
                raise OllamaClientError("INVALID_RESPONSE")
            return parsed

    def _stream(self, payload: dict, budget: ExecutionBudget | None) -> Iterator[OllamaChatResponse]:
        # Closing this generator also closes the HTTP response on early consumer exit.
        with self._response(payload, budget) as response:
            pending = bytearray()
            for chunk in self._chunks(response, budget):
                pending.extend(chunk)
                while b"\n" in pending:
                    line, _, rest = pending.partition(b"\n")
                    pending = bytearray(rest)
                    if not line.strip():
                        continue
                    parsed = self._parse(bytes(line))
                    self._remaining(budget)
                    yield parsed
                    if parsed.done:
                        return
            if pending.strip():
                parsed = self._parse(bytes(pending))
                self._remaining(budget)
                yield parsed
                if parsed.done:
                    return
            raise OllamaClientError("INVALID_RESPONSE")
