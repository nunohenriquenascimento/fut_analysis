from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.enums import MatchStatus, PlayerPosition
from app.media import AssetPath

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
PositiveId = Annotated[int, Field(gt=0)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlayerCreate(InputModel):
    name: Name
    season_id: PositiveId
    team_id: PositiveId
    position: PlayerPosition
    shirt_number: int = Field(ge=1, le=99, strict=True)
    photo_path: AssetPath | None = None


class PlayerRead(PlayerCreate):
    model_config = ConfigDict(from_attributes=True)
    # Preserve readability of legacy registrations without a shirt number.
    shirt_number: int | None
    id: int
    is_active: bool
    created_at: datetime


class PlayerUpdate(InputModel):
    name: Name | None = None
    shirt_number: int | None = Field(default=None, ge=1, le=99, strict=True)
    position: PlayerPosition | None = None
    is_active: bool | None = Field(default=None, strict=True)
    photo_path: AssetPath | None = None

    @model_validator(mode="after")
    def require_non_null_changes(self) -> "PlayerUpdate":
        if not self.model_fields_set:
            raise ValueError("Indique pelo menos um campo para atualizar.")
        if any(getattr(self, field) is None for field in self.model_fields_set - {"photo_path"}):
            raise ValueError("Os campos enviados não podem ser nulos.")
        return self


class RosterContext(BaseModel):
    season_id: int
    season_name: str
    team_id: int
    team_name: str
    team_crest_path: str | None = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    crest_path: str | None = None


class TeamMediaUpdate(InputModel):
    crest_path: AssetPath | None


TeamName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Matchday = Annotated[int, Field(strict=True, ge=1, le=2147483647)]
Venue = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class MatchCreate(InputModel):
    season_id: PositiveId
    team_id: PositiveId
    matchday: Matchday
    opponent_id: PositiveId | None = None
    opponent_name: TeamName | None = None
    kickoff_at: AwareDatetime
    is_home: bool = Field(default=True, strict=True)
    venue: Venue | None = None

    @model_validator(mode="after")
    def different_teams(self) -> "MatchCreate":
        if (self.opponent_id is None) == (self.opponent_name is None):
            raise ValueError("Indique o nome ou o ID do adversário, exclusivamente.")
        if self.team_id == self.opponent_id:
            raise ValueError("A equipa e o adversário devem ser diferentes.")
        return self


class MatchUpdate(InputModel):
    matchday: Matchday | None = None
    opponent_name: TeamName | None = None
    kickoff_at: AwareDatetime | None = None
    is_home: bool | None = Field(default=None, strict=True)
    venue: Venue | None = None

    @model_validator(mode="after")
    def valid_changes(self) -> "MatchUpdate":
        if not self.model_fields_set:
            raise ValueError("Indique pelo menos um campo para atualizar.")
        if any(getattr(self, field) is None for field in self.model_fields_set - {"venue"}):
            raise ValueError("Só o local pode ser nulo.")
        return self


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    season_id: int
    team_id: int
    opponent_id: int
    opponent_name: str
    team_crest_path: str | None = None
    opponent_crest_path: str | None = None
    matchday: int | None
    kickoff_at: datetime
    is_home: bool
    venue: str | None
    status: MatchStatus
    elapsed_seconds: int
    clock_started_at: datetime | None
    created_at: datetime


class SquadEntry(InputModel):
    player_id: Annotated[int, Field(strict=True, gt=0, le=2147483647)]
    is_starter: bool = Field(strict=True)


class ForceMatchDelete(InputModel):
    confirmation: Literal["ELIMINAR"]


class SquadReplace(InputModel):
    players: list[SquadEntry]


class SquadPlayer(BaseModel):
    player: PlayerRead
    role: Literal["TITULAR", "SUPLENTE", "NAO_CONVOCADO"]
