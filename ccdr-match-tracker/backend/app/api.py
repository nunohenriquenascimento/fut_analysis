from app.auth import current_user, require_editor
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, Player, Season, Team
from app.schemas import MatchCreate, MatchRead, MatchUpdate, SquadReplace, SquadPlayer, PlayerCreate, PlayerRead, PlayerUpdate, RosterContext
from app.match_service import get_match, resolve_opponent, read_squad, replace_squad
from app.roster import CLUB_NAME, SEASON_NAME
from app.live_schemas import MatchDetailRead
from app.live_service import events, score, protect_event_players
from app.schemas import TeamRead, TeamMediaUpdate

router = APIRouter()
Database = Annotated[Session, Depends(get_db)]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]
SeasonFilter = Annotated[int | None, Query(gt=0)]
TeamFilter = Annotated[int | None, Query(gt=0)]


def require_references(db: Session, season_id: int, *team_ids: int) -> None:
    if db.get(Season, season_id) is None:
        raise HTTPException(404, "Época não encontrada.")
    for team_id in team_ids:
        if db.get(Team, team_id) is None:
            raise HTTPException(404, "Equipa não encontrada.")


def save(db: Session, record: Player | Match | Team) -> Player | Match | Team:
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if getattr(getattr(exc.orig, "diag", None), "constraint_name", None) == "uq_players_season_id":
            raise HTTPException(409, "Este número de camisola já está atribuído nesta equipa e época, mesmo que o jogador esteja inativo.") from None
        raise HTTPException(409, "Dados em conflito. Verifique as referências e o número da camisola.") from None
    db.refresh(record)
    return record


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Process liveness only; does not assert database readiness."""
    return {"status": "ok"}


@router.get("/players/context", response_model=RosterContext, tags=["players"], dependencies=[Depends(current_user)])
def roster_context(db: Database):
    season = db.scalar(select(Season).where(Season.name == SEASON_NAME))
    team = db.scalar(select(Team).where(Team.name == CLUB_NAME))
    if season is None or team is None:
        raise HTTPException(404, "Plantel não configurado. Execute python -m app.seed no backend.")
    return RosterContext(season_id=season.id, season_name=season.name, team_id=team.id, team_name=team.name, team_crest_path=team.crest_path)


@router.get("/teams", response_model=list[TeamRead], tags=["teams"], dependencies=[Depends(current_user)])
def list_teams(db: Database, limit: Limit = 100, offset: Offset = 0):
    return db.scalars(select(Team).order_by(Team.name, Team.id).limit(limit).offset(offset)).all()


@router.patch("/teams/{team_id}", response_model=TeamRead, tags=["teams"], dependencies=[Depends(require_editor)])
def update_team_media(team_id: int, payload: TeamMediaUpdate, db: Database):
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(404, "Equipa não encontrada.")
    team.crest_path = payload.crest_path
    return save(db, team)


@router.get("/players", response_model=list[PlayerRead], tags=["players"], dependencies=[Depends(current_user)])
def list_players(db: Database, season_id: SeasonFilter = None, team_id: TeamFilter = None,
                 limit: Limit = 100, offset: Offset = 0):
    statement = select(Player).order_by(Player.name, Player.id)
    if season_id is not None:
        statement = statement.where(Player.season_id == season_id)
    if team_id is not None:
        statement = statement.where(Player.team_id == team_id)
    return db.scalars(statement.limit(limit).offset(offset)).all()


@router.post("/players", response_model=PlayerRead, status_code=201, tags=["players"], dependencies=[Depends(require_editor)])
def create_player(payload: PlayerCreate, db: Database):
    require_references(db, payload.season_id, payload.team_id)
    return save(db, Player(**payload.model_dump()))


@router.patch("/players/{player_id}", response_model=PlayerRead, tags=["players"], dependencies=[Depends(require_editor)])
def update_player(player_id: int, payload: PlayerUpdate, db: Database):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(404, "Jogador não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(player, field, value)
    return save(db, player)


@router.get("/matches", response_model=list[MatchRead], tags=["matches"], dependencies=[Depends(current_user)])
def list_matches(db: Database, season_id: SeasonFilter = None, team_id: TeamFilter = None,
                 limit: Limit = 100, offset: Offset = 0):
    statement = select(Match).order_by(Match.kickoff_at.desc(), Match.id.desc())
    if season_id is not None:
        statement = statement.where(Match.season_id == season_id)
    if team_id is not None:
        statement = statement.where(Match.team_id == team_id)
    return db.scalars(statement.limit(limit).offset(offset)).all()


@router.post("/matches", response_model=MatchRead, status_code=201, tags=["matches"], dependencies=[Depends(require_editor)])
def create_match(payload: MatchCreate, db: Database):
    try:
        require_references(db, payload.season_id, payload.team_id)
        values = payload.model_dump(exclude={"opponent_name"})
        if payload.opponent_name is not None:
            values["opponent_id"] = resolve_opponent(db, payload.opponent_name, payload.team_id).id
        else:
            require_references(db, payload.season_id, payload.opponent_id)
        return save(db, Match(**values))
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Dados do jogo em conflito. Tente novamente.") from None
    except Exception:
        db.rollback()
        raise


@router.get("/matches/{match_id}", response_model=MatchDetailRead, tags=["matches"], dependencies=[Depends(current_user)])
def match_detail(match_id: int, db: Database):
    match = get_match(db, match_id, lock=True)
    return MatchDetailRead(**MatchRead.model_validate(match).model_dump(), score=score(events(db, match_id)))


@router.patch("/matches/{match_id}", response_model=MatchRead, tags=["matches"], dependencies=[Depends(require_editor)])
def update_match(match_id: int, payload: MatchUpdate, db: Database):
    try:
        match = get_match(db, match_id, lock=True)
        values = payload.model_dump(exclude_unset=True)
        if "opponent_name" in values:
            match.opponent = resolve_opponent(db, values.pop("opponent_name"), match.team_id)
        for field, value in values.items():
            setattr(match, field, value)
        return save(db, match)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Dados do jogo em conflito. Tente novamente.") from None
    except Exception:
        db.rollback()
        raise


@router.get("/matches/{match_id}/squad", response_model=list[SquadPlayer], tags=["matches"], dependencies=[Depends(current_user)])
def match_squad(match_id: int, db: Database):
    return read_squad(db, get_match(db, match_id))


@router.put("/matches/{match_id}/squad", response_model=list[SquadPlayer], tags=["matches"], dependencies=[Depends(require_editor)])
def put_match_squad(match_id: int, payload: SquadReplace, db: Database):
    try:
        match = get_match(db, match_id, lock=True)
        protect_event_players(db, match, {entry.player_id for entry in payload.players})
        replace_squad(db, match, payload.players)
        db.flush()
        result = read_squad(db, match)
        db.commit()
        return result
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Convocatória em conflito. Recarregue o jogo e tente novamente.") from None
    except Exception:
        db.rollback()
        raise
