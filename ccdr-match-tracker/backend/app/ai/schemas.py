"""Contracts for match evidence and the separate, server-owned access scope."""
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue

from app.statistics_schemas import MatchStatistics
from app.enums import MatchStatus

EntityId = Annotated[int, Field(strict=True, gt=0, le=2_147_483_647)]


class MatchStatisticsInput(BaseModel):
    """Untrusted tool arguments. Access scope and permissions are never arguments."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    match_id: EntityId


class AuthorizedMatchContext(BaseModel):
    """Created by trusted server code AFTER authorization, never from tool JSON.

    Existing roles are global: this object does not infer team membership or
    authenticate a user. Its creator must determine the permitted team/season.
    Even an administrator is restricted to this explicit scope by the tool.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    team_id: EntityId
    season_id: EntityId


class MatchEvidenceScope(BaseModel):
    match_id: EntityId
    team_id: EntityId
    season_id: EntityId
    events: Literal["ALL_RECORDED_MATCH_EVENTS"] = "ALL_RECORDED_MATCH_EVENTS"
    perspective: Literal["MATCH_TEAM"] = "MATCH_TEAM"


class EvidenceSource(BaseModel):
    """Internal record references, not a claim of external verification."""

    entity: Literal["matches", "match_events", "players", "teams"]
    record_ids: list[EntityId]


class DataLimitation(BaseModel):
    code: Literal[
        "UNVERIFIED_COVERAGE", "RECORDED_SHOTS_ONLY", "NO_PLAYER_MINUTES",
        "NO_EVENTS", "NON_FINAL_MATCH", "CANCELLED_MATCH",
    ]
    description: str


class MatchStatisticsEvidence(BaseModel):
    scope: MatchEvidenceScope
    statistics: MatchStatistics
    queried_at: AwareDatetime
    service: Literal["app.statistics_service.match_statistics"] = "app.statistics_service.match_statistics"
    sources: list[EvidenceSource]
    limitations: list[DataLimitation]


ToolName = Literal["get_match_statistics"]


class ToolExecutionRequest(BaseModel):
    """Untrusted proposal. Each registry entry supplies its argument schema."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    tool_name: ToolName
    arguments: dict[str, Any]


ToolErrorCode = Literal[
    "UNKNOWN_TOOL", "INVALID_ARGUMENTS", "UNAUTHENTICATED", "FORBIDDEN",
    "NOT_FOUND", "UNAVAILABLE", "INTERNAL_ERROR", "ARGUMENTS_TOO_LARGE",
    "EXECUTION_LIMIT_REACHED", "DEADLINE_EXCEEDED",
]


class ToolExecutionError(BaseModel):
    code: ToolErrorCode
    message: str


class ToolExecutionMetadata(BaseModel):
    execution_id: UUID
    started_at: AwareDatetime
    duration_ms: float = Field(ge=0, allow_inf_nan=False)


class ToolExecutionSuccess(BaseModel):
    status: Literal["success"] = "success"
    tool_name: ToolName
    evidence: MatchStatisticsEvidence
    metadata: ToolExecutionMetadata


class ToolExecutionFailure(BaseModel):
    status: Literal["error"] = "error"
    # Unknown/unvalidated names are not reflected back to callers.
    tool_name: ToolName | None = None
    error: ToolExecutionError
    metadata: ToolExecutionMetadata


ToolExecutionResult = Annotated[
    ToolExecutionSuccess | ToolExecutionFailure, Field(discriminator="status"),
]


class ToolCatalogFunction(BaseModel):
    """Public function description; parameters come from its registered schema."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    name: ToolName
    description: str = Field(min_length=1)
    parameters: dict[str, JsonValue]


class ToolCatalogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    type: Literal["function"] = "function"
    function: ToolCatalogFunction


class AgentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    question: Annotated[str, Field(min_length=1, max_length=4000)]


AgentErrorCode = Literal[
    "INVALID_QUESTION", "UNAUTHENTICATED", "FORBIDDEN", "UNAVAILABLE", "INTERNAL_ERROR",
    "EXECUTION_LIMIT_REACHED", "DEADLINE_EXCEEDED", "OLLAMA_TIMEOUT", "OLLAMA_UNAVAILABLE",
    "INVALID_MODEL_RESPONSE",
]


class AgentError(BaseModel):
    code: AgentErrorCode
    message: str


class AgentMetadata(BaseModel):
    execution_id: UUID
    started_at: AwareDatetime
    duration_ms: float = Field(ge=0, allow_inf_nan=False)
    rounds_used: int = Field(ge=0)
    calls_used: int = Field(ge=0)
    model_requests: int = Field(ge=0)


class VerifiedEvidenceScope(MatchEvidenceScope):
    model_config = ConfigDict(extra="forbid", frozen=True)


class VerifiedSource(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    entity: Literal["matches", "match_events", "players", "teams"]
    record_ids: tuple[EntityId, ...]


class VerifiedStatistic(BaseModel):
    """Faithful projection of recorded backend data, not real-world completeness."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    metric: Literal[
        "goals", "shots_on_target", "shots_off_target", "shots_blocked", "shots_total",
        "corners", "free_kicks", "fouls", "offsides", "penalties", "yellow_cards",
        "red_cards", "saves", "own_goals", "substitutions", "total_events",
    ]
    side: Literal["us", "opponent", "match"]
    value: int = Field(strict=True, ge=0)
    source_path: str
    event_ids: tuple[EntityId, ...] = ()


class VerifiedMatchFacts(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scope: VerifiedEvidenceScope
    queried_at: AwareDatetime
    service: Literal["app.statistics_service.match_statistics"]
    sources: tuple[VerifiedSource, ...]
    match_status: MatchStatus
    is_final: bool
    coverage: Literal["RECORDED_EVENTS_COMPLETENESS_UNKNOWN"] = "RECORDED_EVENTS_COMPLETENESS_UNKNOWN"
    result_basis: Literal["RECORDED_EVENTS", "NO_RECORDED_EVENTS"]
    statistics: tuple[VerifiedStatistic, ...]
    limitations: tuple[str, ...]


class AgentSuccess(BaseModel):
    status: Literal["success"] = "success"
    # Backend rendering only. A future interpretation belongs in a separate field/contract.
    answer: str = Field(min_length=1)
    facts: tuple[VerifiedMatchFacts, ...] = Field(min_length=1)
    evidence: list[MatchStatisticsEvidence] = Field(min_length=1)
    tool_errors: list[ToolExecutionError] = Field(default_factory=list)
    limitations: list[str]
    factual_validation: Literal["BACKEND_EVIDENCE_PROJECTION"] = "BACKEND_EVIDENCE_PROJECTION"
    metadata: AgentMetadata


class AgentClarification(BaseModel):
    status: Literal["clarification_required"] = "clarification_required"
    reason: Literal["MATCH_IDENTIFICATION_REQUIRED"] = "MATCH_IDENTIFICATION_REQUIRED"
    answer: Literal["Indique o identificador do jogo no formato «jogo 123». É necessário identificar exatamente um jogo."] = (
        "Indique o identificador do jogo no formato «jogo 123». É necessário identificar exatamente um jogo."
    )
    metadata: AgentMetadata


class AgentNoData(BaseModel):
    status: Literal["no_data"] = "no_data"
    reason: Literal["NOT_FOUND", "NO_EVENTS", "NO_EVIDENCE", "UNSUPPORTED_METRICS"]
    answer: str = Field(min_length=1)
    facts: tuple[VerifiedMatchFacts, ...] = ()
    evidence: list[MatchStatisticsEvidence] = Field(default_factory=list)
    tool_errors: list[ToolExecutionError] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    factual_validation: Literal["BACKEND_EVIDENCE_PROJECTION"] = "BACKEND_EVIDENCE_PROJECTION"
    metadata: AgentMetadata


class AgentFailure(BaseModel):
    status: Literal["error"] = "error"
    error: AgentError
    evidence: list[MatchStatisticsEvidence] = Field(default_factory=list)
    tool_errors: list[ToolExecutionError] = Field(default_factory=list)
    metadata: AgentMetadata


AgentResult = Annotated[
    AgentSuccess | AgentClarification | AgentNoData | AgentFailure, Field(discriminator="status"),
]
