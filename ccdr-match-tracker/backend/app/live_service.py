"""Authoritative live clock, transitions, events and derived score."""
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.enums import EventTeam, EventType, MatchStatus
from app.live_schemas import EventCreate, EventRead, EventUpdate, LiveState, Score
from app.models import Match, MatchEvent, MatchSquad, Player
from app.schemas import MatchRead, PlayerRead

RUNNING = {MatchStatus.FIRST_HALF, MatchStatus.SECOND_HALF}
NEXT = {
    MatchStatus.SCHEDULED: MatchStatus.FIRST_HALF,
    MatchStatus.FIRST_HALF: MatchStatus.HALF_TIME,
    MatchStatus.HALF_TIME: MatchStatus.SECOND_HALF,
    MatchStatus.SECOND_HALF: MatchStatus.FINISHED,
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def elapsed(match: Match, now: datetime) -> int:
    seconds = match.elapsed_seconds
    if match.status in RUNNING:
        if match.clock_started_at is None:
            raise HTTPException(409, "Relógio inconsistente: falta o início da parte.")
        seconds += max(0, int((now - match.clock_started_at).total_seconds()))
    return seconds


def period(match: Match) -> int | None:
    if match.status in {MatchStatus.FIRST_HALF, MatchStatus.HALF_TIME}:
        return 1
    if match.status in {MatchStatus.SECOND_HALF, MatchStatus.FINISHED}:
        return 2
    return None


def transition(match: Match, target: str, now: datetime) -> None:
    if NEXT.get(match.status) != target:
        raise HTTPException(409, "Transição inválida para o estado atual do jogo.")
    match.elapsed_seconds = elapsed(match, now)
    match.status = MatchStatus(target)
    match.clock_started_at = now if match.status in RUNNING else None


def events(db: Session, match_id: int) -> list[MatchEvent]:
    return list(db.scalars(select(MatchEvent).where(MatchEvent.match_id == match_id)
                          .order_by(MatchEvent.period, MatchEvent.elapsed_seconds, MatchEvent.id)))


def score(rows: list[MatchEvent]) -> Score:
    result = Score()
    for row in rows:
        if row.event_type not in {EventType.GOAL, EventType.OWN_GOAL}:
            continue
        credits_us = (row.team == EventTeam.US) == (row.event_type == EventType.GOAL)
        if credits_us:
            result.us += 1
        else:
            result.opponent += 1
    return result


def state(db: Session, match: Match) -> LiveState:
    now = utcnow()
    rows = events(db, match.id)
    selected = db.scalars(select(Player).join(MatchSquad, MatchSquad.player_id == Player.id)
                         .where(MatchSquad.match_id == match.id).order_by(Player.shirt_number, Player.id))
    return LiveState(match=MatchRead.model_validate(match), score=score(rows), server_now=now,
                     clock_elapsed_seconds=elapsed(match, now), period=period(match),
                     events=[EventRead.model_validate(row) for row in rows],
                     squad=[PlayerRead.model_validate(player) for player in selected])


def validate_event(db: Session, match: Match, data: EventCreate) -> None:
    if data.team == EventTeam.OPPONENT:
        if data.player_id is not None or data.related_player_id is not None:
            raise HTTPException(409, "Eventos do adversário não podem associar jogadores do nosso plantel.")
        return
    if data.event_type == EventType.GOAL and data.player_id is None:
        raise HTTPException(409, "Escolha o marcador do golo.")
    if data.event_type == EventType.SUBSTITUTION and (data.player_id is None or data.related_player_id is None):
        raise HTTPException(409, "Escolha o jogador que sai e o que entra.")
    if data.related_player_id is not None and data.event_type not in {EventType.GOAL, EventType.SUBSTITUTION}:
        raise HTTPException(409, "O segundo jogador só é permitido em golos ou substituições.")
    if data.player_id is not None and data.player_id == data.related_player_id:
        raise HTTPException(409, "Os dois jogadores devem ser diferentes.")
    for player_id in {data.player_id, data.related_player_id} - {None}:
        player = db.get(Player, player_id)
        if player is None:
            raise HTTPException(404, "Jogador não encontrado.")
        if player.team_id != match.team_id or player.season_id != match.season_id:
            raise HTTPException(409, "O jogador não pertence à equipa e época do jogo.")
        if db.scalar(select(MatchSquad.id).where(MatchSquad.match_id == match.id, MatchSquad.player_id == player_id)) is None:
            raise HTTPException(409, "O jogador não faz parte da convocatória do jogo.")
    # Future on-field/substitution rules can be added here, separately from membership.


def create_event(db: Session, match: Match, data: EventCreate) -> MatchEvent:
    if match.status not in RUNNING:
        raise HTTPException(409, "Só pode registar acontecimentos durante uma parte em curso.")
    validate_event(db, match, data)
    row = MatchEvent(match_id=match.id, **data.model_dump(), period=period(match), elapsed_seconds=elapsed(match, utcnow()))
    db.add(row)
    return row


def get_event(db: Session, match_id: int, event_id: int) -> MatchEvent:
    row = db.scalar(select(MatchEvent).where(MatchEvent.id == event_id, MatchEvent.match_id == match_id))
    if row is None:
        raise HTTPException(404, "Evento não encontrado neste jogo.")
    return row


def update_event(db: Session, match: Match, event_id: int, changes: EventUpdate) -> None:
    row = get_event(db, match.id, event_id)
    fields = {key: getattr(row, key) for key in EventCreate.model_fields}
    fields.update(changes.model_dump(exclude_unset=True))
    data = EventCreate(**fields)
    validate_event(db, match, data)
    for key, value in data.model_dump().items():
        setattr(row, key, value)


def protect_event_players(db: Session, match: Match, desired: set[int]) -> None:
    """A squad edit must not invalidate existing event references."""
    removed = select(MatchSquad.player_id).where(MatchSquad.match_id == match.id, MatchSquad.player_id.not_in(desired))
    used = db.scalar(select(MatchEvent.id).where(MatchEvent.match_id == match.id,
        or_(MatchEvent.player_id.in_(removed), MatchEvent.related_player_id.in_(removed))).limit(1))
    if used is not None:
        raise HTTPException(409, "Não pode retirar convocados associados a eventos. Corrija esses eventos primeiro.")
