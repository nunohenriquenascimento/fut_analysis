"""Roster behaviour on PostgreSQL, with all fixture changes rolled back."""
from datetime import date
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://localhost/ccdr_test")

from app.database import get_db
from app.main import app
from app.models import Player, Season, Team
from app.roster import CLUB_NAME, SEASON_NAME


@pytest.fixture
def roster(migrated_database_url):
    engine = create_engine(migrated_database_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
            season = db.scalar(select(Season).where(Season.name == SEASON_NAME))
            team = db.scalar(select(Team).where(Team.name == CLUB_NAME))
            if season is None:
                season = Season(name=SEASON_NAME, starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
                db.add(season)
            if team is None:
                team = Team(name=CLUB_NAME)
                db.add(team)
            db.commit()
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as client:
                    yield client, db, {"name": "Jogador de teste", "season_id": season.id,
                                       "team_id": team.id, "position": "MC", "shirt_number": 8}
            finally:
                app.dependency_overrides.clear()
        transaction.rollback()
    engine.dispose()


def create(client, payload):
    response = client.post("/players", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.parametrize("position", ["GR", "DC", "ALA", "MDC", "MC", "PL", "UNIVERSAL"])
def test_create_and_list(roster, position):
    client, db, payload = roster
    payload.update(position=position, name="  João Silva  ")
    player = create(client, payload)
    assert player["name"] == "João Silva"
    assert player["position"] == position
    assert player["is_active"] is True
    assert db.get(Player, player["id"]).shirt_number == 8
    response = client.get("/players", params={"season_id": payload["season_id"], "team_id": payload["team_id"]})
    assert response.status_code == 200
    assert player in response.json()
    assert client.get("/players", params={"team_id": 2147483647}).json() == []


def test_duplicate_number_and_scope(roster):
    client, db, payload = roster
    create(client, payload)
    assert client.post("/players", json=payload).status_code == 409
    other_team = Team(name=f"Other team {uuid4().hex}")
    other_season = Season(name=f"Test {uuid4().hex[:16]}", starts_on=date(2027, 7, 1), ends_on=date(2028, 6, 30))
    db.add_all([other_team, other_season])
    db.commit()
    create(client, {**payload, "team_id": other_team.id})
    create(client, {**payload, "season_id": other_season.id})


def test_update_and_duplicate_update(roster):
    client, db, payload = roster
    player = create(client, payload)
    second = create(client, {**payload, "shirt_number": 9})
    response = client.patch(f"/players/{player['id']}", json={"name": "Novo nome", "shirt_number": 10, "position": "ALA"})
    assert response.status_code == 200
    assert response.json()["name"] == "Novo nome"
    assert response.json()["shirt_number"] == 10
    assert response.json()["position"] == "ALA"
    assert response.json()["season_id"] == payload["season_id"]
    assert client.patch(f"/players/{second['id']}", json={"shirt_number": 10}).status_code == 409
    assert db.get(Player, second["id"]).shirt_number == 9


@pytest.mark.parametrize("changes", [{"name": "Outro nome"}, {"shirt_number": 11}, {"position": "MDC"}])
def test_individual_edits(roster, changes):
    client, _, payload = roster
    player = create(client, payload)
    response = client.patch(f"/players/{player['id']}", json=changes)
    assert response.status_code == 200
    assert response.json() == {**player, **changes}


def test_missing_context(roster):
    client, db, payload = roster
    db.get(Season, payload["season_id"]).name = "Other season"
    db.commit()
    assert client.get("/players/context").status_code == 404


def test_deactivate_preserves_player_and_number(roster):
    client, db, payload = roster
    player = create(client, payload)
    response = client.patch(f"/players/{player['id']}", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert response.json()["created_at"] == player["created_at"]
    assert db.get(Player, player["id"]).name == player["name"]
    assert any(row["id"] == player["id"] and not row["is_active"] for row in client.get("/players").json())
    assert client.post("/players", json=payload).status_code == 409
    assert client.patch(f"/players/{player['id']}", json={"is_active": True}).json()["is_active"] is True


@pytest.mark.parametrize("changes", [{}, {"name": " "}, {"name": None}, {"shirt_number": None},
    {"shirt_number": 0}, {"shirt_number": 100}, {"shirt_number": 1.5}, {"position": "DEFENDER"},
    {"position": None}, {"is_active": None}, {"is_active": "false"}, {"team_id": 2}])
def test_invalid_patch(roster, changes):
    client, _, payload = roster
    player = create(client, payload)
    assert client.patch(f"/players/{player['id']}", json=changes).status_code == 422


@pytest.mark.parametrize("changes", [{"name": " "}, {"shirt_number": 0}, {"shirt_number": 100},
    {"shirt_number": None}, {"shirt_number": 1.5}, {"position": "INVALID"}])
def test_invalid_create(roster, changes):
    client, _, payload = roster
    assert client.post("/players", json={**payload, **changes}).status_code == 422


def test_missing_player_context_and_patch_cors(roster):
    client, _, payload = roster
    assert client.patch("/players/2147483647", json={"name": "Nome"}).status_code == 404
    response = client.get("/players/context")
    assert response.status_code == 200
    assert response.json() == {"season_id": payload["season_id"], "team_id": payload["team_id"],
                               "season_name": SEASON_NAME, "team_name": CLUB_NAME, "team_crest_path": None}
    response = client.options("/players/1", headers={"Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "PATCH", "Access-Control-Request-Headers": "content-type"})
    assert response.status_code == 200
    assert "PATCH" in response.headers["access-control-allow-methods"]
