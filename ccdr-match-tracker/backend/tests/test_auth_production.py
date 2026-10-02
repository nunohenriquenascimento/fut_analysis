import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.config import Settings, get_settings
from app import start
from test_auth import accounts, games, password_hash, login  # noqa: F401
from test_auth_live_socket import sockets  # noqa: F401


def settings(**values):
    return Settings(_env_file=None, database_url="postgresql://user:placeholder@postgres.railway.internal:5432/railway",
                    app_env="production", auth_cookie_secure=True, auth_cookie_samesite="none",
                    cors_origins=["https://club.vercel.app"], **values)


def test_railway_database_normalizes_driver_and_keeps_options():
    config = Settings(_env_file=None, database_url="postgres://user:placeholder@db:5432/railway?sslmode=require")
    url = make_url(config.database_url.get_secret_value())
    assert url.drivername == 'postgresql+psycopg'
    assert url.query['sslmode'] == 'require'
    assert 'placeholder' not in str(config)


def test_production_accepts_cross_site_and_same_site():
    assert settings().auth_cookie_samesite == 'none'
    config = Settings(_env_file=None, database_url="postgresql://db/railway", app_env="production",
                      auth_cookie_secure=True, auth_cookie_samesite="lax", cors_origins=["https://app.club.pt"])
    assert config.auth_cookie_samesite == 'lax'


@pytest.mark.parametrize('overrides', [
    {'auth_cookie_secure': False}, {'auth_cookie_samesite': 'invalid'},
    {'cors_origins': ['*']}, {'cors_origins': ['https://*.vercel.app']},
    {'cors_origins': ['http://club.vercel.app']}, {'cors_origins': ['https://localhost']},
    {'cors_origins': ['https://club.vercel.app/']}, {'cors_origins': ['https://club.vercel.app/path']},
    {'cors_origins': []}, {'database_url': 'sqlite:///db'},
])
def test_production_rejects_unsafe_configuration(overrides):
    values = dict(database_url='postgresql://db/railway', app_env='production', auth_cookie_secure=True,
                  auth_cookie_samesite='none', cors_origins=['https://club.vercel.app'])
    values.update(overrides)
    with pytest.raises(ValidationError): Settings(_env_file=None, **values)


def test_none_always_requires_secure_and_production_explicit_origins(monkeypatch):
    for name in ['CORS_ORIGINS', 'AUTH_COOKIE_SAMESITE', 'AUTH_COOKIE_SECURE', 'APP_ENV']:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url='postgresql://db/railway', auth_cookie_samesite='none')
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url='postgresql://db/railway', app_env='production', auth_cookie_secure=True)


def test_start_uses_railway_port_one_worker_and_no_forwarded_identity(monkeypatch):
    monkeypatch.setenv('PORT', '43210')
    monkeypatch.setenv('WEB_CONCURRENCY', '8')
    calls = []
    monkeypatch.setattr(start.uvicorn, 'run', lambda *args, **kwargs: calls.append((args, kwargs)))
    start.main()
    assert calls == [(('app.main:app',), dict(host='0.0.0.0', port=43210, workers=1, proxy_headers=False))]


@pytest.mark.parametrize('port', ['abc', '0', '65536'])
def test_start_rejects_invalid_port(monkeypatch, port):
    monkeypatch.setenv('PORT', port)
    with pytest.raises(SystemExit): start.main()


def test_secure_cross_site_cookie_csrf_origin_and_logout(accounts, monkeypatch):
    from app.auth import cookie_name
    client, _, _, _, _ = accounts
    production_origin = 'https://club.vercel.app'
    config = get_settings()
    monkeypatch.setattr(config, 'auth_cookie_secure', True)
    monkeypatch.setattr(config, 'auth_cookie_samesite', 'none')
    monkeypatch.setattr(config, 'cors_origins', [production_origin])
    client.base_url = 'https://backend.up.railway.app'
    client.headers['Origin'] = production_origin
    response = login(client)
    cookie = response.headers['set-cookie']
    assert '__Host-ccdr_session=' in cookie and 'Secure' in cookie and 'HttpOnly' in cookie
    assert 'SameSite=none' in cookie and 'Domain=' not in cookie
    assert client.get('/auth/me').status_code == 200
    assert client.post('/auth/logout', headers={'X-CSRF-Token': 'forged'}).status_code == 403
    assert client.post('/auth/logout', headers={'Origin': 'https://evil.vercel.app'}).status_code == 403
    response = client.post('/auth/logout')
    assert response.status_code == 204
    assert 'SameSite=none' in response.headers['set-cookie'] and 'Max-Age=0' in response.headers['set-cookie']
    assert client.cookies.get(cookie_name()) is None
    assert client.get('/auth/me').status_code == 401


def test_production_cors_preflight_allows_only_explicit_frontend():
    from fastapi.testclient import TestClient
    from fastapi.middleware.cors import CORSMiddleware
    from app.main import app
    origin = 'https://club.vercel.app'
    wrapped = CORSMiddleware(app, allow_origins=[origin], allow_credentials=True,
                             allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
                             allow_headers=['Content-Type', 'X-CSRF-Token', 'X-Requested-With'])
    with TestClient(wrapped) as client:
        headers = {'Origin': origin, 'Access-Control-Request-Method': 'POST',
                   'Access-Control-Request-Headers': 'content-type,x-csrf-token,x-requested-with'}
        response = client.options('/auth/login', headers=headers)
        assert response.status_code == 200
        assert response.headers['access-control-allow-origin'] == origin
        assert response.headers['access-control-allow-credentials'] == 'true'
        headers['Origin'] = 'https://evil.vercel.app'
        response = client.options('/auth/login', headers=headers)
        assert response.status_code == 400
        assert 'access-control-allow-origin' not in response.headers
        assert client.get('/health').json() == {'status': 'ok'}


def test_production_websocket_secure_cookie_and_exact_origin(sockets, monkeypatch):
    from starlette.websockets import WebSocketDisconnect
    from app.auth import cookie_name
    client, _, ids, _, tokens, _ = sockets
    config = get_settings()
    monkeypatch.setattr(config, 'auth_cookie_secure', True)
    monkeypatch.setattr(config, 'auth_cookie_samesite', 'none')
    monkeypatch.setattr(config, 'cors_origins', ['https://club.vercel.app'])
    headers = {'Origin': 'https://club.vercel.app', 'Cookie': f'{cookie_name()}={tokens["VIEWER"]}'}
    with client.websocket_connect(f'wss://backend.up.railway.app/ws/matches/{ids[0]}/live', headers=headers) as socket:
        assert socket.receive_json()['type'] == 'live.snapshot'
    headers['Origin'] = 'https://evil.vercel.app'
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f'wss://backend.up.railway.app/ws/matches/{ids[0]}/live', headers=headers): pass
    assert exc.value.code == 4403
