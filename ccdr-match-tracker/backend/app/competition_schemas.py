from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, model_validator

from app.schemas import InputModel, Name, PositiveId


class Rules(InputModel):
    win: int = Field(default=3, ge=0, le=100, strict=True)
    draw: int = Field(default=1, ge=0, le=100, strict=True)
    loss: int = Field(default=0, ge=0, le=100, strict=True)
    tiebreakers: list[Literal["head_to_head_points", "head_to_head_goal_difference", "goal_difference", "goals_for", "wins"]] = Field(default_factory=list, max_length=5)

    @model_validator(mode="after")
    def distinct(self):
        if len(set(self.tiebreakers)) != len(self.tiebreakers):
            raise ValueError("Critérios repetidos.")
        return self


class CompetitionCreate(InputModel):
    name: Name
    season_id: PositiveId
    internal_team_id: PositiveId
    team_ids: list[PositiveId] = Field(min_length=2, max_length=64)
    rules: Rules = Field(default_factory=Rules)

    @model_validator(mode="after")
    def participants(self):
        if len(set(self.team_ids)) != len(self.team_ids) or self.internal_team_id not in self.team_ids:
            raise ValueError("Participantes repetidos ou equipa interna ausente.")
        return self


class TeamCreate(InputModel):
    name: Name


class ParticipantsSelection(InputModel):
    team_ids: list[PositiveId] = Field(min_length=2, max_length=64)
    expected_team_ids: list[PositiveId] = Field(min_length=2, max_length=64)

    @model_validator(mode="after")
    def unique_participants(self):
        if len(set(self.team_ids)) != len(self.team_ids) or len(set(self.expected_team_ids)) != len(self.expected_team_ids):
            raise ValueError("Participantes repetidos.")
        return self


class ParticipantsUpdate(ParticipantsSelection):
    confirmation: Literal["ALTERAR PARTICIPANTES"]


class FixtureInput(InputModel):
    external_key: Annotated[str, Field(min_length=1, max_length=120, pattern=r"\S")]
    matchday: int = Field(gt=0, le=1000, strict=True)
    home_team_id: PositiveId
    away_team_id: PositiveId
    kickoff_at: AwareDatetime | None = None
    venue: Annotated[str, Field(max_length=160)] | None = None
    internal_match_id: PositiveId | None = None
    home_goals: int | None = Field(default=None, ge=0, le=999, strict=True)
    away_goals: int | None = Field(default=None, ge=0, le=999, strict=True)
    source: Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]

    @model_validator(mode="after")
    def valid_result(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("Equipas têm de ser diferentes.")
        if (self.home_goals is None) != (self.away_goals is None):
            raise ValueError("Indique ambos os resultados ou nenhum.")
        if self.internal_match_id is not None and self.home_goals is not None:
            raise ValueError("Resultados internos são derivados exclusivamente dos eventos.")
        return self


class FixtureImport(InputModel):
    fixtures: list[FixtureInput] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def unique_keys(self):
        keys = [row.external_key for row in self.fixtures]
        if len(set(keys)) != len(keys):
            raise ValueError("Chaves externas repetidas no lote.")
        return self
