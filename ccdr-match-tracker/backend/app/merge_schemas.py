from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.live_schemas import EventRead, Score
from app.schemas import InputModel, MatchRead, PlayerRead

MatchId = Annotated[int, Field(strict=True, gt=0, le=2147483647)]


class MergeSelection(InputModel):
    principal_id: MatchId
    continuation_id: MatchId
    final_status: Literal["FINISHED", "SECOND_HALF"] = "FINISHED"


class MergeExecute(MergeSelection):
    preview_token: str = Field(min_length=1, max_length=256)
    confirmation: Literal["UNIR JOGOS"]


class MergeSquad(BaseModel):
    id: int
    player: PlayerRead
    is_starter: bool


class MergeGame(BaseModel):
    match: MatchRead
    score: Score
    elapsed_seconds: int
    period: int | None
    event_count: int
    squad: list[MergeSquad]


class TransferEvent(BaseModel):
    original: EventRead
    new_period: Literal[2] = 2
    new_elapsed_seconds: int


class MergePreview(BaseModel):
    principal: MergeGame
    continuation: MergeGame
    final_status: Literal["FINISHED", "SECOND_HALF"]
    transfers: list[TransferEvent]
    continuation_only_players: list[MergeSquad]
    predicted_score: Score
    predicted_elapsed_seconds: int
    warnings: list[str]
    conflicts: list[str]
    can_merge: bool
    preview_token: str | None = None
