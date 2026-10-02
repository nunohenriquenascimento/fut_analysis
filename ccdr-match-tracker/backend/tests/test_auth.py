from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app.auth import cookie_name, digest, hash_password, now, verify_password
from app.auth_schemas import UserCreate
from app.create_admin import bootstrap
from app.enums import UserRole
from app.models import AuthSession, MatchEvent, User
from test_matches import games, create, squad  # noqa: F401

PASSWORD = "Test-password-2026!"
ORIGIN = "http://localhost:3000"


@pytest.fixture(scope="session")
def password_hash():
    return hash_password(PASSWORD)


@pytest.fixture
def accounts(games, password_hash):
    client, db, payload, ids = games
    rows = {}
    for role in UserRole:
        user = User(name=role.value, email=f"{role.value.lower()}@test.local", role=role, is_active=True, password_hash=password_hash)
        db.add(user)
        rows[role.value] = user
    db.commit()
    client.headers.update({"Origin": ORIGIN, "X-Requested-With": "CCDR"})
    return client, db, payload, ids, rows


def login(client, role="ADMIN"):
    response = client.post("/auth/login", json={"email": f"{role.lower()}@test.local", "password": PASSWORD})
    assert response.status_code == 200, response.text
    client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return response


def test_hash_login_cookie_me_logout_and_replay(accounts):
    client, db, _, _, _ = accounts
    response = login(client)
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Max-Age=28800" in cookie
    token = client.cookies.get(cookie_name())
    stored = db.get(AuthSession, digest(token))
    assert stored is not None and stored.token_hash != token
    assert "password" not in response.text and "password_hash" not in client.get("/users").text
    assert client.get("/auth/me").json()["user"]["role"] == "ADMIN"
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401
    client.cookies.set(cookie_name(), token)
    assert client.get("/players").status_code == 401


def test_password_hash_is_salted_and_verified(password_hash):
    assert password_hash != hash_password(PASSWORD)
    assert PASSWORD not in password_hash
    assert verify_password(PASSWORD, password_hash)
    assert not verify_password("wrong", password_hash)
    assert not verify_password(PASSWORD, None)


@pytest.mark.parametrize("path", ["/players", "/players/context", "/teams", "/matches", "/matches/1", "/matches/1/squad", "/matches/1/live", "/matches/1/events", "/matches/1/stats", "/statistics/season", "/statistics/players", "/users", "/auth/me"])
def test_every_read_requires_real_session(accounts, path):
    client, _, _, _, _ = accounts
    assert client.get(path, headers={"X-Role": "ADMIN", "X-User-Id": "1"}).status_code == 401


@pytest.mark.parametrize("role", ["COACH", "VIEWER"])
def test_users_are_admin_only(accounts, role):
    client, _, _, _, users = accounts
    login(client, role)
    assert client.get("/users").status_code == 403
    assert client.post("/users", json={"name": "Fake", "email": "fake@test.local", "password": PASSWORD}).status_code == 403
    assert client.patch(f"/users/{users['ADMIN'].id}", json={"role": "VIEWER"}).status_code == 403


@pytest.mark.parametrize("method,path,body", [
    ("POST", "/players", {}), ("PATCH", "/players/1", {}), ("PATCH", "/teams/1", {}),
    ("POST", "/matches", {}), ("PATCH", "/matches/1", {}), ("PUT", "/matches/1/squad", {}),
    ("POST", "/matches/1/transition", {}), ("POST", "/matches/1/events", {}),
    ("PATCH", "/matches/1/events/1", {}), ("DELETE", "/matches/1/events/1", None),
])
def test_viewer_cannot_mutate_even_with_forged_role(accounts, method, path, body):
    client, _, _, _, _ = accounts
    login(client, "VIEWER")
    assert client.request(method, path, json=body, headers={"X-Role": "ADMIN"}).status_code == 403


@pytest.mark.parametrize("role", ["ADMIN", "COACH"])
def test_editors_create_matches_and_events_with_real_author(accounts, role):
    client, db, payload, ids, users = accounts
    login(client, role)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    assert client.put(base + "/squad", json=squad((ids[0], True))).status_code == 200
    assert client.post(base + "/transition", json={"status": "FIRST_HALF"}).status_code == 200
    assert client.post(base + "/events", json={"event_type": "GOAL", "team": "US", "player_id": ids[0], "recorded_by_id": users['VIEWER'].id}).status_code == 422
    response = client.post(base + "/events", json={"event_type": "GOAL", "team": "US", "player_id": ids[0]})
    assert response.status_code == 201
    event = response.json()["events"][0]
    assert event["recorded_by_id"] == users[role].id
    assert db.get(MatchEvent, event["id"]).recorded_by_id == users[role].id
    assert client.patch(base + f"/events/{event['id']}", json={"notes": "Correção"}).status_code == 200
    assert db.get(MatchEvent, event["id"]).recorded_by_id == users[role].id


def test_csrf_and_login_origin_protection(accounts):
    client, _, payload, _, _ = accounts
    assert client.post("/auth/login", json={"email": "admin@test.local", "password": PASSWORD}, headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.post("/auth/login", json={"email": "admin@test.local", "password": PASSWORD}, headers={"X-Requested-With": ""}).status_code == 403
    login(client)
    for headers in [{"X-CSRF-Token": ""}, {"X-CSRF-Token": "forged"}, {"Origin": "https://evil.example"}]:
        assert client.post("/matches", json=payload, headers=headers).status_code == 403
    assert client.post("/auth/logout", headers={"X-CSRF-Token": ""}).status_code == 403
    assert client.get("/auth/me").status_code == 200


def test_expiry_disabled_accounts_rotation_and_password_reset(accounts):
    client, db, _, _, users = accounts
    login(client, "COACH")
    old = client.cookies.get(cookie_name())
    login(client, "COACH")
    assert client.cookies.get(cookie_name()) != old
    assert db.get(AuthSession, digest(old)) is None
    session = db.get(AuthSession, digest(client.cookies.get(cookie_name())))
    session.expires_at = now() - timedelta(seconds=1)
    db.commit()
    assert client.get("/auth/me").status_code == 401
    login(client, "COACH")
    coach_token = client.cookies.get(cookie_name())
    login(client)
    assert client.patch(f"/users/{users['COACH'].id}", json={"password": "Replacement-password!"}).status_code == 200
    assert db.get(AuthSession, digest(coach_token)) is None
    assert client.patch(f"/users/{users['COACH'].id}", json={"is_active": False}).status_code == 200
    assert client.post("/auth/login", json={"email": "coach@test.local", "password": "Replacement-password!"}).status_code == 401


def test_users_last_admin_email_duplicates_and_bootstrap(accounts):
    client, db, _, _, users = accounts
    login(client)
    for body in [{"is_active": False}, {"role": "COACH"}, {"role": "VIEWER", "is_active": False}]:
        assert client.patch(f"/users/{users['ADMIN'].id}", json=body).status_code == 409
        assert users['ADMIN'].role == UserRole.ADMIN and users['ADMIN'].is_active
    assert client.patch("/users/2147483647", json={"name": "Missing"}).status_code == 404
    data = {"name": "Second Admin", "email": "Second@Test.Local", "password": PASSWORD, "role": "ADMIN"}
    response = client.post("/users", json=data)
    assert response.status_code == 201 and response.json()["email"] == "second@test.local"
    assert client.post("/users", json=data).status_code == 409
    assert client.patch(f"/users/{users['COACH'].id}", json={"email": "SECOND@test.local"}).status_code == 409
    assert client.patch(f"/users/{users['ADMIN'].id}", json={"name": "Changed"}).status_code == 200
    assert client.get("/auth/me").status_code == 200
    with pytest.raises(ValueError):
        bootstrap(db, UserCreate(**data))
    db.rollback()
    assert client.patch(f"/users/{users['ADMIN'].id}", json={"role": "COACH"}).status_code == 200
    assert client.get("/auth/me").status_code == 401


def test_login_throttle_and_no_password_in_validation(accounts):
    client, _, _, _, _ = accounts
    for _ in range(10):
        response = client.post("/auth/login", json={"email": "absent@test.local", "password": "wrong"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Email ou password inválidos."}
    response = client.post("/auth/login", json={"email": "absent@test.local", "password": "wrong"})
    assert response.status_code == 429 and response.headers["retry-after"] == "900"
    secret = "NeverEchoThisPassword!"
    response = client.post("/auth/login", json={"email": "admin@test.local", "password": secret, "role": "ADMIN"})
    assert response.status_code == 422 and secret not in response.text


def test_bootstrap_first_admin_and_legacy_no_login(games):
    client, db, _, _ = games
    client.headers.update({"Origin": ORIGIN, "X-Requested-With": "CCDR"})
    legacy = User(name="Legacy", email="legacy@test.local", role=UserRole.ADMIN, is_active=True)
    db.add(legacy); db.commit()
    assert client.post("/auth/login", json={"email": legacy.email, "password": PASSWORD}).status_code == 401
    payload = UserCreate(name="First Admin", email=legacy.email, password=PASSWORD)
    bootstrap(db, payload); db.commit()
    assert client.post("/auth/login", json={"email": legacy.email, "password": PASSWORD}).status_code == 200
    with pytest.raises(ValueError):
        bootstrap(db, payload)
    db.rollback()


def test_https_cookie_and_forged_token(accounts, monkeypatch):
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "auth_cookie_secure", True)
    client, db, _, _, _ = accounts
    response = login(client)
    assert "__Host-ccdr_session=" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"] and "Domain=" not in response.headers["set-cookie"]
    # TestClient uses HTTP, so it correctly does not send a Secure cookie.
    assert client.get("/auth/me").status_code == 401
    assert db.scalar(select(func.count()).select_from(AuthSession)) == 1
    client.cookies.set(cookie_name(), "x" * 43)
    assert client.get("/auth/me").status_code == 401


def test_concurrent_demotions_keep_one_active_admin(migrated_database_url, password_hash):
    from concurrent.futures import ThreadPoolExecutor
    from fastapi.testclient import TestClient
    import secrets
    from sqlalchemy import create_engine, delete
    from sqlalchemy.orm import Session
    from app.database import get_db
    from app.main import app

    engine = create_engine(migrated_database_url)
    ids, tokens = [], []
    with Session(engine) as db:
        for index in range(2):
            user = User(name=f"Concurrent {index}", email=f"concurrent-{index}@test.local", role=UserRole.ADMIN,
                        is_active=True, password_hash=password_hash)
            db.add(user); db.flush(); ids.append(user.id)
            token = secrets.token_urlsafe(32); tokens.append(token)
            db.add(AuthSession(token_hash=digest(token), user_id=user.id, csrf_token="concurrent-csrf", expires_at=now() + timedelta(hours=8)))
        db.commit()

    def database():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = database
    try:
        def demote(index):
            with TestClient(app) as client:
                return client.patch(f"/users/{ids[index]}", json={"role": "COACH"}, headers={
                    "Origin": ORIGIN, "X-CSRF-Token": "concurrent-csrf", "Cookie": f"{cookie_name()}={tokens[index]}",
                }).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(demote, range(2))) == [200, 409]
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(User).where(User.id.in_(ids), User.role == UserRole.ADMIN, User.is_active.is_(True))) == 1
    finally:
        app.dependency_overrides.clear()
        with Session(engine) as db:
            db.execute(delete(AuthSession).where(AuthSession.user_id.in_(ids)))
            db.execute(delete(User).where(User.id.in_(ids)))
            db.commit()
        engine.dispose()
