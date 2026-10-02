from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, func, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Match, MatchSquad, Player, Season, Team
from app.enums import PlayerPosition


@pytest.fixture
def games(migrated_database_url):
    engine = create_engine(migrated_database_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
            season = Season(name="2026/27", starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
            other_season = Season(name="2027/28", starts_on=date(2027, 7, 1), ends_on=date(2028, 6, 30))
            team, other_team = Team(name="CCDR Vila Cortez do Mondego"), Team(name="Outro clube")
            db.add_all([season, other_season, team, other_team])
            db.flush()
            players = [Player(name=f"Jogador {i}", season_id=season.id, team_id=team.id,
                              position=PlayerPosition.MC, shirt_number=i) for i in range(1, 5)]
            players += [Player(name="Outra equipa", season_id=season.id, team_id=other_team.id, position=PlayerPosition.GR),
                        Player(name="Outra época", season_id=other_season.id, team_id=team.id, position=PlayerPosition.GR)]
            players[3].is_active = False
            db.add_all(players)
            db.commit()
            payload = {"season_id": season.id, "team_id": team.id, "opponent_name": "Adversário",
                       "matchday": 3, "kickoff_at": "2026-10-04T15:00:00+01:00", "is_home": True, "venue": "Campo"}
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as client:
                    yield client, db, payload, [player.id for player in players]
            finally:
                app.dependency_overrides.clear()
        transaction.rollback()
    engine.dispose()


def create(client, payload):
    response = client.post("/matches", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def squad(*entries):
    return {"players": [{"player_id": player_id, "is_starter": starter} for player_id, starter in entries]}


def test_create_list_detail_edit_and_reuse_opponent(games):
    client, db, payload, _ = games
    match = create(client, payload)
    assert match["status"] == "SCHEDULED"
    assert match["matchday"] == 3
    assert match["opponent_name"] == "Adversário"
    assert db.get(Team, match["opponent_id"]).name == "Adversário"
    second = create(client, {**payload, "opponent_name": "  ADVERSÁRIO  ", "matchday": 4})
    assert second["opponent_id"] == match["opponent_id"]
    assert client.get(f"/matches/{match['id']}").json() == {**match, "score": {"us": 0, "opponent": 0}, "can_delete": True, "can_cancel": True}
    listed = client.get("/matches", params={"season_id": payload["season_id"], "team_id": payload["team_id"]})
    assert listed.status_code == 200
    assert {row["id"] for row in listed.json()} == {match["id"], second["id"]}
    assert client.get("/matches?season_id=2147483647").json() == []
    response = client.patch(f"/matches/{match['id']}", json={"matchday": 5, "opponent_name": "Outro clube",
        "kickoff_at": "2026-11-01T18:00:00Z", "is_home": False, "venue": None})
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["matchday"] == 5 and updated["is_home"] is False and updated["venue"] is None
    assert updated["opponent_name"] == "Outro clube"
    assert updated["kickoff_at"].startswith("2026-11-01T18:00:00")
    assert updated["status"] == "SCHEDULED"
    assert updated["opponent_id"] == db.scalar(select(Team.id).where(Team.name == "Outro clube"))


def test_save_replace_and_preserve_inactive(games):
    client, db, payload, ids = games
    match = create(client, payload)
    path = f"/matches/{match['id']}/squad"
    assert {row["player"]["id"] for row in client.get(path).json()} == set(ids[:3])
    assert client.put(path, json=squad((ids[0], True), (ids[1], False))).status_code == 200
    original = db.scalar(select(MatchSquad).where(MatchSquad.player_id == ids[0]))
    original_id = original.id
    client.patch(f"/players/{ids[0]}", json={"is_active": False})
    rows = client.get(path).json()
    retained = next(row for row in rows if row["player"]["id"] == ids[0])
    assert retained["role"] == "TITULAR" and not retained["player"]["is_active"]
    # Retained inactive entries may change role; unselected inactive players cannot join.
    response = client.put(path, json=squad((ids[0], False), (ids[1], True), (ids[2], False)))
    assert response.status_code == 200
    assert db.get(MatchSquad, original_id).is_starter is False
    assert db.scalar(select(func.count()).select_from(MatchSquad)) == 3
    assert client.put(path, json=squad((ids[1], True))).status_code == 200
    assert db.scalar(select(func.count()).select_from(MatchSquad)) == 1
    assert ids[0] not in {row["player"]["id"] for row in client.get(path).json()}
    assert client.put(path, json=squad((ids[0], True))).status_code == 409
    assert client.put(path, json=squad()).status_code == 200
    assert db.scalar(select(func.count()).select_from(MatchSquad)) == 0


@pytest.mark.parametrize("invalid_index,status", [(3, 409), (4, 409), (5, 409), (6, 404)])
def test_invalid_player_does_not_partially_replace(games, invalid_index, status):
    client, db, payload, ids = games
    path = f"/matches/{create(client, payload)['id']}/squad"
    client.put(path, json=squad((ids[0], True)))
    before = client.get(path).json()
    invalid_id = ids[invalid_index] if invalid_index < len(ids) else 2147483647
    response = client.put(path, json=squad((ids[1], False), (invalid_id, True)))
    assert response.status_code == status, response.text
    assert client.get(path).json() == before
    assert db.scalar(select(func.count()).select_from(MatchSquad)) == 1


def test_duplicate_and_invalid_squad_are_atomic(games):
    client, _, payload, ids = games
    path = f"/matches/{create(client, payload)['id']}/squad"
    client.put(path, json=squad((ids[0], True)))
    before = client.get(path).json()
    assert client.put(path, json=squad((ids[1], True), (ids[1], False))).status_code == 409
    assert client.put(path, json={"players": [{"player_id": ids[0], "is_starter": "yes"}]}).status_code == 422
    assert client.get(path).json() == before


def test_database_failure_rolls_back_replacement(games):
    client, db, payload, ids = games
    path = f"/matches/{create(client, payload)['id']}/squad"
    assert client.put(path, json=squad((ids[0], True))).status_code == 200
    before = client.get(path).json()

    def fail_flush(*args):
        raise IntegrityError("injected write failure", {}, Exception("test"))

    event.listen(db, "before_flush", fail_flush, once=True)
    try:
        assert client.put(path, json=squad((ids[1], False))).status_code == 409
    finally:
        event.remove(db, "before_flush", fail_flush)
    assert client.get(path).json() == before


def test_no_starter_limit_and_repeated_save_is_idempotent(games):
    client, db, payload, _ = games
    extra = [Player(name=f"Extra {number}", season_id=payload["season_id"], team_id=payload["team_id"],
                    shirt_number=number, position=PlayerPosition.MC) for number in range(10, 22)]
    db.add_all(extra)
    db.commit()
    path = f"/matches/{create(client, payload)['id']}/squad"
    body = squad(*[(player.id, True) for player in extra])
    assert client.put(path, json=body).status_code == 200
    original_ids = db.scalars(select(MatchSquad.id).order_by(MatchSquad.id)).all()
    assert len(original_ids) == 12
    assert client.put(path, json=body).status_code == 200
    assert db.scalars(select(MatchSquad.id).order_by(MatchSquad.id)).all() == original_ids


@pytest.mark.parametrize("changes", [{"matchday": 0}, {"matchday": None}, {"matchday": 1.5},
    {"opponent_name": " "}, {"kickoff_at": "2026-10-04T15:00:00"}, {"status": "FIRST_HALF"}, {"is_home": "yes"}])
def test_invalid_create(games, changes):
    client, _, payload, _ = games
    assert client.post("/matches", json={**payload, **changes}).status_code == 422


def test_missing_matches_invalid_patch_self_opponent_and_cors(games):
    client, db, payload, _ = games
    for method, path, body in [("get", "/matches/2147483647", None),
        ("patch", "/matches/2147483647", {"matchday": 1}),
        ("get", "/matches/2147483647/squad", None), ("put", "/matches/2147483647/squad", squad())]:
        response = client.request(method, path, json=body)
        assert response.status_code == 404
    assert client.post("/matches", json={**payload, "opponent_name": "ccdr vila cortez do mondego"}).status_code == 409
    match = create(client, payload)
    for changes in [{}, {"status": "FINISHED"}, {"matchday": None}, {"team_id": 2}, {"season_id": 2}]:
        assert client.patch(f"/matches/{match['id']}", json=changes).status_code == 422
    before = client.get(f"/matches/{match['id']}").json()
    assert client.patch(f"/matches/{match['id']}", json={"matchday": 7, "opponent_name": "CCDR Vila Cortez do Mondego"}).status_code == 409
    assert client.get(f"/matches/{match['id']}").json() == before
    response = client.options(f"/matches/{match['id']}/squad", headers={"Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "PUT", "Access-Control-Request-Headers": "content-type"})
    assert response.status_code == 200 and "PUT" in response.headers["access-control-allow-methods"]
