from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, event
from sqlalchemy.exc import IntegrityError

from app import live_service
from app.models import Match, MatchEvent, MatchSquad
from app.enums import MatchStatus
from test_matches import games, create, squad  # noqa: F401 -- shared isolated PostgreSQL fixture


@pytest.fixture
def live_game(games, monkeypatch):
    client, db, payload, ids = games
    match = create(client, payload)
    base = f"/matches/{match['id']}"
    assert client.put(base + "/squad", json=squad((ids[0], True), (ids[1], False))).status_code == 200
    now = [datetime(2026, 10, 4, 14, 0, tzinfo=timezone.utc)]
    monkeypatch.setattr(live_service, "utcnow", lambda: now[0])
    return client, db, base, ids, now


def start(client, base):
    response = client.post(base + "/transition", json={"status": "FIRST_HALF"})
    assert response.status_code == 200, response.text


def post(client, base, **fields):
    response = client.post(base + "/events", json={"event_type": "CORNER", "team": "OPPONENT", **fields})
    assert response.status_code == 201, response.text
    return response.json()


def test_transitions_clock_and_refresh(live_game):
    client, _, base, _, now = live_game
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == 0
    assert client.post(base + "/transition", json={"status": "SECOND_HALF"}).status_code == 409
    start(client, base)
    assert client.post(base + "/transition", json={"status": "FIRST_HALF"}).status_code == 409
    now[0] += timedelta(seconds=123)
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == 123
    state = client.post(base + "/transition", json={"status": "HALF_TIME"}).json()
    assert state["match"]["elapsed_seconds"] == 123 and state["match"]["clock_started_at"] is None
    now[0] += timedelta(minutes=15)
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == 123
    assert client.post(base + "/transition", json={"status": "SECOND_HALF"}).status_code == 200
    now[0] += timedelta(seconds=42)
    state = post(client, base)
    assert state["events"][0]["period"] == 2 and state["events"][0]["elapsed_seconds"] == 165
    state = client.post(base + "/transition", json={"status": "FINISHED"}).json()
    assert state["clock_elapsed_seconds"] == 165
    now[0] += timedelta(hours=2)
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == 165
    assert client.post(base + "/transition", json={"status": "FIRST_HALF"}).status_code == 409


def test_events_score_edit_delete_and_order(live_game):
    client, db, base, ids, now = live_game
    start(client, base)
    now[0] += timedelta(seconds=65)
    state = post(client, base, event_type="GOAL", team="US", player_id=ids[0], related_player_id=ids[1])
    goal = state["events"][0]
    assert goal["period"] == 1 and goal["elapsed_seconds"] == 65
    assert state["score"] == {"us": 1, "opponent": 0}
    post(client, base, event_type="GOAL")
    post(client, base, event_type="OWN_GOAL", team="US", player_id=ids[0])
    state = post(client, base, event_type="OWN_GOAL")
    assert state["score"] == {"us": 2, "opponent": 2}
    assert len(state["events"]) == 4  # No automatically duplicated shot.
    assert client.get(base).json()["score"] == state["score"]
    assert client.get(base + "/events").json() == state["events"]
    assert [row["id"] for row in state["events"]] == sorted(row["id"] for row in state["events"])
    now[0] += timedelta(seconds=20)
    response = client.patch(base + f"/events/{goal['id']}", json={"event_type": "SHOT_ON_TARGET", "related_player_id": None})
    assert response.status_code == 200
    edited = response.json()["events"][0]
    assert edited["elapsed_seconds"] == 65 and edited["period"] == 1
    assert response.json()["score"] == {"us": 1, "opponent": 2}
    own = response.json()["events"][-1]
    response = client.delete(base + f"/events/{own['id']}")
    assert response.status_code == 200 and response.json()["score"] == {"us": 0, "opponent": 2}
    assert db.get(MatchEvent, own["id"]) is None


@pytest.mark.parametrize("event_type", ["GOAL", "OWN_GOAL", "SHOT_ON_TARGET", "SHOT_OFF_TARGET", "SHOT_BLOCKED", "CORNER", "FREE_KICK", "FOUL", "YELLOW_CARD", "RED_CARD", "OFFSIDE", "SAVE", "PENALTY", "SUBSTITUTION"])
def test_supported_events_for_both_teams(live_game, event_type):
    client, _, base, ids, _ = live_game
    start(client, base)
    post(client, base, event_type=event_type)
    fields = {"player_id": ids[0], "related_player_id": ids[1]} if event_type == "SUBSTITUTION" else {"player_id": ids[0]}
    assert len(post(client, base, event_type=event_type, team="US", **fields)["events"]) == 2


@pytest.mark.parametrize("fields,status", [
    ({"player_id": 2147483647}, 404), ({"index": 2}, 409), ({"index": 4}, 409), ({"index": 5}, 409),
    ({"event_type": "GOAL", "player_id": None}, 409),
    ({"event_type": "GOAL", "assist_index": 2}, 409),
    ({"event_type": "GOAL", "related_player_id": 2147483647}, 404),
    ({"event_type": "SUBSTITUTION", "same_player": True}, 409),
    ({"event_type": "SUBSTITUTION"}, 409),
    ({"event_type": "SUBSTITUTION", "assist_index": 2}, 409),
    ({"event_type": "CORNER", "assist_index": 1}, 409),
    ({"team": "OPPONENT"}, 409), ({"event_type": "SHOT"}, 422),
    ({"elapsed_seconds": 500}, 422), ({"period": 2}, 422),
])
def test_invalid_events_leave_no_rows(live_game, fields, status):
    client, db, base, ids, _ = live_game
    start(client, base)
    values = {"team": "US", "event_type": "FOUL", "player_id": ids[0], **fields}
    if "index" in values:
        values["player_id"] = ids[values.pop("index")]
    if "assist_index" in values:
        values["related_player_id"] = ids[values.pop("assist_index")]
    if values.pop("same_player", False):
        values["related_player_id"] = ids[0]
    response = client.post(base + "/events", json=values)
    assert response.status_code == status, response.text
    assert db.scalar(select(MatchEvent.id)) is None


@pytest.mark.parametrize("status", ["SCHEDULED", "HALF_TIME", "FINISHED", "CANCELLED"])
def test_create_requires_running_half(live_game, status):
    client, db, base, _, _ = live_game
    match = db.get(Match, int(base.split("/")[-1]))
    match.status = MatchStatus(status)
    db.commit()
    assert client.post(base + "/events", json={"event_type": "CORNER", "team": "US"}).status_code == 409


def test_invalid_edit_is_atomic_and_event_membership_preserved(live_game):
    client, _, base, ids, _ = live_game
    start(client, base)
    goal = post(client, base, event_type="GOAL", team="US", player_id=ids[0])["events"][0]
    path = base + f"/events/{goal['id']}"
    before = client.get(base + "/events").json()
    assert client.patch(path, json={"team": "OPPONENT"}).status_code == 409
    assert client.patch(path, json={"elapsed_seconds": 999}).status_code == 422
    assert client.patch(path, json={}).status_code == 422
    assert client.get(base + "/events").json() == before
    assert client.put(base + "/squad", json=squad((ids[1], False))).status_code == 409
    assert client.patch(f"/players/{ids[0]}", json={"is_active": False}).status_code == 200
    assert client.patch(path, json={"notes": "Corrigido"}).status_code == 200
    client.post(base + "/transition", json={"status": "HALF_TIME"})
    client.post(base + "/transition", json={"status": "SECOND_HALF"})
    client.post(base + "/transition", json={"status": "FINISHED"})
    assert client.patch(path, json={"team": "OPPONENT", "player_id": None}).json()["score"] == {"us": 0, "opponent": 1}
    assert client.delete(path).json()["score"] == {"us": 0, "opponent": 0}


def test_missing_match_event_and_cors(live_game):
    client, _, base, _, _ = live_game
    assert client.get("/matches/2147483647/live").status_code == 404
    assert client.get("/matches/2147483647/events").status_code == 404
    assert client.post("/matches/2147483647/transition", json={"status": "FIRST_HALF"}).status_code == 404
    assert client.patch(base + "/events/2147483647", json={"notes": "X"}).status_code == 404
    assert client.delete(base + "/events/2147483647").status_code == 404
    response = client.options(base + "/events/1", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "DELETE"})
    assert response.status_code == 200 and "DELETE" in response.headers["access-control-allow-methods"]


@pytest.mark.parametrize("operation", ["transition", "event"])
def test_write_failure_rolls_back_live_changes(live_game, operation):
    client, db, base, _, _ = live_game
    if operation == "event":
        start(client, base)
    before = client.get(base + "/live").json()

    def fail_flush(*args):
        raise IntegrityError("injected failure", {}, Exception("test"))

    event.listen(db, "before_flush", fail_flush, once=True)
    try:
        path, body = ("/transition", {"status": "FIRST_HALF"}) if operation == "transition" else ("/events", {"event_type": "GOAL", "team": "OPPONENT"})
        assert client.post(base + path, json=body).status_code == 409
    finally:
        event.remove(db, "before_flush", fail_flush)
    assert client.get(base + "/live").json() == before


def test_event_cannot_be_changed_through_another_match(live_game):
    client, db, base, _, _ = live_game
    start(client, base)
    goal = post(client, base, event_type="GOAL")["events"][0]
    original = db.get(Match, int(base.split("/")[-1]))
    other = Match(season_id=original.season_id, team_id=original.team_id, opponent_id=original.opponent_id,
                  matchday=2, kickoff_at=original.kickoff_at)
    db.add(other)
    db.commit()
    path = f"/matches/{other.id}/events/{goal['id']}"
    assert client.patch(path, json={"event_type": "CORNER"}).status_code == 404
    assert client.delete(path).status_code == 404
    assert client.get(base).json()["score"] == {"us": 0, "opponent": 1}


def finish(client, base):
    start(client, base)
    for status in ["HALF_TIME", "SECOND_HALF", "FINISHED"]:
        assert client.post(base + "/transition", json={"status": status}).status_code == 200


def test_reopen_preserves_history_clock_and_statistics(live_game):
    client, db, base, ids, now = live_game
    start(client, base)
    now[0] += timedelta(seconds=2701)
    client.post(base + "/transition", json={"status": "HALF_TIME"})
    now[0] += timedelta(minutes=15)
    client.post(base + "/transition", json={"status": "SECOND_HALF"})
    now[0] += timedelta(seconds=1203)
    for kind in ["GOAL", "YELLOW_CARD", "SHOT_ON_TARGET", "SUBSTITUTION"]:
        post(client, base, event_type=kind, team="US", player_id=ids[0],
             related_player_id=ids[1] if kind == "SUBSTITUTION" else None)
    before = client.post(base + "/transition", json={"status": "FINISHED"}).json()
    squad_before = [(row.id, row.player_id, row.is_starter, row.created_at)
                    for row in db.scalars(select(MatchSquad))]
    stats_before = client.get(base + "/stats").json()
    season_before = client.get("/statistics/season").json()
    assert season_before["competitive"]["matches"] == 1
    now[0] += timedelta(hours=3)
    response = client.post(base + "/reopen")
    assert response.status_code == 200, response.text
    reopened = response.json()
    assert reopened["match"]["status"] == "SECOND_HALF"
    assert reopened["match"]["clock_started_at"] is None
    assert reopened["clock_elapsed_seconds"] == before["clock_elapsed_seconds"] == 3904
    assert reopened["events"] == before["events"]
    assert all(row["recorded_by_id"] is not None for row in reopened["events"])
    assert reopened["squad"] == before["squad"] and reopened["score"] == before["score"]
    assert [(row.id, row.player_id, row.is_starter, row.created_at)
            for row in db.scalars(select(MatchSquad))] == squad_before
    stats_after = client.get(base + "/stats").json()
    assert stats_after["is_final"] is False
    for key in ["timeline", "comparison", "score", "total_events"]:
        assert stats_after[key] == stats_before[key]
    season_after = client.get("/statistics/season").json()
    assert season_after["competitive"]["matches"] == 0
    for key in ["comparison", "players", "rankings", "total_events"]:
        assert season_after[key] == season_before[key]
    now[0] += timedelta(minutes=5)
    assert client.get(base + "/live").json()["clock_elapsed_seconds"] == 3904
    assert client.post(base + "/events", json={"event_type": "CORNER", "team": "US"}).status_code == 409
    assert client.post(base + "/resume").status_code == 200
    assert client.post(base + "/resume").status_code == 409
    now[0] += timedelta(seconds=37)
    state = post(client, base, event_type="GOAL", team="US", player_id=ids[0])
    assert state["events"][-1]["elapsed_seconds"] == 3941
    final = client.post(base + "/transition", json={"status": "FINISHED"}).json()
    assert final["clock_elapsed_seconds"] == 3941
    assert final["events"][:4] == before["events"]
    assert final["score"] == {"us": 2, "opponent": 0}
    assert client.get("/statistics/season").json()["competitive"]["goals_for"] == 2
    assert client.get("/statistics/season").json()["competitive"]["matches"] == 1


@pytest.mark.parametrize("status", ["SCHEDULED", "FIRST_HALF", "HALF_TIME", "SECOND_HALF", "CANCELLED"])
def test_reopen_rejects_other_states(live_game, status):
    client, db, base, _, now = live_game
    match = db.get(Match, int(base.split("/")[-1]))
    match.status = MatchStatus(status)
    match.clock_started_at = now[0] if status in {"FIRST_HALF", "SECOND_HALF"} else None
    db.commit()
    before = client.get(base + "/live").json()
    assert client.post(base + "/reopen").status_code == 409
    assert client.get(base + "/live").json() == before
    assert client.post(base + "/resume").status_code == 409


def test_reopen_missing_patch_bypass_and_rollback(live_game):
    client, db, base, _, _ = live_game
    finish(client, base)
    before = client.get(base + "/live").json()
    assert client.post("/matches/2147483647/reopen").status_code == 404
    assert client.post("/matches/2147483647/resume").status_code == 404
    assert client.patch(base, json={"status": "SECOND_HALF"}).status_code == 422
    assert client.post(base + "/transition", json={"status": "SECOND_HALF"}).status_code == 409

    def fail_flush(*args):
        raise IntegrityError("injected failure", {}, Exception("test"))

    event.listen(db, "before_flush", fail_flush, once=True)
    try:
        assert client.post(base + "/reopen").status_code == 409
    finally:
        event.remove(db, "before_flush", fail_flush)
    assert client.get(base + "/live").json() == before
    assert client.post(base + "/reopen").status_code == 200
    # Finishing again without resuming must also retain the frozen time.
    assert client.post(base + "/transition", json={"status": "FINISHED"}).status_code == 200
