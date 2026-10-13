from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy.orm import Session

from app.models import Match, MatchEvent
from test_auth_live_socket import sockets, password_hash, update  # noqa: F401


def setup_merge(sockets):
    client, engine, ids, _, _, headers = sockets
    with Session(engine) as db:
        for match_id, seconds in zip(ids, [3780, 900]):
            match = db.get(Match, match_id)
            match.status = "FINISHED"
            match.elapsed_seconds = seconds
        db.add(MatchEvent(match_id=ids[1], event_type="GOAL", team="OPPONENT", period=1, elapsed_seconds=270))
        db.commit()
    selection = {"principal_id": ids[0], "continuation_id": ids[1], "final_status": "FINISHED"}
    response = client.post("/matches/merge/preview", json=selection, headers=headers["ADMIN"])
    assert response.status_code == 200, response.text
    return {**selection, "preview_token": response.json()["preview_token"], "confirmation": "UNIR JOGOS"}


@pytest.mark.parametrize("role", ["ADMIN", "COACH", "VIEWER"])
def test_merge_permissions(sockets, role):
    payload = setup_merge(sockets)
    client, _, ids, _, _, headers = sockets
    response = client.post("/matches/merge/preview", json={key: payload[key] for key in ["principal_id", "continuation_id", "final_status"]}, headers=headers[role])
    assert response.status_code == (200 if role == "ADMIN" else 403)
    response = client.post("/matches/merge", json=payload, headers=headers[role])
    assert response.status_code == (200 if role == "ADMIN" else 403)
    if role != "ADMIN":
        assert client.get(f"/matches/{ids[1]}/live", headers=headers[role]).status_code == 200


def test_merge_requires_session_origin_csrf(sockets):
    payload = setup_merge(sockets)
    client, _, _, _, _, headers = sockets
    assert client.post("/matches/merge", json=payload).status_code == 401
    assert client.post("/matches/merge", json=payload, headers={**headers["ADMIN"], "Origin": "https://untrusted.example"}).status_code == 403
    assert client.post("/matches/merge", json=payload, headers={**headers["ADMIN"], "X-CSRF-Token": "invalid"}).status_code == 403


def test_concurrent_merge_one_commit_and_two_live_clients(sockets):
    payload = setup_merge(sockets)
    client, _, ids, users, _, headers = sockets
    path = f"/ws/matches/{ids[0]}/live"
    with client.websocket_connect(path, headers=headers["COACH"]) as coach, client.websocket_connect(path, headers=headers["VIEWER"]) as viewer:
        update(coach); update(viewer)
        barrier = Barrier(2)
        def merge(_):
            barrier.wait(timeout=10)
            return client.post("/matches/merge", json=payload, headers=headers["ADMIN"])
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(merge, [1, 2]))
        assert sorted(row.status_code for row in responses) == [200, 404]
        for socket in [coach, viewer]:
            message = update(socket)
            assert message["type"] == "live.state_changed" and message["actor_id"] == users["ADMIN"]
        state = client.get(f"/matches/{ids[0]}/live", headers=headers["VIEWER"]).json()
        assert state["score"] == {"us": 0, "opponent": 1}
        assert state["clock_elapsed_seconds"] == 4680
        assert len(state["events"]) == 1 and state["events"][0]["elapsed_seconds"] == 4050


def test_reverse_order_merge_preview_cannot_overwrite_first_commit(sockets):
    payload = setup_merge(sockets)
    client, _, _, _, _, headers = sockets
    reverse = {"principal_id": payload["continuation_id"], "continuation_id": payload["principal_id"], "final_status": "FINISHED"}
    reverse_preview = client.post("/matches/merge/preview", json=reverse, headers=headers["ADMIN"]).json()
    barrier = Barrier(2)
    def merge(body):
        barrier.wait(timeout=10)
        return client.post("/matches/merge", json=body, headers=headers["ADMIN"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(merge, [payload, {**reverse, "preview_token": reverse_preview["preview_token"], "confirmation": "UNIR JOGOS"}]))
    assert sorted(row.status_code for row in responses) == [200, 404]
