import pytest

from test_auth import accounts, password_hash, login  # noqa: F401
from test_matches import games  # noqa: F401


@pytest.mark.parametrize("path", ["/competitions", "/competitions/1/teams", "/competitions/1/calendar", "/competitions/1/matchdays", "/competitions/1/standings"])
def test_competition_reads_need_session(accounts, path):
    client, *_ = accounts
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("method,path,payload", [
    ("POST", "/teams", {"name": "Teste"}),
    ("POST", "/competitions", {}),
    ("PUT", "/competitions/1/rules", {}),
    ("POST", "/competitions/1/fixtures/import", {}),
])
def test_viewer_cannot_write(accounts, method, path, payload):
    client, *_ = accounts
    login(client, "VIEWER")
    assert client.request(method, path, json=payload).status_code == 403


def test_competition_write_needs_csrf_and_origin(accounts):
    client, *_ = accounts
    login(client)
    for headers in ({"X-CSRF-Token": ""}, {"Origin": "https://untrusted.example"}):
        assert client.post("/teams", json={"name": "Teste"}, headers=headers).status_code == 403


@pytest.mark.parametrize("role", ["ADMIN", "COACH"])
@pytest.mark.parametrize("name,duplicate", [
    ("Nova equipa", "  NOVA   EQUIPA "),
    ("Águias São João", "  ÁGUIAS\u00a0 SÃO\tJOÃO  "),
])
def test_editor_can_create_team(accounts, role, name, duplicate):
    client, *_ = accounts
    login(client, role)
    assert client.post("/teams", json={"name": name}).status_code == 201
    assert client.post("/teams", json={"name": duplicate}).status_code == 409


@pytest.mark.parametrize("role", ["COACH", "VIEWER"])
@pytest.mark.parametrize("method,path", [("POST", "/competitions/1/teams/preview"), ("PUT", "/competitions/1/teams")])
def test_posterior_membership_management_is_admin_only(accounts, role, method, path):
    client, *_ = accounts
    login(client, role)
    assert client.request(method, path, json={}).status_code == 403


def test_admin_membership_management_requires_csrf_and_origin(accounts):
    client, _, payload, _, _ = accounts
    login(client)
    other = client.post("/teams", json={"name": "Participante novo"}).json()["id"]
    ids = [payload["team_id"], other]
    created = client.post("/competitions", json=dict(name="Competição de permissões", season_id=payload["season_id"],
        internal_team_id=ids[0], team_ids=ids))
    assert created.status_code == 201
    cid = created.json()["id"]
    body = dict(team_ids=ids, expected_team_ids=ids)
    for headers in ({"X-CSRF-Token": ""}, {"Origin": "https://untrusted.example"}):
        assert client.post(f"/competitions/{cid}/teams/preview", json=body, headers=headers).status_code == 403
        assert client.put(f"/competitions/{cid}/teams", json={**body, "confirmation": "ALTERAR PARTICIPANTES"}, headers=headers).status_code == 403
    assert client.post(f"/competitions/{cid}/teams/preview", json=body).status_code == 200
    assert client.put(f"/competitions/{cid}/teams", json={**body, "confirmation": "ALTERAR PARTICIPANTES"}).status_code == 200
