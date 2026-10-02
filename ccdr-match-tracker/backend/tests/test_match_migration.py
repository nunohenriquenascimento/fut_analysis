from sqlalchemy import create_engine, text

from conftest import alembic


def test_matchday_migration_preserves_existing_game_and_squad(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0002").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams(id,name) VALUES(1,'Clube'),(2,'Adversario')"))
        db.execute(text("INSERT INTO players(id,season_id,team_id,name,position,is_active) VALUES(1,1,1,'Jogador','MC',true)"))
        db.execute(text("INSERT INTO matches(id,season_id,team_id,opponent_id,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,'2026-10-04T14:00:00Z',true,'SCHEDULED',0)"))
        db.execute(text("INSERT INTO match_squads(id,match_id,player_id,is_starter) VALUES(1,1,1,true)"))
        before = db.execute(text("SELECT * FROM matches")).all()
        squad = db.execute(text("SELECT * FROM match_squads")).all()
    result = alembic(url, "upgrade", "head")
    assert result.returncode == 0, result.stderr
    with engine.begin() as db:
        assert db.execute(text("SELECT matchday FROM matches")).scalar() is None
        assert db.execute(text("SELECT * FROM match_squads")).all() == squad
        db.execute(text("UPDATE matches SET matchday=3"))
    result = alembic(url, "check")
    assert result.returncode == 0, result.stdout + result.stderr
    result = alembic(url, "downgrade", "0002")
    assert result.returncode == 0, result.stderr
    with engine.connect() as db:
        assert db.execute(text("SELECT * FROM matches")).all() == before
        assert db.execute(text("SELECT * FROM match_squads")).all() == squad
    engine.dispose()
