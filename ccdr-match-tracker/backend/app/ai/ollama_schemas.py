"""Native Ollama wire models, deliberately separate from execution permissions."""
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue

from app.ai.ollama_config import Thinking


class OllamaToolFunction(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True, hide_input_in_errors=True)
    name: str = Field(min_length=1)
    arguments: dict[str, JsonValue]
    index: int | None = Field(default=None, ge=0)


class OllamaToolCall(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True, hide_input_in_errors=True)
    function: OllamaToolFunction
    # Native calls may have no identifier. Never invent, reorder or deduplicate one.
    id: str | None = None
    index: int | None = Field(default=None, ge=0)
    type: Literal["function"] | None = None


class OllamaMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    thinking: str | None = None
    tool_calls: list[OllamaToolCall] | None = None
    tool_name: str | None = None
    tool_call_id: str | None = None


class OllamaResponseMessage(OllamaMessage):
    # Ignore protocol extensions, but never accept a generated system/user message.
    model_config = ConfigDict(extra="ignore", strict=True, hide_input_in_errors=True)
    role: Literal["assistant"]


class OllamaToolDescription(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    name: str = Field(min_length=1)
    description: str | None = None
    parameters: dict[str, JsonValue]


class OllamaToolDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    type: Literal["function"] = "function"
    function: OllamaToolDescription


class OllamaChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    model: str = Field(min_length=1)
    messages: list[OllamaMessage] = Field(min_length=1)
    tools: list[OllamaToolDefinition] | None = None
    stream: bool = False
    think: Thinking = None


class OllamaChatResponse(BaseModel):
    """A full response or one native NDJSON chunk; chunks are not aggregated."""

    model_config = ConfigDict(extra="ignore", strict=True, hide_input_in_errors=True)
    model: str = Field(min_length=1)
    message: OllamaResponseMessage
    done: bool
    created_at: AwareDatetime | None = Field(default=None, strict=False)
    done_reason: str | None = None
    total_duration: int | None = Field(default=None, ge=0)
    load_duration: int | None = Field(default=None, ge=0)
    prompt_eval_count: int | None = Field(default=None, ge=0)
    prompt_eval_cached_count: int | None = Field(default=None, ge=0)
    prompt_eval_duration: int | None = Field(default=None, ge=0)
    eval_count: int | None = Field(default=None, ge=0)
    eval_duration: int | None = Field(default=None, ge=0)
