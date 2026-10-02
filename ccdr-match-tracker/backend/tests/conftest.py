"""PostgreSQL tests use disposable schemas, never the application's tables."""
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

BACKEND = Path(__file__).resolve().parents[1]


def alembic(url, *args):
    return subprocess.run(
        [sys.executable, "-m", "alembic", *args], cwd=BACKEND,
        env={**os.environ, "DATABASE_URL": url}, capture_output=True, text=True,
    )


@pytest.fixture(scope="session")
def postgres_schema():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to PostgreSQL with CREATE schema permission")
    engine = create_engine(url)
    schemas = []

    def create():
        schema = "roster_test_" + uuid4().hex
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        schemas.append(schema)
        return make_url(url).update_query_dict({"options": f"-csearch_path={schema}"}).render_as_string(hide_password=False)

    yield create
    with engine.begin() as connection:
        for schema in schemas:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    engine.dispose()


@pytest.fixture(scope="session")
def migrated_database_url(postgres_schema):
    url = postgres_schema()
    result = alembic(url, "upgrade", "head")
    assert result.returncode == 0, result.stderr
    return url
