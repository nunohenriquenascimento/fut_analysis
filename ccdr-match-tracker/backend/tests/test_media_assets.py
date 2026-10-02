import pytest
from sqlalchemy import create_engine, text

from conftest import alembic
from test_matches import games, create  # noqa: F401 -- isolated PostgreSQL fixture


def test_media_paths_persist_and_propagate_without_changing_game_rules(games):
    client, db, payload, ids = games
    game = create(client, payload)
    player_path = f"/players/{ids[0]}"
    assert client.patch(player_path, json={"photo_path": "/players/jogador-1.webp"}).status_code == 200
    assert client.patch(f"/teams/{payload['team_id']}", json={"crest_path": "/clubs/ccdr-vila-cortez/crest.png"}).status_code == 200
    assert client.patch(f"/teams/{game['opponent_id']}", json={"crest_path": "/teams/adversario.png"}).status_code == 200
    db.expire_all()
    for endpoint in [f"/matches/{game['id']}", f"/matches/{game['id']}/live", f"/matches/{game['id']}/stats"]:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        match = data.get("match", data)
        assert match["team_crest_path"] == "/clubs/ccdr-vila-cortez/crest.png"
        assert match["opponent_crest_path"] == "/teams/adversario.png"
        assert data["score"] == {"us": 0, "opponent": 0}
    assert client.get("/players/context").json()["team_crest_path"] == "/clubs/ccdr-vila-cortez/crest.png"
    squad = client.get(f"/matches/{game['id']}/squad").json()
    assert next(row for row in squad if row["player"]["id"] == ids[0])["player"]["photo_path"] == "/players/jogador-1.webp"
    for endpoint in ["/statistics/season", "/statistics/players"]:
        data = client.get(endpoint).json()
        assert data["context"]["team_crest_path"] == "/clubs/ccdr-vila-cortez/crest.png"
        assert next(row for row in data["players"] if row["player"]["id"] == ids[0])["player"]["photo_path"] == "/players/jogador-1.webp"
        assert all(not ranking for ranking in data["rankings"].values())
    teams = client.get("/teams").json()
    assert next(row for row in teams if row["id"] == game["opponent_id"])["crest_path"] == "/teams/adversario.png"
    assert client.patch(player_path, json={"photo_path": None}).json()["photo_path"] is None
    assert client.patch(f"/teams/{game['opponent_id']}", json={"crest_path": None}).json()["crest_path"] is None
    assert client.patch("/teams/2147483647", json={"crest_path": None}).status_code == 404


@pytest.mark.parametrize("path", [r"C:\photos\player.png", "https://example.com/photo.png", "//example.com/a.png", "/players/../secret.png", "/players/a.exe", "/players/a.png?x=1", ""])
def test_media_rejects_non_public_paths(games, path):
    client, _, payload, ids = games
    assert client.patch(f"/players/{ids[0]}", json={"photo_path": path}).status_code == 422
    assert client.patch(f"/teams/{payload['team_id']}", json={"crest_path": path}).status_code == 422


def test_0005_upgrade_downgrade_preserves_existing_records(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0004").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams(id,name) VALUES(1,'Clube'),(2,'Adversario')"))
        db.execute(text("INSERT INTO players(id,season_id,team_id,name,position,shirt_number,is_active) VALUES(1,1,1,'Jogador','MC',8,false)"))
        db.execute(text("INSERT INTO matches(id,season_id,team_id,opponent_id,matchday,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,1,'2026-10-04T14:00:00Z',true,'FINISHED',5400)"))
        db.execute(text("INSERT INTO match_squads(id,match_id,player_id,is_starter) VALUES(1,1,1,true)"))
        db.execute(text("INSERT INTO match_events(id,match_id,event_type,team,player_id,period,elapsed_seconds) VALUES(1,1,'GOAL','US',1,1,60)"))
        tables = ["seasons", "teams", "players", "matches", "match_squads", "match_events"]
        columns = {table: list(db.execute(text(f"SELECT * FROM {table}")).keys()) for table in tables}
        before = {table: db.execute(text(f"SELECT * FROM {table} ORDER BY id")).all() for table in tables}
    result = alembic(url, "upgrade", "0005")
    assert result.returncode == 0, result.stderr
    with engine.begin() as db:
        for table in tables:
            assert db.execute(text(f"SELECT {','.join(columns[table])} FROM {table} ORDER BY id")).all() == before[table]
        assert db.execute(text("SELECT photo_path FROM players")).scalar() is None
        assert db.execute(text("SELECT crest_path FROM teams WHERE id=1")).scalar() is None
        db.execute(text("UPDATE players SET photo_path='/players/jogador-1.webp'"))
        db.execute(text("UPDATE teams SET crest_path='/teams/adversario.png' WHERE id=2"))
    assert alembic(url, "upgrade", "head").returncode == 0
    assert alembic(url, "check").returncode == 0
    result = alembic(url, "downgrade", "0004")
    assert result.returncode == 0, result.stderr
    with engine.connect() as db:
        for table in tables:
            assert db.execute(text(f"SELECT * FROM {table} ORDER BY id")).all() == before[table]
    assert alembic(url, "upgrade", "0005").returncode == 0
    engine.dispose()
