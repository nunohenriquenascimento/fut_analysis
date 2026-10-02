"""Read-only statistics derived from matches, squads and current events."""
from collections import defaultdict
import unicodedata

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.enums import EventTeam, EventType, MatchStatus
from app.live_schemas import EventRead
from app.live_service import events, score
from app.match_service import get_match
from app.models import Match, MatchEvent, MatchSquad, Player, Season, Team
from app.roster import CLUB_NAME, SEASON_NAME
from app.schemas import MatchRead, PlayerRead, RosterContext
from app.statistics_schemas import (
    Comparison, CompetitiveSummary, MatchStatistics, PlayerStatistics,
    RankingEntry, Rankings, SeasonStatistics,
)

EVENT_FIELDS = {
    EventType.SHOT_ON_TARGET: "shots_on_target", EventType.SHOT_OFF_TARGET: "shots_off_target",
    EventType.SHOT_BLOCKED: "shots_blocked", EventType.CORNER: "corners",
    EventType.FREE_KICK: "free_kicks", EventType.FOUL: "fouls", EventType.OFFSIDE: "offsides",
    EventType.PENALTY: "penalties", EventType.YELLOW_CARD: "yellow_cards",
    EventType.RED_CARD: "red_cards", EventType.SAVE: "saves",
}
SHOTS = {EventType.SHOT_ON_TARGET, EventType.SHOT_OFF_TARGET, EventType.SHOT_BLOCKED}


def name_key(name: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", name.casefold()) if not unicodedata.combining(char))


def comparison(rows: list[MatchEvent]) -> Comparison:
    result = Comparison()
    goals = score(rows)  # Exactly the same own-goal rules as Live; no changes to Live.
    result.us.goals, result.opponent.goals = goals.us, goals.opponent
    for row in rows:
        side = result.us if row.team == EventTeam.US else result.opponent
        field = EVENT_FIELDS.get(row.event_type)
        if field:
            setattr(side, field, getattr(side, field) + 1)
        if row.event_type in SHOTS:
            side.shots_total += 1
    return result


def match_statistics(db: Session, match_id: int) -> MatchStatistics:
    match = get_match(db, match_id)
    rows = events(db, match_id)
    referenced = {value for row in rows for value in (row.player_id, row.related_player_id) if value is not None}
    players = db.scalars(select(Player).where(Player.id.in_(referenced)).order_by(Player.name, Player.id))
    return MatchStatistics(match=MatchRead.model_validate(match), team_name=db.get(Team, match.team_id).name,
        score=score(rows), is_final=match.status == MatchStatus.FINISHED, total_events=len(rows),
        comparison=comparison(rows), timeline=[EventRead.model_validate(row) for row in rows],
        players=[PlayerRead.model_validate(player) for player in players])


def context(db: Session) -> RosterContext:
    season = db.scalar(select(Season).where(Season.name == SEASON_NAME))
    team = db.scalar(select(Team).where(Team.name == CLUB_NAME))
    if season is None or team is None:
        raise HTTPException(404, "Época/equipa não configuradas. Execute python -m app.seed no backend.")
    return RosterContext(season_id=season.id, season_name=season.name, team_id=team.id, team_name=team.name, team_crest_path=team.crest_path)


def player_totals(db: Session, roster: RosterContext, match_ids, rows: list[MatchEvent]) -> list[PlayerStatistics]:
    players = db.scalars(select(Player).where(Player.season_id == roster.season_id, Player.team_id == roster.team_id))
    totals = {player.id: PlayerStatistics(player=PlayerRead.model_validate(player)) for player in players}
    # Count squads separately from events: joins must not multiply appearances.
    callups = db.execute(select(MatchSquad.player_id, func.count(), func.count().filter(MatchSquad.is_starter))
        .where(MatchSquad.match_id.in_(match_ids)).group_by(MatchSquad.player_id))
    for player_id, called, started in callups:
        if player_id in totals:
            totals[player_id].matches_called_up = called
            totals[player_id].matches_started = started
    for row in rows:
        if row.team != EventTeam.US:
            continue
        player = totals.get(row.player_id)
        if row.event_type == EventType.GOAL:
            if player:
                player.goals += 1
            assistant = totals.get(row.related_player_id)
            if assistant:
                assistant.assists += 1
        elif player:
            field = EVENT_FIELDS.get(row.event_type)
            if field in PlayerStatistics.model_fields:
                setattr(player, field, getattr(player, field) + 1)
            if row.event_type in SHOTS:
                player.shots_total += 1
    return sorted(totals.values(), key=lambda row: (name_key(row.player.name), row.player.name, row.player.id))


def rankings(players: list[PlayerStatistics]) -> Rankings:
    result = {}
    for metric in Rankings.model_fields:
        ordered = sorted((row for row in players if getattr(row, metric) > 0),
            key=lambda row: (-getattr(row, metric), name_key(row.player.name), row.player.name, row.player.id))
        result[metric] = [RankingEntry(player_id=row.player.id, name=row.player.name, value=getattr(row, metric)) for row in ordered]
    return Rankings(**result)


def season_statistics(db: Session) -> SeasonStatistics:
    roster = context(db)
    filters = (Match.season_id == roster.season_id, Match.team_id == roster.team_id)
    matches = list(db.scalars(select(Match).where(*filters)))
    match_ids = select(Match.id).where(*filters)
    rows = list(db.scalars(select(MatchEvent).where(MatchEvent.match_id.in_(match_ids))
        .order_by(MatchEvent.match_id, MatchEvent.period, MatchEvent.elapsed_seconds, MatchEvent.id)))
    by_match = defaultdict(list)
    for row in rows:
        by_match[row.match_id].append(row)
    competitive = CompetitiveSummary()
    for match in matches:
        if match.status != MatchStatus.FINISHED:
            continue
        result = score(by_match[match.id])
        competitive.matches += 1
        competitive.goals_for += result.us
        competitive.goals_against += result.opponent
        if result.us > result.opponent:
            competitive.wins += 1
        elif result.us == result.opponent:
            competitive.draws += 1
        else:
            competitive.losses += 1
    competitive.goal_difference = competitive.goals_for - competitive.goals_against
    players = player_totals(db, roster, match_ids, rows)
    return SeasonStatistics(context=roster, total_matches=len(matches), matches_with_events=len({row.match_id for row in rows}),
        total_events=len(rows), competitive=competitive, comparison=comparison(rows), players=players, rankings=rankings(players))
