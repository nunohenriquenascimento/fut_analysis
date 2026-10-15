from sqlalchemy import create_engine, text

from app.migration_audit import snapshot
from conftest import alembic


def test_audit_verifies_0007_preservation_and_detects_changed_rows(postgres_schema):
    url = postgres_schema()
    assert alembic(url, "upgrade", "0006").returncode == 0
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO teams (name) VALUES ('Equipa sintética')"))
        before = snapshot(engine)
        assert before["version"] == "0006"
        assert before["tables"]["teams"]["rows"] == 1
        result = alembic(url, "upgrade", "0007")
        assert result.returncode == 0, result.stderr
        after = snapshot(engine)
        assert after["version"] == "0007"
        assert after["tables"] == before["tables"]
        with engine.begin() as connection:
            connection.execute(text("UPDATE teams SET name='Alteração sintética'"))
        changed = snapshot(engine)
        assert changed["tables"]["teams"]["rows"] == before["tables"]["teams"]["rows"]
        assert changed["tables"]["teams"]["sha256"] != before["tables"]["teams"]["sha256"]
    finally:
        engine.dispose()
