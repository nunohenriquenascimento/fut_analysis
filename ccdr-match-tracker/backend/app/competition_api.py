from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import current_user, require_admin, require_editor
from app.competition_schemas import CompetitionCreate, FixtureImport, ParticipantsSelection, ParticipantsUpdate, Rules, TeamCreate
from app.competition_participants import participants_plan
from app.competition_service import calendar, get_competition, standings
from app.database import get_db
from app.models import Competition, CompetitionFixture, CompetitionTeam, Match, Season, Team
from app.match_service import find_team_by_name
from app.schemas import TeamRead

router = APIRouter(tags=["competitions"], dependencies=[Depends(current_user)])
Database = Annotated[Session, Depends(get_db)]


def commit(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Conflito de participantes, chaves externas ou jogos duplicados.") from None


def summary(item):
    return dict(id=item.id, season_id=item.season_id, internal_team_id=item.internal_team_id,
                name=item.name, rules=item.rules, provisional=True)


@router.post("/teams", response_model=TeamRead, status_code=201, dependencies=[Depends(require_editor)])
def create_team(payload: TeamCreate, db: Database):
    name = " ".join(payload.name.split())
    if find_team_by_name(db, name) is not None:
        raise HTTPException(409, "Já existe uma equipa com este nome.")
    row = Team(name=name)
    db.add(row)
    commit(db)
    db.refresh(row)
    return row


@router.post("/competitions", status_code=201, dependencies=[Depends(require_editor)])
def create_competition(payload: CompetitionCreate, db: Database):
    if db.get(Season, payload.season_id) is None:
        raise HTTPException(404, "Época não encontrada.")
    found = set(db.scalars(select(Team.id).where(Team.id.in_(payload.team_ids))))
    if found != set(payload.team_ids):
        raise HTTPException(404, "Equipa não encontrada.")
    row = Competition(name=payload.name, season_id=payload.season_id,
                      internal_team_id=payload.internal_team_id, rules=payload.rules.model_dump())
    db.add(row)
    try:
        db.flush()
        db.add_all([CompetitionTeam(competition_id=row.id, team_id=team_id) for team_id in payload.team_ids])
        commit(db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Competição já existente nesta época.") from None
    return summary(row)


@router.get("/competitions")
def list_competitions(db: Database, limit: Annotated[int, Query(ge=1, le=200)] = 100,
                      offset: Annotated[int, Query(ge=0)] = 0):
    return [summary(row) for row in db.scalars(select(Competition).order_by(Competition.id).limit(limit).offset(offset))]


@router.get("/competitions/{competition_id}/teams", response_model=list[TeamRead])
def participants(competition_id: int, db: Database):
    get_competition(db, competition_id)
    return db.scalars(select(Team).join(CompetitionTeam, CompetitionTeam.team_id == Team.id)
                      .where(CompetitionTeam.competition_id == competition_id).order_by(Team.name, Team.id)).all()


@router.put("/competitions/{competition_id}/rules", dependencies=[Depends(require_editor)])
def update_rules(competition_id: int, payload: Rules, db: Database):
    row = get_competition(db, competition_id, lock=True)
    row.rules = payload.model_dump()
    commit(db)
    return summary(row)


@router.post("/competitions/{competition_id}/teams/preview", dependencies=[Depends(require_admin)])
def preview_participants(competition_id: int, payload: ParticipantsSelection, db: Database):
    competition = get_competition(db, competition_id, lock=True)
    return participants_plan(db, competition, payload)


@router.put("/competitions/{competition_id}/teams", dependencies=[Depends(require_admin)])
def update_participants(competition_id: int, payload: ParticipantsUpdate, db: Database):
    # The same competition row lock serializes imports and membership changes.
    competition = get_competition(db, competition_id, lock=True)
    plan = participants_plan(db, competition, payload)
    if not plan["can_apply"]:
        raise HTTPException(409, " ".join(plan["conflicts"]))
    removed = [team["id"] for team in plan["removed"]]
    if removed:
        db.execute(delete(CompetitionTeam).where(CompetitionTeam.competition_id == competition_id,
                                               CompetitionTeam.team_id.in_(removed)))
    db.add_all([CompetitionTeam(competition_id=competition_id, team_id=team["id"]) for team in plan["added"]])
    commit(db)
    return participants(competition_id, db)


@router.post("/competitions/{competition_id}/fixtures/import", dependencies=[Depends(require_editor)])
def import_fixtures(competition_id: int, payload: FixtureImport, db: Database):
    competition = get_competition(db, competition_id, lock=True)
    return apply_fixture_import(db, competition, payload)


def apply_fixture_import(db, competition, payload, *, commit_changes=True, validate_only=False, member_ids=None):
    """Shared batch validation for manual input and verified FPF mapping."""
    competition_id = competition.id
    members = set(db.scalars(select(CompetitionTeam.team_id).where(CompetitionTeam.competition_id == competition_id)))
    if member_ids is not None:
        members = set(member_ids)
    existing = {row.external_key: row for row in db.scalars(select(CompetitionFixture).where(
        CompetitionFixture.competition_id == competition_id))}
    changes = []
    # Validate the entire batch before mutating anything. Imports replace each keyed fixture.
    for item in payload.fixtures:
        if not {item.home_team_id, item.away_team_id} <= members:
            raise HTTPException(409, "As equipas têm de participar na competição.")
        previous = existing.get(item.external_key)
        identity = (item.matchday, item.home_team_id, item.away_team_id, item.internal_match_id)
        if previous and identity != (previous.matchday, previous.home_team_id, previous.away_team_id, previous.internal_match_id):
            raise HTTPException(409, "Uma chave existente não pode identificar outro jogo.")
        if competition.internal_team_id in {item.home_team_id, item.away_team_id}:
            if item.internal_match_id is None:
                raise HTTPException(409, "Jogos da nossa equipa exigem ligação a um jogo interno, sem resultado externo.")
        elif item.internal_match_id is not None:
            raise HTTPException(409, "Apenas jogos da nossa equipa podem ter ligação interna.")
        if item.internal_match_id is not None:
            match = db.scalar(select(Match).where(Match.id == item.internal_match_id).with_for_update(of=Match))
            if match is None:
                raise HTTPException(404, "Jogo interno não encontrado.")
            home, away = (match.team_id, match.opponent_id) if match.is_home else (match.opponent_id, match.team_id)
            if (match.season_id, match.team_id, match.matchday, home, away) != (
                competition.season_id, competition.internal_team_id, item.matchday, item.home_team_id, item.away_team_id
            ):
                raise HTTPException(409, "Jogo interno incompatível com época, jornada ou equipas.")
        changes.append((previous, item))
    if validate_only:
        return dict(imported=len(changes))
    for previous, item in changes:
        if previous is None:
            db.add(CompetitionFixture(competition_id=competition_id, **item.model_dump()))
        else:
            for key, value in item.model_dump().items():
                setattr(previous, key, value)
    if commit_changes:
        commit(db)
    else:
        db.flush()
    return dict(imported=len(changes))


@router.get("/competitions/{competition_id}/calendar")
def read_calendar(competition_id: int, db: Database, matchday: Annotated[int | None, Query(gt=0)] = None):
    rows = calendar(db, competition_id)
    return [row for row in rows if matchday is None or row["matchday"] == matchday]


@router.get("/competitions/{competition_id}/matchdays")
def read_matchdays(competition_id: int, db: Database):
    groups = {}
    for row in calendar(db, competition_id):
        groups.setdefault(row["matchday"], []).append(row)
    return [dict(matchday=number, fixtures=rows) for number, rows in groups.items()]


@router.get("/competitions/{competition_id}/standings")
def read_standings(competition_id: int, db: Database):
    return standings(db, competition_id)
