import pytest
from sqlalchemy import create_engine, text

from conftest import alembic
from app.enums import MatchStatus, EventTeam, EventType
from app.models import Match, MatchEvent
from test_matches import games, create  # noqa: F401


@pytest.fixture
def competition(games):
    client, db, payload, _ = games
    ids = [payload["team_id"]]
    for name in ("Adversário A", "Adversário B", "Adversário C"):
        response = client.post("/teams", json={"name": name})
        assert response.status_code == 201, response.text
        ids.append(response.json()["id"])
    response = client.post("/competitions", json=dict(name="Liga Dappin", season_id=payload["season_id"],
        internal_team_id=ids[0], team_ids=ids))
    assert response.status_code == 201, response.text
    return client, db, payload, ids, response.json()["id"]


def fixture(home, away, key="one", **kwargs):
    return dict(external_key=key, matchday=1, home_team_id=home, away_team_id=away,
                source="Introdução manual verificada", **kwargs)


def send(client, cid, *rows):
    return client.post(f"/competitions/{cid}/fixtures/import", json={"fixtures": rows})


def test_import_reimport_correction_calendar_and_no_internal_changes(competition):
    client, db, payload, ids, cid = competition
    match = create(client, {**payload, "opponent_name": "Adversário A", "matchday": 1})
    before = client.get(f"/matches/{match['id']}").json()
    external = fixture(ids[2], ids[3], home_goals=2, away_goals=1)
    own = fixture(ids[0], ids[1], "ours", internal_match_id=match["id"])
    assert send(client, cid, external, own).status_code == 200
    assert send(client, cid, external, own).status_code == 200
    assert len(client.get(f"/competitions/{cid}/calendar").json()) == 2
    assert len(client.get(f"/competitions/{cid}/teams").json()) == 4
    assert client.get(f"/competitions/{cid}/matchdays").json()[0]["matchday"] == 1
    assert client.get(f"/competitions/{cid}/calendar?matchday=2").json() == []
    assert send(client, cid, {**external, "away_goals": 2}).status_code == 200
    table = client.get(f"/competitions/{cid}/standings").json()
    assert table["provisional"] and table["completed_fixtures"] == 1
    row = next(row for row in table["rows"] if row["team_id"] == ids[2])
    assert (row["played"], row["draws"], row["points"], row["goals_for"]) == (1, 1, 1, 2)
    # Linking changes deletion eligibility, while every stored/live field stays intact.
    assert client.get(f"/matches/{match['id']}").json() == {**before, "can_delete": False}
    assert send(client, cid, {**external, "home_goals": None, "away_goals": None}).status_code == 200
    assert client.get(f"/competitions/{cid}/standings").json()["completed_fixtures"] == 0


def test_internal_away_score_derived_and_reopen_excluded(competition):
    client, db, payload, ids, cid = competition
    match = create(client, {**payload, "opponent_name": "Adversário A", "matchday": 1, "is_home": False})
    row = db.get(Match, match["id"])
    row.status = MatchStatus.FINISHED
    db.add_all([MatchEvent(match_id=row.id, event_type=EventType.GOAL, team=EventTeam.US, period=1, elapsed_seconds=0),
                MatchEvent(match_id=row.id, event_type=EventType.OWN_GOAL, team=EventTeam.US, period=1, elapsed_seconds=0)])
    db.commit()
    assert send(client, cid, fixture(ids[1], ids[0], internal_match_id=row.id)).status_code == 200
    values = client.get(f"/competitions/{cid}/standings").json()
    ours = next(r for r in values["rows"] if r["team_id"] == ids[0])
    assert (ours["goals_for"], ours["goals_against"], ours["draws"]) == (1, 1, 1)
    row.status = MatchStatus.SECOND_HALF
    db.commit()
    assert client.get(f"/competitions/{cid}/standings").json()["completed_fixtures"] == 0
    row.matchday = 2
    db.commit()
    assert client.get(f"/competitions/{cid}/calendar").status_code == 409


def test_atomic_validation_duplicate_and_identity_protection(competition):
    client, db, payload, ids, cid = competition
    first = fixture(ids[1], ids[2], home_goals=1, away_goals=0)
    bad = fixture(ids[0], ids[3], "bad", home_goals=9, away_goals=0)
    assert send(client, cid, first, bad).status_code == 409
    assert client.get(f"/competitions/{cid}/calendar").json() == []
    assert send(client, cid, first, first).status_code == 422
    assert send(client, cid, first, {**first, "external_key": "duplicate"}).status_code == 409
    assert client.get(f"/competitions/{cid}/calendar").json() == []
    assert send(client, cid, first).status_code == 200
    assert send(client, cid, {**first, "matchday": 2}).status_code == 409
    assert send(client, cid, {**first, "away_goals": None}).status_code == 422
    assert send(client, cid, {**first, "home_goals": -1}).status_code == 422
    assert send(client, cid, {**first, "kickoff_at": "2026-10-15T15:00:00"}).status_code == 422
    assert send(client, cid, {**first, "home_team_id": 2147483647}).status_code == 409


def test_configurable_head_to_head_precedes_goal_difference(competition):
    client, _, _, ids, cid = competition
    # B beats C, C beats D heavily, D beats B: all three have three points.
    assert send(client, cid,
        fixture(ids[1], ids[2], "bc", home_goals=1, away_goals=0),
        fixture(ids[2], ids[3], "cd", home_goals=10, away_goals=0),
        fixture(ids[3], ids[1], "db", home_goals=2, away_goals=0)).status_code == 200
    table = client.get(f"/competitions/{cid}/standings").json()["rows"]
    assert all(row["unresolved_tie"] for row in table[:3])
    assert client.put(f"/competitions/{cid}/rules", json=dict(win=3, draw=1, loss=0,
        tiebreakers=["head_to_head_points", "head_to_head_goal_difference"])).status_code == 200
    table = client.get(f"/competitions/{cid}/standings").json()["rows"]
    assert [row["team_id"] for row in table[:3]] == [ids[2], ids[1], ids[3]]
    # With B and C tied on points, B wins the direct meeting despite C's better GD.
    assert send(client, cid, fixture(ids[3], ids[1], "db", home_goals=None, away_goals=None)).status_code == 200
    table = client.get(f"/competitions/{cid}/standings").json()["rows"]
    assert [row["team_id"] for row in table[:2]] == [ids[1], ids[2]]


def test_linked_game_cannot_be_deleted_or_absorbed(competition):
    client, db, payload, ids, cid = competition
    original = create(client, {**payload, "opponent_name": "Adversário A", "matchday": 1})
    continuation = create(client, {**payload, "opponent_name": "Adversário A", "matchday": 1})
    assert send(client, cid, fixture(ids[0], ids[1], internal_match_id=continuation["id"])).status_code == 200
    assert not client.get(f"/matches/{continuation['id']}").json()["can_delete"]
    assert client.delete(f"/matches/{continuation['id']}").status_code == 409
    for game in (original, continuation):
        db.get(Match, game["id"]).status = MatchStatus.FINISHED
    db.commit()
    preview = client.post("/matches/merge/preview", json=dict(principal_id=original["id"],
        continuation_id=continuation["id"], final_status="FINISHED"))
    assert preview.status_code == 200, preview.text
    assert not preview.json()["can_merge"]
    assert any("calendário" in message for message in preview.json()["conflicts"])


def test_competition_migration_is_additive_and_downgrade_guarded(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0006").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams(id,name) VALUES(1,'CCDR'),(2,'Visitante')"))
        db.execute(text("INSERT INTO matches(id,season_id,team_id,opponent_id,matchday,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,1,'2026-10-15T14:00:00Z',true,'FINISHED',5400)"))
        before = db.execute(text("SELECT * FROM matches")).all()
    result = alembic(url, "upgrade", "0007")
    assert result.returncode == 0, result.stderr
    with engine.begin() as db:
        assert db.execute(text("SELECT * FROM matches")).all() == before
        db.execute(text("INSERT INTO competitions(season_id,internal_team_id,name,rules) VALUES(1,1,'Liga','{}')"))
    result = alembic(url, "downgrade", "0006")
    assert result.returncode != 0 and "Downgrade recusado" in result.stderr
    with engine.connect() as db:
        assert db.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0007"
        assert db.execute(text("SELECT * FROM matches")).all() == before
    engine.dispose()
