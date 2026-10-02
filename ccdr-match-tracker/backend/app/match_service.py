"""Match and squad rules, shared by the HTTP endpoints."""
from fastapi import HTTPException
from sqlalchemy import exists, func, or_, select, text
from sqlalchemy.orm import Session

from app.models import Match, MatchEvent, MatchSquad, Player, Team
from app.enums import MatchStatus
from app.schemas import PlayerRead, SquadEntry, SquadPlayer


def get_match(db: Session, match_id: int, *, lock: bool = False) -> Match:
    query = select(Match).where(Match.id == match_id)
    if lock:
        query = query.with_for_update(of=Match)
    match = db.scalar(query)
    if match is None:
        raise HTTPException(404, "Jogo não encontrado.")
    return match


def deletable(db: Session, match: Match) -> bool:
    """Current stored history only; never cascade historical records."""
    if match.status != MatchStatus.SCHEDULED or match.elapsed_seconds != 0 or match.clock_started_at is not None:
        return False
    return not db.scalar(select(exists().where(MatchSquad.match_id == match.id))) and not db.scalar(
        select(exists().where(MatchEvent.match_id == match.id)))


def cancel_match(match: Match) -> None:
    # Import here because Live also uses get_match from this module.
    from app import live_service as live
    if match.status == MatchStatus.CANCELLED:
        raise HTTPException(409, "O jogo já está cancelado.")
    match.elapsed_seconds = live.elapsed(match, live.utcnow())
    match.clock_started_at = None
    match.status = MatchStatus.CANCELLED


def resolve_opponent(db: Session, name: str, team_id: int) -> Team:
    name = " ".join(name.split())
    # Serialize name-based creation, including requests for different games.
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(lower(:name)))"), {"name": name})
    normalized = func.lower(func.regexp_replace(func.btrim(Team.name), r"\s+", " ", "g"))
    team = db.scalar(select(Team).where(normalized == func.lower(name)).order_by(Team.id))
    if team is not None and team.id == team_id:
        raise HTTPException(409, "A equipa não pode jogar contra si própria.")
    if team is None:
        team = Team(name=name)
        db.add(team)
        db.flush()
    return team


def read_squad(db: Session, match: Match) -> list[SquadPlayer]:
    selected = {row.player_id: row.is_starter for row in db.scalars(
        select(MatchSquad).where(MatchSquad.match_id == match.id)
    )}
    players = db.scalars(select(Player).where(or_(
        (Player.team_id == match.team_id) & (Player.season_id == match.season_id) & Player.is_active,
        Player.id.in_(selected),
    )).order_by(Player.shirt_number.asc().nulls_last(), Player.name, Player.id))
    return [SquadPlayer(player=PlayerRead.model_validate(player), role=(
        "TITULAR" if selected[player.id] else "SUPLENTE"
    ) if player.id in selected else "NAO_CONVOCADO") for player in players]


def validate_squad(db: Session, match: Match, entries: list[SquadEntry], existing: dict[int, MatchSquad]) -> None:
    """All validations precede mutation. Future squad-size rules belong here."""
    ids = [entry.player_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise HTTPException(409, "Um jogador não pode aparecer duas vezes na convocatória.")
    # Lock in stable order, so deactivation cannot race with the active check.
    players = {player.id: player for player in db.scalars(
        select(Player).where(Player.id.in_(ids)).order_by(Player.id).with_for_update()
    )}
    for player_id in ids:
        player = players.get(player_id)
        if player is None:
            raise HTTPException(404, "Jogador não encontrado.")
        if player.team_id != match.team_id or player.season_id != match.season_id:
            raise HTTPException(409, "O jogador deve pertencer à equipa e época do jogo.")
        if not player.is_active and player_id not in existing:
            raise HTTPException(409, "Um jogador inativo não pode ser adicionado à convocatória.")


def replace_squad(db: Session, match: Match, entries: list[SquadEntry]) -> None:
    existing = {row.player_id: row for row in db.scalars(
        select(MatchSquad).where(MatchSquad.match_id == match.id)
    )}
    validate_squad(db, match, entries, existing)
    desired = {entry.player_id: entry.is_starter for entry in entries}
    for player_id, row in existing.items():
        if player_id not in desired:
            db.delete(row)
    for player_id, is_starter in desired.items():
        if player_id in existing:
            existing[player_id].is_starter = is_starter
        else:
            db.add(MatchSquad(match_id=match.id, player_id=player_id, is_starter=is_starter))
