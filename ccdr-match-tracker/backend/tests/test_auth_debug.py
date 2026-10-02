from datetime import timedelta
import json

import pytest

from app import auth_debug
from app.auth import cookie_name, digest, now
from app.config import get_settings
from app.models import AuthSession
from test_auth import accounts, games, password_hash, login, PASSWORD  # noqa: F401


@pytest.fixture
def debug(monkeypatch, caplog):
    monkeypatch.setattr(get_settings(), 'auth_debug_logging', True)
    auth_debug._revoked.clear()
    caplog.set_level('INFO', logger=auth_debug.logger.name)
    yield caplog
    auth_debug._revoked.clear()


def logs(caplog):
    return [json.loads(row.message) for row in caplog.records if row.name == auth_debug.logger.name]


def final(caplog):
    return [row for row in logs(caplog) if row['phase'] == 'response'][-1]


def test_disabled_has_no_detailed_logs_or_header(accounts, monkeypatch, caplog):
    monkeypatch.setattr(get_settings(), 'auth_debug_logging', False)
    caplog.set_level('INFO', logger=auth_debug.logger.name)
    client, _, _, _, _ = accounts
    assert 'x-request-id' not in login(client).headers
    assert client.get('/auth/me').status_code == 200
    assert logs(caplog) == []


def test_success_logs_cookie_attributes_and_no_secrets(accounts, debug):
    client, db, _, _, _ = accounts
    client.headers['User-Agent'] = 'Mobile Safari SECRET-UA'
    client.headers['Authorization'] = 'Bearer SECRET-AUTHORIZATION'
    client.headers['X-Request-ID'] = 'SECRET-REQUEST-ID'
    response = login(client)
    token = client.cookies.get(cookie_name())
    stored = db.get(AuthSession, digest(token))
    assert stored is not None
    row = final(debug)
    assert row['credentials_valid'] and row['session_created'] and row['status'] == 200
    assert row['cookie_httponly'] and row['cookie_domain'] == '<host-only>'
    assert row['cookie_max_age_present'] and not row['cookie_expires_present']
    assert row['set_cookie_header_present'] and row['user_agent'] == 'Mobile Safari'
    assert row['request_id'] == response.headers['x-request-id']
    assert response.headers['access-control-expose-headers'] == 'X-Request-ID'
    assert client.get('/auth/me').status_code == 200
    assert final(debug)['session_found'] and final(debug)['user_active']
    joined = json.dumps(logs(debug))
    for secret in [PASSWORD, token, digest(token), stored.csrf_token, stored.token_hash,
                   'SECRET-UA', 'SECRET-AUTHORIZATION', 'SECRET-REQUEST-ID', get_settings().database_url.get_secret_value()]:
        assert secret not in joined


@pytest.mark.parametrize('case,reason', [('missing', 'session_cookie_missing'), ('unknown', 'session_not_found'),
                                     ('expired', 'session_expired'), ('revoked', 'session_revoked'), ('inactive', 'user_inactive')])
def test_me_internal_reasons_keep_public_response_generic(accounts, debug, case, reason):
    client, db, _, _, users = accounts
    if case != 'missing':
        login(client)
        token = client.cookies.get(cookie_name())
        if case == 'unknown': client.cookies.set(cookie_name(), 'x' * 43)
        elif case == 'expired':
            db.get(AuthSession, digest(token)).expires_at = now() - timedelta(seconds=1); db.commit()
        elif case == 'revoked':
            assert client.post('/auth/logout').status_code == 204
            client.cookies.set(cookie_name(), token)
        elif case == 'inactive': users['ADMIN'].is_active = False; db.commit()
    response = client.get('/auth/me')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Sessão inexistente ou expirada.'
    row = final(debug)
    assert row['reason'] == reason and row['status'] == 401
    assert row['session_cookie_present'] == (case != 'missing')


def test_origin_rejected_and_unknown_cookie_names_are_not_echoed(accounts, debug):
    client, _, _, _, _ = accounts
    client.cookies.set('SECRET-AS-NAME', 'SECRET-AS-VALUE')
    client.headers['Origin'] = 'https://evil.example'
    response = client.post('/auth/login', json={'email': 'admin@test.local', 'password': PASSWORD})
    assert response.status_code == 403
    row = final(debug)
    assert not row['origin_allowed'] and not row['origin_validation_passed']
    assert row['reason'] == 'origin_not_allowed' and row['other_cookie_count'] == 1
    assert 'SECRET-AS-' not in json.dumps(logs(debug))


def test_revocation_cache_is_bounded_and_not_an_auth_source(debug):
    auth_debug.remember_revoked([f'hash-{index}' for index in range(1030)])
    assert len(auth_debug._revoked) == 1024
    assert not auth_debug.known_revoked('hash-0')
    assert auth_debug.known_revoked('hash-1029')
