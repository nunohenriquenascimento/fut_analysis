"""Exercise the actual Alembic CLI and PostgreSQL enum conversion with legacy data."""
import pytest
from sqlalchemy import create_engine, text

from conftest import alembic


@pytest.mark.parametrize("new_position", ["ALA", "MDC", "UNIVERSAL"])
def test_upgrade_preserves_rows_and_downgrade_is_atomic(postgres_schema, new_position):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0001").returncode == 0
    engine = create_engine(url)
    with engine.begin() as db:
        db.execute(text("INSERT INTO seasons (id,name,starts_on,ends_on) VALUES (17,'2026/27','2026-07-01','2027-06-30')"))
        db.execute(text("INSERT INTO teams (id,name) VALUES (23,'Legacy club')"))
        for index, position in enumerate(["GOALKEEPER", "DEFENDER", "MIDFIELDER", "FORWARD"], 1):
            db.execute(text("INSERT INTO players (id,season_id,team_id,name,position,shirt_number,is_active) VALUES (:id,17,23,:name,:position,:number,:active)"),
                       {"id": index, "name": f"Legacy {index}", "position": position,
                        "number": index if index != 4 else None, "active": index != 2})
        original = db.execute(text("SELECT id,season_id,team_id,name,shirt_number,is_active,created_at FROM players ORDER BY id")).all()
    result = alembic(url, "upgrade", "head")
    assert result.returncode == 0, result.stderr
    with engine.connect() as db:
        assert db.execute(text("SELECT id,season_id,team_id,name,shirt_number,is_active,created_at FROM players ORDER BY id")).all() == original
        assert db.execute(text("SELECT position::text FROM players ORDER BY id")).scalars().all() == ["GR", "DC", "MC", "PL"]
        assert db.execute(text("SELECT enum_range(NULL::player_position)::text")).scalar() == "{GR,DC,ALA,MDC,MC,PL,UNIVERSAL}"
    result = alembic(url, "check")
    assert result.returncode == 0, result.stdout + result.stderr
    # Later revisions are validated above, then isolate the 0002 rollback.
    assert alembic(url, "downgrade", "0002").returncode == 0
    with engine.begin() as db:
        db.execute(text("UPDATE players SET position=:position WHERE id=1"), {"position": new_position})
    result = alembic(url, "downgrade", "0001")
    assert result.returncode != 0
    assert "manual reassignment" in result.stderr
    with engine.begin() as db:
        assert db.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"
        assert db.execute(text("SELECT position::text FROM players WHERE id=1")).scalar() == new_position
        assert db.execute(text("SELECT count(*) FROM players")).scalar() == 4
        db.execute(text("UPDATE players SET position='GR' WHERE id=1"))
    result = alembic(url, "downgrade", "0001")
    assert result.returncode == 0, result.stderr
    with engine.connect() as db:
        assert db.execute(text("SELECT position::text FROM players ORDER BY id")).scalars().all() == ["GOALKEEPER", "DEFENDER", "MIDFIELDER", "FORWARD"]
        assert db.execute(text("SELECT id,season_id,team_id,name,shirt_number,is_active,created_at FROM players ORDER BY id")).all() == original
    assert alembic(url, "upgrade", "head").returncode == 0
    engine.dispose()
