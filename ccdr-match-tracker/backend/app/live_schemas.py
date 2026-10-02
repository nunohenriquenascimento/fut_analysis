from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.enums import EventTeam, EventType
from app.schemas import InputModel, MatchRead, PlayerRead

EventPlayerId = Annotated[int, Field(strict=True, gt=0, le=2147483647)]
Notes = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]


class Transition(InputModel):
    status: Literal["FIRST_HALF", "HALF_TIME", "SECOND_HALF", "FINISHED"]


class EventCreate(InputModel):
    event_type: EventType
    team: EventTeam
    player_id: EventPlayerId | None = None
    related_player_id: EventPlayerId | None = None
    notes: Notes | None = None


class EventUpdate(InputModel):
    event_type: EventType | None = None
    team: EventTeam | None = None
    player_id: EventPlayerId | None = None
    related_player_id: EventPlayerId | None = None
    notes: Notes | None = None

    @model_validator(mode="after")
    def valid_changes(self):
        if not self.model_fields_set:
            raise ValueError("Indique pelo menos um campo para atualizar.")
        if any(getattr(self, key) is None for key in self.model_fields_set & {"event_type", "team"}):
            raise ValueError("Tipo de evento e equipa não podem ser nulos.")
        return self


class EventRead(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    match_id: int
    period: int
    elapsed_seconds: int
    created_at: datetime
    recorded_by_id: int | None = None


class Score(BaseModel):
    us: int = 0
    opponent: int = 0


class MatchDetailRead(MatchRead):
    score: Score


class LiveState(BaseModel):
    match: MatchRead
    score: Score
    server_now: datetime
    clock_elapsed_seconds: int
    period: int | None
    events: list[EventRead]
    squad: list[PlayerRead]
