"""Contract at the edge: prefix stripping plus Uvicorn's root_path semantics."""
from pathlib import Path
import importlib.util

import pytest
from fastapi.testclient import TestClient
from starlette.responses import PlainTextResponse
from starlette.websockets import WebSocketDisconnect

from app.config import get_settings
from app.main import app
from test_auth import accounts, games, password_hash, PASSWORD  # noqa: F401
from test_auth_live_socket import sockets  # noqa: F401

ORIGIN = 'https://club.up.railway.app'
PROJECT = Path(__file__).resolve().parents[2]


class ProxyContract:
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            return await app(scope, receive, send)
        path = scope['path']
        if path.startswith('/api/') or path.startswith('/ws/') or path == '/health':
            upstream = path[4:] if path.startswith('/api/') else path
            # Caddy forwards upstream without /api; Uvicorn prepends root_path in ASGI scope.
            forwarded = dict(scope, root_path='/api', path='/api' + upstream, raw_path=('/api' + upstream).encode())
            await app(forwarded, receive, send)
        else:
            await PlainTextResponse('next-frontend')(scope, receive, send)


@pytest.fixture
def same_origin(monkeypatch):
    config = get_settings()
    monkeypatch.setattr(config, 'auth_cookie_secure', True)
    monkeypatch.setattr(config, 'auth_cookie_samesite', 'lax')
    monkeypatch.setattr(config, 'cors_origins', [ORIGIN])


def test_login_cookie_me_csrf_logout_and_routing(accounts, same_origin, monkeypatch):
    monkeypatch.setattr(get_settings(), 'auth_debug_logging', True)
    with TestClient(ProxyContract(), base_url=ORIGIN, headers={'Origin': ORIGIN, 'X-Requested-With': 'CCDR'}) as client:
        assert client.get('/').text == 'next-frontend'
        assert client.get('/matches/31/live').text == 'next-frontend'
        assert client.get('/health').json() == {'status': 'ok'}
        assert client.get('/api/health').json() == {'status': 'ok'}
        response = client.post('/api/auth/login', json={'email': 'admin@test.local', 'password': PASSWORD})
        assert response.status_code == 200
        assert 'x-request-id' in response.headers
        cookie = response.headers['set-cookie']
        assert '__Host-ccdr_session=' in cookie and 'HttpOnly' in cookie and 'Secure' in cookie
        assert 'SameSite=lax' in cookie and 'Path=/' in cookie and 'Domain=' not in cookie
        assert client.get('/api/auth/me').status_code == 200
        assert client.post('/api/auth/logout').status_code == 403
        client.headers['X-CSRF-Token'] = response.json()['csrf_token']
        assert client.post('/api/auth/logout').status_code == 204
        assert client.get('/api/auth/me').status_code == 401
        response = client.post('/api/auth/login', json={'email': 'invalid', 'password': 'secret-not-in-response'})
        assert response.status_code == 422
        assert 'secret-not-in-response' not in response.text


def test_authenticated_same_origin_websocket_and_origin_rejection(sockets, same_origin):
    _, _, ids, _, tokens, _ = sockets
    with TestClient(ProxyContract(), base_url=ORIGIN) as client:
        # Browser cookie belongs to this same HTTPS host, not a separate API host.
        client.cookies.set('__Host-ccdr_session', tokens['VIEWER'], domain='club.up.railway.app', path='/')
        with client.websocket_connect(f'{ORIGIN.replace("https:", "wss:")}/ws/matches/{ids[0]}/live', headers={'Origin': ORIGIN}) as socket:
            assert socket.receive_json()['type'] == 'live.snapshot'
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect(f'{ORIGIN.replace("https:", "wss:")}/ws/matches/{ids[0]}/live', headers={'Origin': 'https://evil.example'}): pass
        assert exc.value.code == 4403


def test_proxy_config_keeps_ws_and_strips_api_without_cookie_rewriting():
    config = (PROJECT / 'deploy/Caddyfile').read_text()
    assert 'handle_path /api/*' in config and 'handle /ws/*' in config and 'handle /health' in config
    assert config.count('reverse_proxy 127.0.0.1:8000') == 3
    assert 'reverse_proxy 127.0.0.1:3000' in config
    assert 'header_down' not in config
    assert 'auto_https off' in config and ':{$PORT:8080}' in config


def test_supervisor_commands_reserve_internal_ports_and_one_worker(monkeypatch):
    spec = importlib.util.spec_from_file_location('combined_start', PROJECT / 'deploy/start.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    monkeypatch.setenv('PORT', '8080')
    assert module.public_port() == 8080
    command = module.commands()[0][0]
    assert command[command.index('--workers') + 1] == '1'
    assert command[command.index('--root-path') + 1] == '/api'
    assert command[command.index('--forwarded-allow-ips') + 1] == '127.0.0.1'
    for value in ['3000', '8000', 'bad', '0']:
        monkeypatch.setenv('PORT', value)
        with pytest.raises(ValueError): module.public_port()
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('AUTH_COOKIE_SAMESITE', 'none')
    with pytest.raises(ValueError, match='requires AUTH_COOKIE_SAMESITE=lax'): module.main()
