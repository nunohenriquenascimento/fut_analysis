from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import secrets

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app import live_socket
from app.auth import cookie_name, digest, now
from app.database import get_db
from app.main import app
from app.models import AuthSession, Match, MatchEvent, Player, Season, Team, User
from test_auth import password_hash  # noqa: F401

ORIGIN = "http://localhost:3000"


@pytest.fixture
def sockets(migrated_database_url, password_hash, monkeypatch):
    engine = create_engine(migrated_database_url)
    with Session(engine) as db:
        season = Season(name="Socket test", starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
        team, opponent = Team(name="Socket club"), Team(name="Socket opponent")
        db.add_all([season, team, opponent]); db.flush()
        player = Player(name="Socket scorer", season_id=season.id, team_id=team.id, position="MC", shirt_number=8)
        db.add(player)
        matches = [Match(season_id=season.id, team_id=team.id, opponent_id=opponent.id,
                         kickoff_at=now(), status="SCHEDULED", matchday=index + 1) for index in range(2)]
        db.add_all(matches)
        tokens, headers, users = {}, {}, {}
        for role in ("ADMIN", "COACH", "VIEWER"):
            user = User(name=role, email=f"socket-{role.lower()}@test.local", password_hash=password_hash, role=role, is_active=True)
            db.add(user); db.flush(); users[role] = user.id
            token = secrets.token_urlsafe(32); tokens[role] = token
            db.add(AuthSession(token_hash=digest(token), user_id=user.id, csrf_token="socket-csrf", expires_at=now() + timedelta(hours=8)))
            headers[role] = {"Origin": ORIGIN, "Cookie": f"{cookie_name()}={token}", "X-CSRF-Token": "socket-csrf"}
        db.commit()
        ids = [match.id for match in matches]
        shared_ids = season.id, team.id, opponent.id, player.id

    def database():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = database
    monkeypatch.setattr(live_socket, "get_engine", lambda: engine)
    monkeypatch.setattr(live_socket, "CHECK_INTERVAL", .1)
    try:
        with TestClient(app) as client:
            yield client, engine, ids, users, tokens, headers
    finally:
        app.dependency_overrides.clear()
        with Session(engine) as db:
            from app.models import MatchSquad
            db.execute(delete(MatchEvent).where(MatchEvent.match_id.in_(ids)))
            db.execute(delete(MatchSquad).where(MatchSquad.match_id.in_(ids)))
            db.execute(delete(Match).where(Match.id.in_(ids)))
            db.execute(delete(AuthSession).where(AuthSession.user_id.in_(users.values())))
            db.execute(delete(User).where(User.id.in_(users.values())))
            db.execute(delete(Player).where(Player.id == shared_ids[3]))
            db.execute(delete(Team).where(Team.id.in_(shared_ids[1:3])))
            db.execute(delete(Season).where(Season.id == shared_ids[0])); db.commit()
        engine.dispose()


def update(socket):
    # Idle validation heartbeats do not contain clock updates.
    for _ in range(30):
        message = socket.receive_json()
        if message['type'] != 'live.ping': return message
    raise AssertionError("No notification")


@pytest.mark.parametrize("role", ["ADMIN", "COACH", "VIEWER"])
def test_authenticated_snapshot(sockets, role):
    client, _, ids, _, _, headers = sockets
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers[role]) as socket:
        message = update(socket)
        assert message['type'] == 'live.snapshot' and message['version'] == 1
        assert message['match_id'] == ids[0]
        assert message['data']['match']['status'] == 'SCHEDULED'
        assert message['data']['events'] == [] and message['data']['score'] == {'us': 0, 'opponent': 0}
        assert 'clock_elapsed_seconds' in message['data']


@pytest.mark.parametrize("reason,code", [("missing", 4401), ("inactive", 4401), ("expired", 4401), ("origin", 4403), ("missing_match", 4404), ("revoked", 4401)])
def test_socket_rejects_invalid_identity_origin_or_game(sockets, reason, code):
    client, engine, ids, users, tokens, headers = sockets
    request_headers = dict(headers['ADMIN']); match_id = ids[0]
    with Session(engine) as db:
        if reason == 'missing': request_headers.pop('Cookie')
        elif reason == 'origin': request_headers['Origin'] = 'https://evil.example'
        elif reason == 'missing_match': match_id = 2147483647
        elif reason == 'inactive': db.get(User, users['ADMIN']).is_active = False
        elif reason == 'expired': db.get(AuthSession, digest(tokens['ADMIN'])).expires_at = now() - timedelta(seconds=1)
        else: db.execute(delete(AuthSession).where(AuthSession.user_id == users['ADMIN']))
        db.commit()
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/ws/matches/{match_id}/live?role=ADMIN&user_id=1", headers=request_headers): pass
    assert exc.value.code == code


def test_two_clients_all_live_writes_and_viewer_permissions(sockets):
    client, _, ids, users, _, headers = sockets
    base = f"/matches/{ids[0]}"
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['COACH']) as coach, client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['VIEWER']) as viewer:
        update(coach); update(viewer)
        operations = [
            ('POST', base + '/transition', {'status': 'FIRST_HALF'}, 'live.state_changed'),
            ('POST', base + '/events', {'event_type': 'CORNER', 'team': 'OPPONENT'}, 'live.event_created'),
        ]
        for method, path, body, kind in operations:
            response = client.request(method, path, json=body, headers=headers['COACH'])
            assert response.status_code in (200, 201)
            for socket in (coach, viewer):
                message = update(socket)
                assert message['type'] == kind and message['actor_id'] == users['COACH']
                assert message['data'] == {} # No email/token exposed.
        event_id = response.json()['events'][0]['id']
        assert client.patch(base + f'/events/{event_id}', json={'notes': 'Corrected'}, headers=headers['COACH']).status_code == 200
        assert update(coach)['type'] == update(viewer)['type'] == 'live.event_updated'
        assert client.delete(base + f'/events/{event_id}', headers=headers['COACH']).status_code == 200
        assert update(coach)['type'] == update(viewer)['type'] == 'live.event_deleted'
        assert client.post(base + '/transition', json={'status': 'HALF_TIME'}, headers=headers['COACH']).status_code == 200
        assert update(coach)['type'] == update(viewer)['type'] == 'live.state_changed'
        assert client.post(base + '/transition', json={'status': 'SECOND_HALF'}, headers=headers['COACH']).status_code == 200
        assert update(coach)['type'] == update(viewer)['type'] == 'live.state_changed'
        assert client.post(base + '/events', json={'event_type': 'CORNER', 'team': 'OPPONENT'}, headers=headers['VIEWER']).status_code == 403
        assert client.post(base + '/transition', json={'status': 'FINISHED'}, headers=headers['VIEWER']).status_code == 403
        assert client.post(base + '/cancel', headers=headers['ADMIN']).status_code == 200
        assert update(coach)['type'] == update(viewer)['type'] == 'live.cancelled'


def test_games_isolated_and_failures_not_published(sockets):
    client, _, ids, _, _, headers = sockets
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['ADMIN']) as first, client.websocket_connect(f"/ws/matches/{ids[1]}/live", headers=headers['ADMIN']) as second:
        update(first); update(second)
        assert client.post(f"/matches/{ids[0]}/transition", json={'status': 'FIRST_HALF'}, headers=headers['ADMIN']).status_code == 200
        assert update(first)['type'] == 'live.state_changed'
        assert second.receive_json()['type'] == 'live.ping'
        assert client.post(f"/matches/{ids[0]}/transition", json={'status': 'FIRST_HALF'}, headers=headers['ADMIN']).status_code == 409
        assert first.receive_json()['type'] == 'live.ping'


def test_logout_closes_existing_socket_and_rejects_reconnect(sockets):
    client, _, ids, _, _, headers = sockets
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['ADMIN']) as socket:
        update(socket)
        assert client.post('/auth/logout', headers=headers['ADMIN']).status_code == 204
        with pytest.raises(WebSocketDisconnect) as exc:
            while True: socket.receive_json()
        assert exc.value.code == 4401
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['ADMIN']): pass


def test_socket_cannot_execute_mutations(sockets):
    client, _, ids, _, _, headers = sockets
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['ADMIN']) as socket:
        update(socket)
        socket.send_json({'type': 'transition', 'status': 'FIRST_HALF'})
        with pytest.raises(WebSocketDisconnect) as exc:
            while True: socket.receive_json()
        assert exc.value.code == 1008
    assert client.get(f"/matches/{ids[0]}/live", headers=headers['ADMIN']).json()['match']['status'] == 'SCHEDULED'


def test_concurrent_editors_keep_both_events_and_notify(sockets):
    client, _, ids, users, _, headers = sockets
    base = f"/matches/{ids[0]}"
    assert client.post(base + '/transition', json={'status': 'FIRST_HALF'}, headers=headers['COACH']).status_code == 200
    with client.websocket_connect(f"/ws/matches/{ids[0]}/live", headers=headers['VIEWER']) as socket:
        update(socket)
        def create(role):
            return client.post(base + '/events', json={'event_type': 'GOAL', 'team': 'OPPONENT'}, headers=headers[role])
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(create, ['ADMIN', 'COACH']))
        assert all(response.status_code == 201 for response in responses)
        notifications = [update(socket), update(socket)]
        assert all(message['type'] == 'live.event_created' for message in notifications)
        assert {message['actor_id'] for message in notifications} == {users['ADMIN'], users['COACH']}
        current = client.get(base + '/live', headers=headers['VIEWER']).json()
        assert current['score'] == {'us': 0, 'opponent': 2}
        assert len({event['id'] for event in current['events']}) == 2


def test_notification_failure_does_not_rollback_committed_http_write(sockets, monkeypatch):
    client, _, ids, _, _, headers = sockets
    async def unavailable(*args):
        raise RuntimeError('Notification transport unavailable')
    monkeypatch.setattr(live_socket.hub, 'publish', unavailable)
    base = f"/matches/{ids[0]}"
    assert client.post(base + '/transition', json={'status': 'FIRST_HALF'}, headers=headers['COACH']).status_code == 200
    assert client.post(base + '/events', json={'event_type': 'GOAL', 'team': 'OPPONENT'}, headers=headers['COACH']).status_code == 201
    assert client.get(base + '/live', headers=headers['VIEWER']).json()['score']['opponent'] == 1


def finish_game(client, base, headers):
    for status in ['FIRST_HALF', 'HALF_TIME', 'SECOND_HALF', 'FINISHED']:
        assert client.post(base + '/transition', json={'status': status}, headers=headers).status_code == 200


@pytest.mark.parametrize('role', ['ADMIN', 'COACH', 'VIEWER'])
def test_reopen_resume_permissions_and_two_socket_notifications(sockets, role):
    client, _, ids, users, _, headers = sockets
    base = f'/matches/{ids[0]}'
    finish_game(client, base, headers['COACH'])
    if role == 'VIEWER':
        assert client.post(base + '/reopen', headers=headers[role]).status_code == 403
        assert client.post(base + '/resume', headers=headers[role]).status_code == 403
        assert client.get(base + '/live', headers=headers[role]).json()['match']['status'] == 'FINISHED'
        return
    with client.websocket_connect(f'/ws/matches/{ids[0]}/live', headers=headers['COACH']) as coach, client.websocket_connect(f'/ws/matches/{ids[0]}/live', headers=headers['VIEWER']) as viewer:
        assert update(coach)['data']['match']['status'] == 'FINISHED'
        assert update(viewer)['data']['match']['status'] == 'FINISHED'
        response = client.post(base + '/reopen', headers=headers[role])
        assert response.status_code == 200
        for socket in [coach, viewer]:
            message = update(socket)
            assert message['type'] == 'live.state_changed' and message['actor_id'] == users[role]
        current = client.get(base + '/live', headers=headers['VIEWER']).json()
        assert current['match']['status'] == 'SECOND_HALF' and current['match']['clock_started_at'] is None
        assert client.post(base + '/resume', headers=headers[role]).status_code == 200
        for socket in [coach, viewer]:
            assert update(socket)['type'] == 'live.state_changed'


def test_concurrent_reopen_only_one_succeeds(sockets):
    client, _, ids, _, _, headers = sockets
    base = f'/matches/{ids[0]}'
    finish_game(client, base, headers['ADMIN'])
    before = client.get(base + '/live', headers=headers['VIEWER']).json()
    from threading import Barrier
    barrier = Barrier(2)

    def reopen(role):
        barrier.wait(timeout=10)
        return client.post(base + '/reopen', headers=headers[role])

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(reopen, ['ADMIN', 'COACH']))
    assert sorted(response.status_code for response in responses) == [200, 409]
    current = client.get(base + '/live', headers=headers['VIEWER']).json()
    assert current['match']['status'] == 'SECOND_HALF'
    assert current['match']['clock_started_at'] is None
    assert current['clock_elapsed_seconds'] == before['clock_elapsed_seconds']
    assert current['events'] == before['events'] and current['score'] == before['score']
