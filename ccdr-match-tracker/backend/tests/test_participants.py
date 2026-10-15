import pytest
from sqlalchemy import select

from app.models import CompetitionTeam, Team
from test_competitions import competition, fixture, send  # noqa: F401
from test_matches import games, create  # noqa: F401


def selection(ids, proposed=None):
    return dict(team_ids=proposed or ids, expected_team_ids=ids)


def preview(client, cid, body):
    return client.post(f"/competitions/{cid}/teams/preview", json=body)


def apply(client, cid, body):
    return client.put(f"/competitions/{cid}/teams", json={**body, "confirmation": "ALTERAR PARTICIPANTES"})


def members(db, cid):
    return set(db.scalars(select(CompetitionTeam.team_id).where(CompetitionTeam.competition_id == cid)))


def test_preview_confirmation_add_remove_preserves_teams(competition):
    client, db, _, ids, cid = competition
    extra = client.post("/teams", json={"name": "Novo participante"}).json()["id"]
    body = selection(ids, ids + [extra])
    response = preview(client, cid, body)
    assert response.status_code == 200, response.text
    assert response.json()["can_apply"] and response.json()["added"] == [{"id": extra, "name": "Novo participante"}]
    assert members(db, cid) == set(ids)
    assert client.put(f"/competitions/{cid}/teams", json=body).status_code == 422
    assert client.put(f"/competitions/{cid}/teams", json={**body, "confirmation": "SIM"}).status_code == 422
    assert apply(client, cid, body).status_code == 200
    assert members(db, cid) == set(ids + [extra])
    assert apply(client, cid, selection(ids + [extra], ids)).status_code == 200
    assert members(db, cid) == set(ids)
    assert db.get(Team, extra) is not None


@pytest.mark.parametrize("goals", [dict(), dict(home_goals=2, away_goals=1)])
def test_scheduled_or_finished_external_game_blocks_removal(competition, goals):
    client, db, _, ids, cid = competition
    assert send(client, cid, fixture(ids[1], ids[2], **goals)).status_code == 200
    body = selection(ids, [ids[0], ids[2], ids[3]])
    response = preview(client, cid, body)
    assert response.status_code == 200 and not response.json()["can_apply"]
    assert apply(client, cid, body).status_code == 409
    assert members(db, cid) == set(ids)
    assert len(client.get(f"/competitions/{cid}/calendar").json()) == 1


def test_unlinked_internal_game_blocks_removal_without_altering_it(competition):
    client, db, payload, ids, cid = competition
    match = create(client, {**payload, "opponent_name": "Adversário A"})
    before = client.get(f"/matches/{match['id']}").json()
    body = selection(ids, [ids[0], ids[2], ids[3]])
    assert not preview(client, cid, body).json()["can_apply"]
    assert apply(client, cid, body).status_code == 409
    assert members(db, cid) == set(ids)
    assert client.get(f"/matches/{match['id']}").json() == before


def test_preview_is_revalidated_when_a_game_is_imported_after_review(competition):
    client, db, _, ids, cid = competition
    body = selection(ids, ids[:3])
    assert preview(client, cid, body).json()["can_apply"]
    assert send(client, cid, fixture(ids[2], ids[3])).status_code == 200
    assert apply(client, cid, body).status_code == 409
    assert members(db, cid) == set(ids)


def test_stale_members_duplicate_missing_team_and_own_team_protection(competition):
    client, db, _, ids, cid = competition
    extra = client.post("/teams", json={"name": "Mais uma equipa"}).json()["id"]
    assert apply(client, cid, selection(ids, ids + [extra])).status_code == 200
    assert preview(client, cid, selection(ids)).status_code == 409
    assert apply(client, cid, selection(ids)).status_code == 409
    current = ids + [extra]
    assert preview(client, cid, selection(current, current + [extra])).status_code == 422
    assert preview(client, cid, selection(current, ids + [2147483647])).status_code == 404
    assert not preview(client, cid, selection(current, ids[1:])).json()["can_apply"]
    assert apply(client, cid, selection(current, ids[1:])).status_code == 409
    assert members(db, cid) == set(current)
