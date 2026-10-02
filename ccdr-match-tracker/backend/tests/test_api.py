"""HTTP validation without a database; optional integration against migrated PostgreSQL."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Non-secret, unused connection for tests that override the database dependency.
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://localhost/ccdr_test")

from app.database import get_db
from app.main import app
from app.models import Season, Team
from datetime import date


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: None
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_and_cors(client):
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.json() == {"status": "ok"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    response = client.options("/players", headers={
        "Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" not in client.get(
        "/health", headers={"Origin": "https://untrusted.example"}
    ).headers


def test_invalid_player_and_pagination(client):
    payload = {"name": " ", "season_id": 1, "team_id": 1, "position": "INVALID", "shirt_number": 100}
    assert client.post("/players", json=payload).status_code == 422
    assert client.get("/players?limit=201").status_code == 422
    assert client.get("/matches?offset=-1").status_code == 422


def test_invalid_match(client):
    payload = {"season_id": 1, "team_id": 1, "opponent_id": 1, "matchday": 1, "kickoff_at": "2026-10-04T14:00:00Z"}
    assert client.post("/matches", json=payload).status_code == 422
    payload.update(opponent_id=2, kickoff_at="2026-10-04T14:00:00")
    assert client.post("/matches", json=payload).status_code == 422


def test_postgresql_api(migrated_database_url):
    engine = create_engine(migrated_database_url)
    # Every request uses a savepoint; the outer transaction rolls everything back.
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
            season = Season(name="Integration test", starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
            team = Team(name="Test club")
            opponent = Team(name="Test opponent")
            db.add_all([season, team, opponent])
            db.commit()
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as client:
                    payload = {"name": "Jogador", "season_id": season.id, "team_id": team.id,
                               "position": "MC", "shirt_number": 8}
                    response = client.post("/players", json=payload)
                    assert response.status_code == 201, response.text
                    assert response.json()["is_active"] is True
                    assert client.post("/players", json=payload).status_code == 409
                    assert len(client.get(f"/players?season_id={season.id}&team_id={team.id}").json()) == 1
                    payload["season_id"] = 2147483647
                    assert client.post("/players", json=payload).status_code == 404
                    response = client.post("/matches", json={"season_id": season.id, "team_id": team.id,
                        "opponent_id": opponent.id, "matchday": 1, "kickoff_at": "2026-10-04T15:00:00+01:00"})
                    assert response.status_code == 201, response.text
                    assert response.json()["status"] == "SCHEDULED"
                    assert response.json()["elapsed_seconds"] == 0
                    assert len(client.get(f"/matches?season_id={season.id}").json()) == 1
            finally:
                app.dependency_overrides.clear()
        transaction.rollback()
    engine.dispose()
