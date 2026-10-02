from sqlalchemy import create_engine, text
from conftest import alembic


def test_0004_refuses_ambiguous_shots_and_preserves_events(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0003").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams(id,name) VALUES(1,'Clube'),(2,'Adversario')"))
        db.execute(text("INSERT INTO matches(id,season_id,team_id,opponent_id,matchday,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,1,'2026-10-04T14:00:00Z',true,'SCHEDULED',0)"))
        db.execute(text("INSERT INTO match_events(id,match_id,event_type,team,period,elapsed_seconds,notes) VALUES(1,1,'SHOT','OPPONENT',1,60,'legado')"))
    result = alembic(url, "upgrade", "head")
    assert result.returncode != 0 and "manually classify" in result.stderr
    with engine.begin() as db:
        assert db.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0003"
        assert db.execute(text("SELECT event_type::text FROM match_events")).scalar() == "SHOT"
        db.execute(text("UPDATE match_events SET event_type='SHOT_OFF_TARGET'"))
        before = db.execute(text("SELECT id,match_id,event_type::text,team::text,period,elapsed_seconds,notes,created_at FROM match_events")).all()
    assert alembic(url, "upgrade", "head").returncode == 0
    with engine.connect() as db:
        assert db.execute(text("SELECT id,match_id,event_type::text,team::text,period,elapsed_seconds,notes,created_at FROM match_events")).all() == before
        assert 'SHOT' not in db.execute(text("SELECT unnest(enum_range(NULL::event_type))::text")).scalars().all()
    assert alembic(url, "check").returncode == 0
    assert alembic(url, "downgrade", "0003").returncode == 0
    with engine.connect() as db:
        assert db.execute(text("SELECT id,match_id,event_type::text,team::text,period,elapsed_seconds,notes,created_at FROM match_events")).all() == before
        assert 'SHOT' in db.execute(text("SELECT unnest(enum_range(NULL::event_type))::text")).scalars().all()
    engine.dispose()
