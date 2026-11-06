"""Ollama transport contracts: simulated HTTP only, no Ollama server or database."""
import json
import os
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from app.ai.catalog import get_tool_catalog
from app.ai.ollama_client import OllamaClient, OllamaClientError
from app.ai.ollama_config import OllamaSettings
from app.ai.ollama_schemas import OllamaChatResponse
from app.ai.policy import ExecutionBudget, ExecutionPolicy

MESSAGES = [{"role": "user", "content": "Analisa os dados disponíveis."}]


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in list(os.environ):
        if name.startswith("OLLAMA_"):
            monkeypatch.delenv(name)


def reply(**overrides):
    return {"model": "qwen3:8b", "created_at": "2026-11-06T15:00:00Z",
            "message": {"role": "assistant", "content": "Análise disponível."},
            "done": True, "done_reason": "stop", **overrides}


def client_for(handler, **settings):
    return OllamaClient(OllamaSettings(_env_file=None, **settings), transport=httpx.MockTransport(handler))


class Chunks(httpx.SyncByteStream):
    def __init__(self, *chunks):
        self.chunks = chunks
        self.closed = False
        self.reads = 0

    def __iter__(self):
        for chunk in self.chunks:
            self.reads += 1
            yield chunk

    def close(self):
        self.closed = True


def test_plain_request_has_configured_model_and_real_httpx_timeouts():
    requests = []

    def handler(request):
        requests.append(request)
        assert request.method == "POST" and str(request.url) == "http://localhost:11434/api/chat"
        assert json.loads(request.content) == {
            "model": "installed-model:custom", "messages": MESSAGES, "stream": False, "think": False,
        }
        assert request.extensions["timeout"] == {"connect": 5.0, "read": 12.0, "write": 5.0, "pool": 5.0}
        return httpx.Response(200, json=reply(model="installed-model:custom"))

    with client_for(handler, model="installed-model:custom", timeout_seconds=12) as client:
        response = client.chat(MESSAGES)
    assert isinstance(response, OllamaChatResponse)
    assert response.message.content == "Análise disponível." and response.done
    assert response.created_at.utcoffset().total_seconds() == 0
    assert len(requests) == 1


def test_catalog_is_sent_unchanged_and_all_message_roles_are_supported():
    catalog = get_tool_catalog()
    calls = [
        {"id": "call-z", "index": 2, "type": "function", "function": {
            "index": 2, "name": "get_match_statistics", "arguments": {"match_id": 7}}},
        {"id": "call-a", "index": 0, "function": {
            "index": 0, "name": "unknown_proposal", "arguments": {"permissions": ["*"], "match_id": True}}},
    ]
    history = [{"role": "system", "content": "Usa apenas os dados fornecidos."}, *MESSAGES,
               {"role": "assistant", "thinking": "Texto de protocolo.", "tool_calls": calls},
               {"role": "tool", "tool_name": "get_match_statistics", "tool_call_id": "call-z", "content": "{}"}]

    def handler(request):
        payload = json.loads(request.content)
        assert payload["tools"] == catalog
        assert payload["messages"] == history
        assert payload["think"] is True
        return httpx.Response(200, json=reply(message={"role": "assistant", "content": "", "tool_calls": calls}))

    with client_for(handler) as client:
        response = client.chat(history, tools=catalog, think=True)
    parsed = response.message.tool_calls
    assert [call.id for call in parsed] == ["call-z", "call-a"]
    assert [call.function.index for call in parsed] == [2, 0]
    assert [call.index for call in parsed] == [2, 0]
    assert parsed[1].function.name == "unknown_proposal"
    assert parsed[1].function.arguments == {"permissions": ["*"], "match_id": True}


def test_native_calls_without_ids_remain_without_ids_and_never_execute(monkeypatch):
    from app.ai import executor, tools

    def forbidden(*args, **kwargs):
        pytest.fail("The HTTP client must never execute a tool")

    monkeypatch.setattr(executor, "execute_tool", forbidden)
    monkeypatch.setattr(tools, "get_match_statistics", forbidden)
    call = {"function": {"name": "__import__('os').system", "arguments": {"command": "proposal only"}}}
    with client_for(lambda _: httpx.Response(200, json=reply(message={"role": "assistant", "tool_calls": [call]}))) as client:
        response = client.chat(MESSAGES)
    assert response.message.tool_calls[0].id is None
    assert response.message.model_dump(exclude_none=True) == {"role": "assistant", "tool_calls": [call]}


def test_unexpected_response_fields_are_ignored_not_forwarded():
    wire = reply(private_metadata="private-secret", message={
        "role": "assistant", "content": "Texto.", "private_field": "private-secret",
    })
    with client_for(lambda _: httpx.Response(200, json=wire)) as client:
        response = client.chat(MESSAGES)
    assert response.message.content == "Texto."
    assert "private-secret" not in response.model_dump_json()


@pytest.mark.parametrize("wire", [
    b"not JSON private-secret", b"", b"[]", b"null", b'{"model":"private-secret"}',
    json.dumps(reply(done="true")).encode(), json.dumps(reply(done=False)).encode(),
    json.dumps(reply(message={"role": "system", "content": "private-secret"})).encode(),
    json.dumps(reply(message={"role": "assistant", "content": 5})).encode(),
    json.dumps(reply(message={"role": "assistant", "tool_calls": [{"function": {
        "name": "tool", "arguments": "{\\\"match_id\\\":1}"}}]})).encode(),
    b'{"model":"test","message":{"role":"assistant"},"done":true,"value":NaN}',
    b"\xff",
])
def test_invalid_responses_are_sanitized_and_closed(wire):
    stream = Chunks(wire)
    with client_for(lambda _: httpx.Response(200, stream=stream)) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES)
    assert error.value.code == "INVALID_RESPONSE" and stream.closed
    assert "private-secret" not in str(error.value)


@pytest.mark.parametrize("status", [301, 307, 400, 401, 404, 429, 500, 503])
def test_http_errors_are_sanitized_not_retried_or_redirected(status):
    requests = []
    stream = Chunks(b'{"error":"private-secret"}')

    def handler(request):
        requests.append(request)
        return httpx.Response(status, headers={"Location": "http://private-secret.invalid"}, stream=stream)

    with client_for(handler) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES)
    assert error.value.code == "HTTP_ERROR" and error.value.status_code == status
    assert "private-secret" not in str(error.value)
    assert len(requests) == 1 and stream.closed and stream.reads == 0


@pytest.mark.parametrize("exception, code", [
    (httpx.ConnectTimeout, "TIMEOUT"), (httpx.ReadTimeout, "TIMEOUT"),
    (httpx.WriteTimeout, "TIMEOUT"), (httpx.PoolTimeout, "TIMEOUT"),
    (httpx.ConnectError, "UNAVAILABLE"), (httpx.ReadError, "UNAVAILABLE"),
])
def test_transport_timeouts_and_unavailability_are_sanitized(exception, code):
    calls = []

    def handler(request):
        calls.append(True)
        raise exception("private-secret URL or credentials", request=request)

    with client_for(handler) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES)
    assert error.value.code == code and "private-secret" not in str(error.value)
    assert error.value.__suppress_context__ and len(calls) == 1


def test_read_timeout_during_body_closes_response():
    class TimedOut(Chunks):
        def __iter__(self):
            yield b'{"model":'
            raise httpx.ReadTimeout("private-secret")

    stream = TimedOut()
    with client_for(lambda _: httpx.Response(200, stream=stream)) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES)
    assert error.value.code == "TIMEOUT" and stream.closed


def test_no_session_headers_cookies_proxy_or_netrc_credentials_are_forwarded(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://private-secret.invalid:9999")
    monkeypatch.setenv("NETRC", "/private-secret")
    requests = []

    def handler(request):
        requests.append(request)
        assert not {"cookie", "authorization", "x-csrf-token", "proxy-authorization"} & set(request.headers)
        return httpx.Response(200, json=reply(), headers={"Set-Cookie": "ccdr_session=private-secret; Path=/"})

    with client_for(handler) as client:
        client.chat(MESSAGES)
        client.chat(MESSAGES)  # A Set-Cookie from the first reply is not forwarded.
    assert len(requests) == 2


@pytest.mark.parametrize("messages, tools, stream, think", [
    ([], None, False, None), ([{"role": "unknown", "content": "x"}], None, False, None),
    ([{"role": "user", "content": "x", "cookie": "private-secret"}], None, False, None),
    (MESSAGES, [{"type": "python", "function": {}}], False, None),
    (MESSAGES, None, "true", None), (MESSAGES, None, False, 123),
])
def test_invalid_requests_do_not_reach_transport(messages, tools, stream, think):
    def forbidden(_):
        pytest.fail("Invalid requests must not be sent")

    with client_for(forbidden) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(messages, tools=tools, stream=stream, think=think)
    assert error.value.code == "INVALID_REQUEST"
    assert "private-secret" not in str(error.value)


@pytest.mark.parametrize("settings", [
    {"base_url": "ftp://localhost"}, {"base_url": "localhost:11434"},
    {"base_url": "http://user:private-secret@localhost"}, {"base_url": "http://localhost/api/chat"},
    {"base_url": "http://localhost?"}, {"base_url": "http://localhost#"},
    {"base_url": "http://localhost:70000"}, {"base_url": "http://local host"},
    {"model": ""}, {"model": "model\nprivate-secret"}, {"timeout_seconds": 0},
    {"timeout_seconds": float("inf")}, {"timeout_seconds": True}, {"connect_timeout_seconds": -1},
    {"max_response_bytes": 0}, {"max_response_bytes": True}, {"think": 123}, {"think": " "},
])
def test_invalid_configuration_is_rejected_without_showing_values(settings):
    with pytest.raises(ValidationError) as error:
        OllamaSettings(_env_file=None, **settings)
    assert "private-secret" not in str(error.value)


def test_configuration_is_isolated_environment_driven_and_model_is_not_assumed_installed(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://ollama.example.test/")
    monkeypatch.setenv("OLLAMA_MODEL", "my-installed-model:latest")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "25")
    monkeypatch.setenv("OLLAMA_THINK", "false")
    monkeypatch.setenv("OLLAMA_MAX_RESPONSE_BYTES", "2048")
    settings = OllamaSettings(_env_file=None)
    assert settings.base_url == "https://ollama.example.test"
    assert settings.model == "my-installed-model:latest" and settings.timeout_seconds == 25
    assert settings.think is False and settings.max_response_bytes == 2048
    with pytest.raises(ValidationError):
        settings.model = "other"


@pytest.mark.parametrize("value, expected", [("true", True), ("false", False), ("low", "low")])
def test_thinking_environment_boolean_or_model_defined_mode(monkeypatch, value, expected):
    monkeypatch.setenv("OLLAMA_THINK", value)
    settings = OllamaSettings(_env_file=None)
    assert settings.think == expected
    with client_for(lambda request: httpx.Response(200, json=reply()), think=expected) as client:
        client.chat(MESSAGES)


def test_client_sanitizes_invalid_environment_configuration(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://user:private-secret@localhost")
    with pytest.raises(OllamaClientError) as error:
        OllamaClient(transport=httpx.MockTransport(lambda _: pytest.fail("No network expected")))
    assert error.value.code == "INVALID_CONFIG" and "private-secret" not in str(error.value)


@pytest.mark.parametrize("declared_length", [None, "100000"])
def test_response_byte_limit_with_or_without_content_length(declared_length):
    stream = Chunks(b"x" * 20, b"x" * 20)
    headers = {} if declared_length is None else {"Content-Length": declared_length}
    with client_for(lambda _: httpx.Response(200, headers=headers, stream=stream), max_response_bytes=30) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES)
    assert error.value.code == "RESPONSE_TOO_LARGE" and stream.closed
    if declared_length:
        assert stream.reads == 0


def test_exact_response_size_boundary():
    wire = json.dumps(reply(), ensure_ascii=False).encode()
    with client_for(lambda _: httpx.Response(200, content=wire), max_response_bytes=len(wire)) as client:
        assert client.chat(MESSAGES).done


def test_ndjson_stream_preserves_chunk_order_thinking_calls_and_split_utf8():
    call = {"id": "call-1", "function": {"index": 0, "name": "get_match_statistics", "arguments": {"match_id": 1}}}
    wires = [reply(done=False, message={"role": "assistant", "thinking": "Contexto."}),
             reply(done=False, message={"role": "assistant", "content": "Olá", "tool_calls": [call]}),
             reply(message={"role": "assistant", "content": ""})]
    data = b"\n" + b"\r\n".join(json.dumps(wire, ensure_ascii=False).encode() for wire in wires)
    cut = data.index("á".encode()) + 1
    stream = Chunks(data[:cut], data[cut:cut + 1], data[cut + 1:])

    def handler(request):
        assert json.loads(request.content)["stream"] is True
        assert request.headers["accept"] == "application/x-ndjson"
        return httpx.Response(200, stream=stream)

    with client_for(handler) as client:
        chunks = list(client.chat(MESSAGES, stream=True, tools=get_tool_catalog()))
    assert len(chunks) == 3 and [chunk.done for chunk in chunks] == [False, False, True]
    assert chunks[0].message.thinking == "Contexto." and chunks[1].message.content == "Olá"
    assert chunks[1].message.tool_calls[0].model_dump(exclude_none=True) == call
    assert stream.closed


@pytest.mark.parametrize("tail, code", [(b'{"error":"private-secret"}\n', "REMOTE_ERROR"),
                                       (b"invalid private-secret\n", "INVALID_RESPONSE"),
                                       (b"", "INVALID_RESPONSE")])
def test_stream_error_or_truncation_is_detected_after_partial_response(tail, code):
    partial = json.dumps(reply(done=False)).encode() + b"\n"
    stream = Chunks(partial, tail)
    with client_for(lambda _: httpx.Response(200, stream=stream)) as client:
        iterator = client.chat(MESSAGES, stream=True)
        assert next(iterator).done is False
        with pytest.raises(OllamaClientError) as error:
            next(iterator)
    assert error.value.code == code and "private-secret" not in str(error.value) and stream.closed


def test_streaming_size_is_cumulative_across_chunks_and_closing_early_releases_response():
    partial = json.dumps(reply(done=False)).encode() + b"\n"
    stream = Chunks(partial, partial)
    with client_for(lambda _: httpx.Response(200, stream=stream), max_response_bytes=len(partial) + 1) as client:
        iterator = client.chat(MESSAGES, stream=True)
        next(iterator)
        with pytest.raises(OllamaClientError) as error:
            next(iterator)
    assert error.value.code == "RESPONSE_TOO_LARGE" and stream.closed
    early = Chunks(partial, partial)
    with client_for(lambda _: httpx.Response(200, stream=early)) as client:
        iterator = client.chat(MESSAGES, stream=True)
        next(iterator)
        iterator.close()
        assert early.closed and early.reads == 1


def test_remote_error_and_compressed_body_are_controlled():
    for wire, headers, code in [(b'{"error":"private-secret"}', {}, "REMOTE_ERROR"),
                                (b"compressed", {"Content-Encoding": "gzip"}, "INVALID_RESPONSE")]:
        with client_for(lambda _: httpx.Response(200, stream=Chunks(wire), headers=headers)) as client:
            with pytest.raises(OllamaClientError) as error:
                client.chat(MESSAGES)
        assert error.value.code == code and "private-secret" not in str(error.value)


def test_budget_caps_transport_timeouts_without_consuming_tool_calls_or_rounds():
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(ExecutionPolicy(timeout_seconds=10.0), clock=lambda: clock.now)
    clock.now = 7.0

    def handler(request):
        assert request.extensions["timeout"] == {"connect": 3.0, "read": 3.0, "write": 3.0, "pool": 3.0}
        return httpx.Response(200, json=reply())

    with client_for(handler) as client:
        assert client.chat(MESSAGES, budget=budget).done
    assert budget.remaining_seconds() == 3.0 and budget.calls_used == budget.rounds_used == 0


def test_expired_budget_does_not_contact_transport():
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(ExecutionPolicy(timeout_seconds=1.0), clock=lambda: clock.now)
    clock.now = 1.0
    with client_for(lambda _: pytest.fail("Expired budget must not send HTTP")) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES, budget=budget)
    assert error.value.code == "DEADLINE_EXCEEDED"


def test_deadline_after_http_headers_closes_response_before_body():
    clock = SimpleNamespace(now=0.0)
    budget = ExecutionBudget(ExecutionPolicy(timeout_seconds=1.0), clock=lambda: clock.now)
    stream = Chunks(json.dumps(reply()).encode())

    def handler(_):
        clock.now = 1.0
        return httpx.Response(200, stream=stream)

    with client_for(handler) as client:
        with pytest.raises(OllamaClientError) as error:
            client.chat(MESSAGES, budget=budget)
    assert error.value.code == "DEADLINE_EXCEEDED" and stream.closed and stream.reads == 0
