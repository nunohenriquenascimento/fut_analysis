"""Read-model regressions without a database; not PostgreSQL integration tests."""
from types import SimpleNamespace

import pytest

from app import competition_service as service
from app.enums import MatchStatus
from app.models import CompetitionFixture, Match


class Rows(list):
    def all(self):
        return self


@pytest.fixture
def table_source(monkeypatch):
    competition = SimpleNamespace(rules=dict(win=3, draw=1, loss=0, tiebreakers=[]))
    fixtures = [
        dict(home_team_id=1, away_team_id=2, home_goals=2, away_goals=1, status="FINISHED"),
        dict(home_team_id=3, away_team_id=1, home_goals=3, away_goals=0, status="FINISHED"),
        dict(home_team_id=1, away_team_id=3, home_goals=1, away_goals=1, status="FINISHED"),
        dict(home_team_id=2, away_team_id=3, home_goals=10, away_goals=0, status="CANCELLED"),
        dict(home_team_id=1, away_team_id=2, home_goals=8, away_goals=0, status="SECOND_HALF"),
        dict(home_team_id=3, away_team_id=2, home_goals=None, away_goals=None, status="SCHEDULED"),
    ]
    monkeypatch.setattr(service, "get_competition", lambda *_: competition)
    monkeypatch.setattr(service, "calendar", lambda *_: fixtures)
    db = SimpleNamespace(scalars=lambda _: Rows(SimpleNamespace(id=i, name=f"Team {i}") for i in (1, 2, 3)))
    return db, competition, fixtures


def test_standings_aggregates_and_excludes_cancelled_unfinished_games(table_source):
    db, _, _ = table_source
    table = service.standings(db, 1)
    assert table["provisional"] is True
    assert table["completed_fixtures"] == 3
    ours = next(row for row in table["rows"] if row["team_id"] == 1)
    assert {key: ours[key] for key in (
        "played", "wins", "draws", "losses", "goals_for", "goals_against", "goal_difference", "points"
    )} == dict(played=3, wins=1, draws=1, losses=1, goals_for=3, goals_against=5, goal_difference=-2, points=4)
    tied = [row for row in table["rows"] if row["rank"] == 1]
    assert {row["team_id"] for row in tied} == {1, 3}
    assert all(row["unresolved_tie"] for row in tied)


def test_correction_recomputes_points_without_cached_totals(table_source):
    db, competition, fixtures = table_source
    service.standings(db, 1)
    fixtures[0].update(home_goals=0, away_goals=0)
    rows = {row["team_id"]: row for row in service.standings(db, 1)["rows"]}
    assert [rows[i]["points"] for i in (1, 2, 3)] == [2, 1, 4]
    competition.rules = dict(win=2, draw=1, loss=0, tiebreakers=[])
    rows = {row["team_id"]: row for row in service.standings(db, 1)["rows"]}
    assert rows[3]["points"] == 3


@pytest.mark.parametrize("home", [True, False])
def test_calendar_reads_internal_score_without_storing_external_goals(monkeypatch, home):
    competition = SimpleNamespace(season_id=1)
    match = Match(id=7, season_id=1, team_id=1, opponent_id=2, matchday=3,
                  is_home=home, status=MatchStatus.CANCELLED, venue="Internal venue")
    fixture = CompetitionFixture(id=8, competition_id=1, external_key="ours", matchday=3,
                                 home_team_id=1 if home else 2, away_team_id=2 if home else 1,
                                 internal_match_id=7, source="Calendar", home_goals=None, away_goals=None)
    monkeypatch.setattr(service, "get_competition", lambda *_: competition)
    monkeypatch.setattr(service, "events", lambda *_: [])
    monkeypatch.setattr(service, "score", lambda _: SimpleNamespace(us=2, opponent=1))
    db = SimpleNamespace(scalars=lambda _: Rows([fixture]), get=lambda *_: match)
    row, = service.calendar(db, 1)
    assert row["status"] == "CANCELLED"
    assert (row["home_goals"], row["away_goals"]) == ((2, 1) if home else (1, 2))
    assert fixture.home_goals is None and fixture.away_goals is None
    assert row["internal_match_id"] == 7 and row["venue"] == match.venue
