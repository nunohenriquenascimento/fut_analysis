import pytest
from datetime import datetime, timezone
from sqlalchemy import event, select
from sqlalchemy.exc import IntegrityError

from app.models import Match, MatchEvent, MatchSquad, Player, Season, Team, User
from app.enums import MatchStatus
from test_auth import accounts, password_hash, login  # noqa: F401
from test_matches import games, create, squad  # noqa: F401

CONFIRM = {"confirmation": "ELIMINAR"}


@pytest.mark.parametrize("status,history", [
    ("SCHEDULED", "squad"), ("SCHEDULED", "events"), ("SCHEDULED", "empty"),
    ("FIRST_HALF", "both"), ("HALF_TIME", "both"), ("SECOND_HALF", "both"),
    ("FINISHED", "both"), ("CANCELLED", "both"),
])
def test_force_deletes_only_target_and_statistics(accounts, status, history):
    client, db, payload, ids, users = accounts
    login(client)
    target, other = create(client, payload), create(client, {**payload, "matchday": 4})
    stored = db.get(Match, target['id'])
    stored.status = MatchStatus(status)
    stored.elapsed_seconds = 90 if status != "SCHEDULED" else 0
    stored.clock_started_at = datetime.now(timezone.utc) if status in {"FIRST_HALF", "SECOND_HALF"} else None
    db.get(Match, other['id']).status = MatchStatus.FINISHED
    if history in {"squad", "both"}:
        db.add(MatchSquad(match_id=target['id'], player_id=ids[0], is_starter=True))
    if history in {"events", "both"}:
        db.add(MatchEvent(match_id=target['id'], event_type="GOAL", team="US", player_id=ids[0], recorded_by_id=users['ADMIN'].id, period=1, elapsed_seconds=30))
    db.add(MatchSquad(match_id=other['id'], player_id=ids[0], is_starter=True))
    db.add(MatchEvent(match_id=other['id'], event_type="GOAL", team="US", player_id=ids[0], recorded_by_id=users['ADMIN'].id, period=1, elapsed_seconds=30))
    db.commit()
    other_detail = client.get(f"/matches/{other['id']}").json()
    other_squad = client.get(f"/matches/{other['id']}/squad").json()
    other_events = client.get(f"/matches/{other['id']}/events").json()
    shared = {model: [row.id for row in db.scalars(select(model))] for model in (Player, Team, Season, User)}
    if history != "empty" or status != "SCHEDULED":
        assert client.delete(f"/matches/{target['id']}").status_code == 409
    response = client.request("DELETE", f"/matches/{target['id']}/force", json=CONFIRM)
    assert response.status_code == 204, response.text
    assert db.get(Match, target['id']) is None
    assert db.scalar(select(MatchEvent.id).where(MatchEvent.match_id == target['id'])) is None
    assert db.scalar(select(MatchSquad.id).where(MatchSquad.match_id == target['id'])) is None
    for model, before in shared.items():
        assert [row.id for row in db.scalars(select(model))] == before
    assert client.get(f"/matches/{other['id']}").json() == other_detail
    assert client.get(f"/matches/{other['id']}/squad").json() == other_squad
    assert client.get(f"/matches/{other['id']}/events").json() == other_events
    assert client.get(f"/matches/{target['id']}/stats").status_code == 404
    stats = client.get("/statistics/season").json()
    assert stats['total_matches'] == 1 and stats['total_events'] == 1
    assert stats['competitive']['matches'] == 1 and stats['competitive']['wins'] == 1
    assert stats['competitive']['goals_for'] == 1
    player = next(row for row in stats['players'] if row['player']['id'] == ids[0])
    assert player['goals'] == 1 and player['matches_called_up'] == 1 and player['matches_started'] == 1
    assert stats['rankings']['goals'][0]['value'] == 1


@pytest.mark.parametrize("role", ["COACH", "VIEWER"])
def test_force_forbidden(accounts, role):
    client, db, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    login(client, role)
    assert client.request("DELETE", f"/matches/{match['id']}/force", json=CONFIRM, headers={"X-Role": "ADMIN"}).status_code == 403
    assert db.get(Match, match['id']) is not None


def test_force_404_confirmation_and_csrf(accounts):
    client, db, payload, _, _ = accounts
    login(client)
    assert client.request("DELETE", "/matches/2147483647/force", json=CONFIRM).status_code == 404
    match = create(client, payload)
    path = f"/matches/{match['id']}/force"
    for body in [{}, {"confirmation": "yes"}, {"confirmation": "ELIMINAR", "role": "ADMIN"}]:
        assert client.request("DELETE", path, json=body).status_code == 422
    assert client.request("DELETE", path, json=CONFIRM, headers={"X-CSRF-Token": ""}).status_code == 403
    assert db.get(Match, match['id']) is not None
    assert client.post("/auth/logout").status_code == 204
    assert client.request("DELETE", path, json=CONFIRM).status_code == 401


@pytest.mark.parametrize("failure", ["integrity", "runtime"])
def test_force_rollback_restores_all_deleted_dependencies(accounts, failure):
    client, db, payload, ids, _ = accounts
    login(client)
    match = create(client, payload)
    db.add(MatchSquad(match_id=match['id'], player_id=ids[0], is_starter=True))
    db.add(MatchEvent(match_id=match['id'], event_type="CORNER", team="OPPONENT", period=1, elapsed_seconds=30))
    db.commit()
    def fail(*args):
        # The final ORM flush happens after both dependent DELETE statements.
        if failure == "integrity": raise IntegrityError("test", {}, Exception("dependent FK"))
        raise RuntimeError("test rollback")
    event.listen(db, "before_flush", fail, once=True)
    if failure == "integrity":
        assert client.request("DELETE", f"/matches/{match['id']}/force", json=CONFIRM).status_code == 409
    else:
        with pytest.raises(RuntimeError):
            client.request("DELETE", f"/matches/{match['id']}/force", json=CONFIRM)
    assert db.get(Match, match['id']) is not None
    assert db.scalar(select(MatchSquad.id).where(MatchSquad.match_id == match['id'])) is not None
    assert db.scalar(select(MatchEvent.id).where(MatchEvent.match_id == match['id'])) is not None
