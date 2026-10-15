"""Plan and apply membership changes; never delete shared teams or matches."""
from fastapi import HTTPException
from sqlalchemy import or_, select

from app.models import CompetitionFixture, CompetitionTeam, Match, Team


def participants_plan(db, competition, selection):
    current = set(db.scalars(select(CompetitionTeam.team_id).where(CompetitionTeam.competition_id == competition.id)))
    if current != set(selection.expected_team_ids):
        raise HTTPException(409, "Os participantes foram alterados. Atualize a lista antes de rever a alteração.")
    proposed = set(selection.team_ids)
    teams = {team.id: team for team in db.scalars(select(Team).where(Team.id.in_(proposed | current)))}
    if proposed - teams.keys():
        raise HTTPException(404, "Equipa não encontrada.")
    conflicts = []
    if competition.internal_team_id not in proposed:
        conflicts.append("A nossa equipa tem de permanecer na competição.")
    removed = current - proposed
    if removed:
        fixtures = db.scalars(select(CompetitionFixture).where(
            CompetitionFixture.competition_id == competition.id,
            or_(CompetitionFixture.home_team_id.in_(removed), CompetitionFixture.away_team_id.in_(removed))
        )).all()
        if fixtures:
            conflicts.append("Não é possível retirar participantes com jogos no calendário ou resultados registados nesta competição.")
        internal = db.scalar(select(Match.id).where(
            Match.season_id == competition.season_id, Match.team_id == competition.internal_team_id,
            Match.opponent_id.in_(removed)
        ).limit(1))
        if internal is not None:
            conflicts.append("Existem jogos internos com participantes a retirar nesta época; reveja as dependências antes de alterar a competição.")
    def describe(ids):
        return [dict(id=team_id, name=teams[team_id].name) for team_id in sorted(ids)]
    return dict(current_team_ids=sorted(current), proposed_team_ids=sorted(proposed),
                added=describe(proposed - current), removed=describe(removed), conflicts=conflicts,
                can_apply=not conflicts)
