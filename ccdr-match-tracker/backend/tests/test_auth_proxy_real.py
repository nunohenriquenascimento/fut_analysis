"""Optional real Caddy integration; set CADDY_BIN to run, no cloud services."""
import json
import os
from pathlib import Path
import socket
import subprocess
from threading import Thread
import time

import httpx
import pytest
import uvicorn
from starlette.responses import PlainTextResponse
from websockets.sync.client import connect

from app.config import get_settings
from app.main import app
from test_auth_live_socket import sockets, password_hash  # noqa: F401
from test_auth import PASSWORD


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def test_real_caddy_http_cookie_and_websocket_upgrade(sockets, monkeypatch, tmp_path):
    binary = os.environ.get('CADDY_BIN')
    if not binary: pytest.skip('Set CADDY_BIN for real proxy integration')
    _, _, ids, users, _, _ = sockets
    origin = 'https://club.up.railway.app'
    config = get_settings()
    monkeypatch.setattr(config, 'auth_cookie_secure', True)
    monkeypatch.setattr(config, 'auth_cookie_samesite', 'lax')
    monkeypatch.setattr(config, 'cors_origins', [origin])
    api_port, next_port, proxy_port = free_port(), free_port(), free_port()
    async def frontend(scope, receive, send):
        await PlainTextResponse('next-upstream')(scope, receive, send)
    api = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=api_port, root_path='/api',
                                     proxy_headers=True, forwarded_allow_ips='127.0.0.1', log_level='error'))
    next_server = uvicorn.Server(uvicorn.Config(frontend, host='127.0.0.1', port=next_port, lifespan='off', log_level='error'))
    threads = [Thread(target=server.run, daemon=True) for server in (api, next_server)]
    process = None
    try:
        for thread in threads: thread.start()
        source = Path(__file__).resolve().parents[2] / 'deploy/Caddyfile'
        caddyfile = tmp_path / 'Caddyfile'
        caddyfile.write_text(source.read_text().replace('127.0.0.1:8000', f'127.0.0.1:{api_port}')
                            .replace('127.0.0.1:3000', f'127.0.0.1:{next_port}'))
        process = subprocess.Popen([binary, 'run', '--config', str(caddyfile), '--adapter', 'caddyfile'],
                                   env={**os.environ, 'PORT': str(proxy_port)}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        with httpx.Client(base_url=f'http://127.0.0.1:{proxy_port}', headers={'Origin': origin, 'X-Requested-With': 'CCDR'}) as client:
            deadline = time.monotonic() + 10
            while True:
                try:
                    if client.get('/health').status_code == 200: break
                except httpx.TransportError: pass
                assert time.monotonic() < deadline, 'Proxy startup timed out'
                time.sleep(.1)
            assert client.get('/login').text == 'next-upstream'
            assert client.get('/matches/31/live').text == 'next-upstream'
            assert client.get('/api/health').json() == {'status': 'ok'}
            response = client.post('/api/auth/login', json={'email': 'socket-coach@test.local', 'password': PASSWORD})
            assert response.status_code == 200
            assert 'Secure' in response.headers['set-cookie'] and 'SameSite=lax' in response.headers['set-cookie']
            # Simulate Railway's outer HTTPS edge: local Caddy transport is HTTP.
            cookie = '__Host-ccdr_session=' + client.cookies.get('__Host-ccdr_session')
            client.headers['Cookie'] = cookie
            client.headers['X-CSRF-Token'] = response.json()['csrf_token']
            assert client.get('/api/auth/me').status_code == 200
            assert client.post(f'/api/matches/{ids[0]}/transition', json={'status': 'FIRST_HALF'}).status_code == 200
            with connect(f'ws://127.0.0.1:{proxy_port}/ws/matches/{ids[0]}/live', origin=origin,
                         additional_headers={'Cookie': cookie}, open_timeout=5) as ws:
                assert json.loads(ws.recv(timeout=5))['type'] == 'live.snapshot'
                response = client.post(f'/api/matches/{ids[0]}/events', json={'event_type': 'GOAL', 'team': 'OPPONENT'})
                assert response.status_code == 201
                deadline = time.monotonic() + 5
                while True:
                    remaining = deadline - time.monotonic()
                    assert remaining > 0, 'Event notification timed out'
                    message = json.loads(ws.recv(timeout=remaining))
                    if message['type'] != 'live.ping':
                        break
                    ws.send('pong')
                assert message['type'] == 'live.event_created' and message['actor_id'] == users['COACH']
            assert client.post('/api/auth/logout').status_code == 204
            assert client.get('/api/auth/me').status_code == 401
    finally:
        if process:
            process.terminate(); process.wait(timeout=5)
        api.should_exit = next_server.should_exit = True
        for thread in threads:
            if thread.ident: thread.join(timeout=5)
