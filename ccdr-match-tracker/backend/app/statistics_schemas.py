from typing import Literal

from pydantic import BaseModel, Field

from app.live_schemas import EventRead, Score
from app.schemas import MatchRead, PlayerRead, RosterContext


class EventTotals(BaseModel):
    goals: int = 0
    shots_on_target: int = 0
    shots_off_target: int = 0
    shots_blocked: int = 0
    shots_total: int = 0
    corners: int = 0
    free_kicks: int = 0
    fouls: int = 0
    offsides: int = 0
    penalties: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    saves: int = 0


class Comparison(BaseModel):
    us: EventTotals = Field(default_factory=EventTotals)
    opponent: EventTotals = Field(default_factory=EventTotals)


class MatchStatistics(BaseModel):
    match: MatchRead
    team_name: str
    score: Score
    is_final: bool
    total_events: int
    comparison: Comparison
    timeline: list[EventRead]
    players: list[PlayerRead]


class PlayerStatistics(BaseModel):
    player: PlayerRead
    matches_called_up: int = 0
    matches_started: int = 0
    goals: int = 0
    assists: int = 0
    shots_on_target: int = 0
    shots_off_target: int = 0
    shots_blocked: int = 0
    shots_total: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    fouls: int = 0
    offsides: int = 0


class RankingEntry(BaseModel):
    player_id: int
    name: str
    value: int


class Rankings(BaseModel):
    goals: list[RankingEntry]
    assists: list[RankingEntry]
    shots_total: list[RankingEntry]
    yellow_cards: list[RankingEntry]
    red_cards: list[RankingEntry]


class CompetitiveSummary(BaseModel):
    matches: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0


class StatisticsScope(BaseModel):
    competitive: Literal["FINISHED"] = "FINISHED"
    events: Literal["ALL_MATCHES_WITH_EVENTS"] = "ALL_MATCHES_WITH_EVENTS"
    callups: Literal["ALL_MATCHES_INCLUDING_SCHEDULED"] = "ALL_MATCHES_INCLUDING_SCHEDULED"


class PlayerStatisticsResponse(BaseModel):
    context: RosterContext
    scope: StatisticsScope = Field(default_factory=StatisticsScope)
    players: list[PlayerStatistics]
    rankings: Rankings


class SeasonStatistics(PlayerStatisticsResponse):
    total_matches: int
    matches_with_events: int
    total_events: int
    competitive: CompetitiveSummary
    comparison: Comparison
