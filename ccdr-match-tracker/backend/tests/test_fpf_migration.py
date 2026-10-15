from sqlalchemy import create_engine, text

from conftest import alembic


def test_0008_is_additive_and_capture_downgrade_is_guarded(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0007").returncode == 0
    engine = create_engine(url)
    with engine.begin() as c:
        c.execute(text("INSERT INTO seasons(id,name,starts_on,ends_on) VALUES (1,'2026/27','2026-07-01','2027-06-30')"))
        c.execute(text("INSERT INTO teams(id,name) VALUES (1,'Synthetic club')"))
        c.execute(text("INSERT INTO competitions(id,season_id,internal_team_id,name,rules) VALUES (1,1,1,'Synthetic','{}')"))
        before = c.execute(text("SELECT id,season_id,internal_team_id,name,rules::text FROM competitions")).all()
    assert alembic(url, "upgrade", "0008").returncode == 0
    assert alembic(url, "check").returncode == 0
    with engine.begin() as c:
        assert c.execute(text("SELECT id,season_id,internal_team_id,name,rules::text FROM competitions")).all() == before
        assert c.execute(text("SELECT fpf_data FROM competitions")).scalar() is None
        c.execute(text("UPDATE competitions SET fpf_data='{}'"))
    assert alembic(url, "downgrade", "0007").returncode != 0
    with engine.connect() as c:
        assert c.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0008"
    engine.dispose()
