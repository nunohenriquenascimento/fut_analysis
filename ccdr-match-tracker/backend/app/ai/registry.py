"""The single, immutable registry used for both descriptions and dispatch."""
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from pydantic import BaseModel

from app.ai.schemas import MatchStatisticsEvidence, MatchStatisticsInput, ToolName
from app.ai.tools import get_match_statistics


@dataclass(frozen=True)
class ToolDefinition:
    arguments_schema: type[BaseModel]
    handler: Callable[..., MatchStatisticsEvidence]
    description: str = ""


TOOLS: Mapping[ToolName, ToolDefinition] = MappingProxyType({
    "get_match_statistics": ToolDefinition(
        arguments_schema=MatchStatisticsInput,
        handler=get_match_statistics,
        description=(
            "Consulta estatísticas registadas de um jogo, incluindo resultado, "
            "eventos e limitações dos dados."
        ),
    ),
})
