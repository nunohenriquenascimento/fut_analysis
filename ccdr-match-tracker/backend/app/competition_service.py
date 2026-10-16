"""Competition reads combine external results with linked, event-derived games."""
from fastapi import HTTPException
from sqlalchemy import select

from app.enums import MatchStatus
from app.live_service import events, score
from app.models import Competition, CompetitionFixture, CompetitionTeam, Match, Team
from app.fpf_source import ORIGIN


def get_competition(db, competition_id, lock=False):
    query = select(Competition).where(Competition.id == competition_id)
    if lock:
        query = query.with_for_update()
    item = db.scalar(query)
    if item is None:
        raise HTTPException(404, "Competição não encontrada.")
    return item


def calendar(db, competition_id):
    competition = get_competition(db, competition_id)
    snapshot = competition.fpf_data or {}
    mapping = snapshot.get("team_mapping", {})
    schedules = {(capture["matchday"], mapping.get(game["home_name"]), mapping.get(game["away_name"])): game.get("schedule_text")
                 for capture in snapshot.get("round_captures", {}).values()
                 if capture["series_id"] == snapshot.get("identity", [None, None, None])[2]
                 for game in capture["matches"]}
    rows = db.scalars(select(CompetitionFixture).where(CompetitionFixture.competition_id == competition_id)
                      .order_by(CompetitionFixture.matchday, CompetitionFixture.kickoff_at, CompetitionFixture.id))
    result = []
    for row in rows:
        data = {column.name: getattr(row, column.name) for column in CompetitionFixture.__table__.columns}
        data["status"] = "FINISHED" if row.home_goals is not None else "SCHEDULED"
        if row.internal_match_id is None and row.source.startswith(ORIGIN + "/"):
            schedule = schedules.get((row.matchday, row.home_team_id, row.away_team_id))
            if schedule:
                data["schedule_text"] = schedule
        if row.internal_match_id is not None:
            match = db.get(Match, row.internal_match_id)
            actual_home, actual_away = ((match.team_id, match.opponent_id) if match.is_home else (match.opponent_id, match.team_id))
            if (match.season_id, actual_home, actual_away, match.matchday) != (
                get_competition(db, competition_id).season_id, row.home_team_id, row.away_team_id, row.matchday
            ):
                raise HTTPException(409, "Ligação interna desatualizada; reveja o calendário.")
            value = score(events(db, match.id))
            data.update(status=match.status.value, kickoff_at=match.kickoff_at, venue=match.venue,
                        home_goals=value.us if match.is_home else value.opponent,
                        away_goals=value.opponent if match.is_home else value.us)
        result.append(data)
    return result


def standings(db, competition_id):
    competition = get_competition(db, competition_id)
    fixtures = [row for row in calendar(db, competition_id) if row["status"] == "FINISHED"]
    teams = db.scalars(select(Team).join(CompetitionTeam, CompetitionTeam.team_id == Team.id)
                       .where(CompetitionTeam.competition_id == competition_id).order_by(Team.id)).all()
    table = {team.id: dict(team_id=team.id, name=team.name, played=0, wins=0, draws=0, losses=0,
                           goals_for=0, goals_against=0, goal_difference=0, points=0) for team in teams}
    policy = competition.rules
    for game in fixtures:
        for team_id, gf, ga in ((game["home_team_id"], game["home_goals"], game["away_goals"]),
                                (game["away_team_id"], game["away_goals"], game["home_goals"])):
            row = table[team_id]
            outcome = "win" if gf > ga else "draw" if gf == ga else "loss"
            row["played"] += 1
            row[{"win": "wins", "draw": "draws", "loss": "losses"}[outcome]] += 1
            row["goals_for"] += gf
            row["goals_against"] += ga
            row["goal_difference"] += gf - ga
            row["points"] += policy[outcome]

    def refine(group, criteria):
        if len(group) <= 1 or not criteria:
            return [group]
        criterion, *remaining = criteria
        ids = {row["team_id"] for row in group}
        values = {team_id: 0 for team_id in ids}
        if criterion.startswith("head_to_head"):
            for game in fixtures:
                h, a = game["home_team_id"], game["away_team_id"]
                if h not in ids or a not in ids:
                    continue
                hg, ag = game["home_goals"], game["away_goals"]
                if criterion == "head_to_head_points":
                    values[h] += policy["win" if hg > ag else "draw" if hg == ag else "loss"]
                    values[a] += policy["win" if ag > hg else "draw" if hg == ag else "loss"]
                else:
                    values[h] += hg - ag
                    values[a] += ag - hg
        else:
            values = {row["team_id"]: row[criterion] for row in group}
        buckets = {}
        for row in group:
            buckets.setdefault(values[row["team_id"]], []).append(row)
        return [part for value in sorted(buckets, reverse=True) for part in refine(buckets[value], remaining)]

    groups = refine(list(table.values()), ["points", *policy["tiebreakers"]])
    output, rank = [], 1
    for group in groups:
        for row in group:
            output.append(dict(row, rank=rank, unresolved_tie=len(group) > 1))
        rank += len(group)
    return dict(provisional=True, warning="Regulamento 2026/2027 não validado; política configurável. Sem sanções administrativas.",
                rules=policy, completed_fixtures=len(fixtures), rows=output)
