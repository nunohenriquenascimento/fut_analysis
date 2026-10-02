from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event, select
from sqlalchemy.exc import IntegrityError

from app import live_service
from app.enums import MatchStatus
from app.models import Match, MatchEvent, MatchSquad, Player, Team
from test_auth import accounts, password_hash, login  # noqa: F401
from test_matches import games, create, squad  # noqa: F401


def test_admin_delete_empty_preserves_other_entities(accounts):
    client, db, payload, ids, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    assert client.get(base).json()["can_delete"] is True
    assert client.delete(base).status_code == 204
    assert db.get(Match, match['id']) is None
    assert db.get(Team, match['opponent_id']) is not None
    assert db.get(Player, ids[0]) is not None
    assert client.get(base).status_code == 404
    assert client.get("/matches").json() == []
    assert client.delete(base).status_code == 404
    assert client.post(base + "/cancel").status_code == 404


@pytest.mark.parametrize("role", ["COACH", "VIEWER"])
def test_management_forbidden_and_flags_false(accounts, role):
    client, db, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    login(client, role)
    detail = client.get(base).json()
    assert detail["can_delete"] is False and detail["can_cancel"] is False
    assert client.delete(base, headers={"X-Role": "ADMIN"}).status_code == 403
    assert client.post(base + "/cancel", headers={"X-Role": "ADMIN"}).status_code == 403
    assert db.get(Match, match['id']).status == MatchStatus.SCHEDULED


@pytest.mark.parametrize("dependency", ["squad", "event", "elapsed", "clock"])
def test_delete_revalidates_history_after_eligibility(accounts, dependency):
    client, db, payload, ids, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    assert client.get(base).json()["can_delete"] is True
    if dependency == "squad":
        assert client.put(base + "/squad", json=squad((ids[0], True))).status_code == 200
    elif dependency == "event":
        db.add(MatchEvent(match_id=match['id'], event_type="CORNER", team="OPPONENT", period=1, elapsed_seconds=0))
    elif dependency == "elapsed":
        db.get(Match, match['id']).elapsed_seconds = 1
    else:
        db.get(Match, match['id']).clock_started_at = datetime.now(timezone.utc)
    db.commit()
    assert client.get(base).json()["can_delete"] is False
    assert client.delete(base).status_code == 409
    assert db.get(Match, match['id']) is not None


@pytest.mark.parametrize("status", ["FIRST_HALF", "HALF_TIME", "SECOND_HALF", "FINISHED", "CANCELLED"])
def test_delete_blocks_every_non_scheduled_state(accounts, status):
    client, db, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    db.get(Match, match['id']).status = MatchStatus(status)
    db.commit()
    assert client.delete(f"/matches/{match['id']}").status_code == 409


@pytest.mark.parametrize("status", ["SCHEDULED", "FIRST_HALF", "HALF_TIME", "SECOND_HALF", "FINISHED"])
def test_cancel_preserves_history_freezes_clock_and_statistics(accounts, monkeypatch, status):
    client, db, payload, ids, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    assert client.put(base + "/squad", json=squad((ids[0], True))).status_code == 200
    instant = datetime(2026, 10, 4, 15, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(live_service, "utcnow", lambda: instant)
    stored = db.get(Match, match['id'])
    stored.status = MatchStatus(status)
    stored.elapsed_seconds = 60
    stored.clock_started_at = instant - timedelta(seconds=17) if status in {"FIRST_HALF", "SECOND_HALF"} else None
    db.add(MatchEvent(match_id=match['id'], event_type="GOAL", team="US", player_id=ids[0], period=1, elapsed_seconds=10))
    db.commit()
    before_events = client.get(base + "/events").json()
    before_squad = client.get(base + "/squad").json()
    before_stats = client.get("/statistics/season").json()
    response = client.post(base + "/cancel")
    assert response.status_code == 200, response.text
    detail = response.json()
    assert detail["status"] == "CANCELLED" and detail["score"] == {"us": 1, "opponent": 0}
    assert detail["clock_started_at"] is None
    assert detail["elapsed_seconds"] == (77 if status in {"FIRST_HALF", "SECOND_HALF"} else 60)
    assert not detail["can_delete"] and not detail["can_cancel"]
    assert client.get(base + "/events").json() == before_events
    assert client.get(base + "/squad").json() == before_squad
    assert client.get(base + "/stats").json()["score"] == detail["score"]
    assert client.get("/matches").json()[0]["status"] == "CANCELLED"
    stats = client.get("/statistics/season").json()
    assert stats["competitive"] == {"matches": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0}
    for key in ("total_matches", "total_events", "matches_with_events", "comparison", "players", "rankings"):
        assert stats[key] == before_stats[key]
    assert client.post(base + "/cancel").status_code == 409
    assert client.delete(base).status_code == 409
    assert client.patch(base, json={"status": "SCHEDULED"}).status_code == 422
    assert client.post(base + "/transition", json={"status": "FIRST_HALF"}).status_code == 409
    monkeypatch.setattr(live_service, "utcnow", lambda: instant + timedelta(hours=1))
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == detail["elapsed_seconds"]


@pytest.mark.parametrize("operation", ["delete", "cancel"])
def test_management_requires_csrf_and_session(accounts, operation):
    client, _, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    send = lambda **kwargs: client.delete(base, **kwargs) if operation == "delete" else client.post(base + "/cancel", **kwargs)
    assert send(headers={"X-CSRF-Token": "forged"}).status_code == 403
    assert client.post("/auth/logout").status_code == 204
    assert send().status_code == 401


@pytest.mark.parametrize("operation", ["delete", "cancel"])
def test_management_integrity_failure_rolls_back(accounts, operation):
    client, db, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    def fail(*args):
        raise IntegrityError("test", {}, Exception("conflict"))
    event.listen(db, "before_flush", fail, once=True)
    response = client.delete(base) if operation == "delete" else client.post(base + "/cancel")
    assert response.status_code == 409
    assert client.get(base).json()["status"] == "SCHEDULED"


def test_cancel_inconsistent_running_clock_is_atomic(accounts):
    client, db, payload, _, _ = accounts
    login(client)
    match = create(client, payload)
    stored = db.get(Match, match['id']); stored.status = MatchStatus.FIRST_HALF
    db.commit()
    assert client.post(f"/matches/{match['id']}/cancel").status_code == 409
    assert stored.status == MatchStatus.FIRST_HALF
