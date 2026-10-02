from sqlalchemy import create_engine, text

from conftest import alembic


def test_0006_preserves_users_events_and_round_trip(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0005").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO users(id,name,email,role,is_active) VALUES(1,'Legacy','legacy@test.local','ADMIN',true)"))
        db.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams(id,name) VALUES(1,'Clube'),(2,'Adversario')"))
        db.execute(text("INSERT INTO matches(id,season_id,team_id,opponent_id,matchday,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,1,'2026-10-04T14:00:00Z',true,'FINISHED',5400)"))
        db.execute(text("INSERT INTO match_events(id,match_id,event_type,team,period,elapsed_seconds,recorded_by_id) VALUES(1,1,'GOAL','OPPONENT',1,60,1)"))
        users = db.execute(text("SELECT * FROM users")).all()
        events = db.execute(text("SELECT * FROM match_events")).all()
    result = alembic(url, "upgrade", "head")
    assert result.returncode == 0, result.stderr
    assert alembic(url, "check").returncode == 0
    with engine.begin() as db:
        assert db.execute(text("SELECT password_hash FROM users")).scalar() is None
        assert db.execute(text("SELECT * FROM match_events")).all() == events
        db.execute(text("INSERT INTO auth_sessions(token_hash,user_id,csrf_token,expires_at) VALUES(:token,1,:csrf,now()+interval '8 hours')"), {"token": "a" * 64, "csrf": "b" * 64})
    result = alembic(url, "downgrade", "0005")
    assert result.returncode == 0, result.stderr
    with engine.connect() as db:
        assert db.execute(text("SELECT * FROM users")).all() == users
        assert db.execute(text("SELECT * FROM match_events")).all() == events
    assert alembic(url, "upgrade", "head").returncode == 0
    engine.dispose()
