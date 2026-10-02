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


@pytest.fixture(autouse=True)
def legacy_authorized_actor(request):
    """Existing business regressions exercise rules as ADMIN; auth tests use real sessions."""
    if request.path.name.startswith("test_auth"):
        yield
        return
    from typing import Annotated
    from fastapi import Depends
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    from app.auth import current_user
    from app.database import get_db
    from app.enums import UserRole
    from app.main import app
    from app.models import User

    def actor(db: Annotated[Session, Depends(get_db)]):
        if db is None:
            return User(id=1, name="Test admin", email="admin@test.local", role=UserRole.ADMIN, is_active=True)
        user = db.scalar(select(User).where(User.email == "admin@test.local"))
        if user is None:
            user = User(name="Test admin", email="admin@test.local", role=UserRole.ADMIN, is_active=True)
            db.add(user)
            db.commit()
        return user

    app.dependency_overrides[current_user] = actor
    yield
    app.dependency_overrides.pop(current_user, None)


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
