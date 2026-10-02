"""Opt-in diagnostics. Never serialize request bodies, headers or session identifiers."""
from collections import OrderedDict
from datetime import datetime, timezone
import json
import logging
from threading import Lock
from time import monotonic
from urllib.parse import urlsplit
from uuid import uuid4

from app.config import get_settings

logger = logging.getLogger('uvicorn.error.auth_debug')
_revoked = OrderedDict()
_lock = Lock()


def remember_revoked(hashes):
    if not get_settings().auth_debug_logging:
        return
    with _lock:
        for key in hashes:
            _revoked[key] = monotonic()
        while len(_revoked) > 1024:
            _revoked.popitem(last=False)


def known_revoked(key):
    with _lock:
        instant = _revoked.get(key)
        return instant is not None and monotonic() - instant < 86400


def origin_label(value):
    if not value:
        return None
    try:
        url = urlsplit(value)
        if url.scheme not in {'https', 'http'} or not url.hostname or url.username is not None or url.password is not None or url.path or url.query or url.fragment:
            return '<invalid>'
        return f'{url.scheme}://{url.hostname}' + (f':{url.port}' if url.port else '')
    except ValueError:
        return '<invalid>'


def browser_label(value):
    # Classification only: arbitrary UA strings can contain identifiers or secrets.
    family = next((name for marker, name in [('Edg', 'Edge'), ('Firefox', 'Firefox'), ('FxiOS', 'Firefox'),
                   ('CriOS', 'Chrome'), ('Chrome', 'Chrome'), ('Safari', 'Safari')] if marker in value), 'Other')
    return ('Mobile ' if any(word in value for word in ['Mobile', 'Android', 'iPhone', 'iPad']) else 'Desktop ') + family


def fields(request, **values):
    if get_settings().auth_debug_logging and hasattr(request.state, 'auth_diagnostic'):
        request.state.auth_diagnostic.update(values)


async def middleware(request, call_next):
    config = get_settings()
    enabled = config.auth_debug_logging and request.url.path in {'/auth/login', '/auth/me'}
    if not enabled:
        return await call_next(request)
    request_id = uuid4().hex
    expected = '__Host-ccdr_session' if config.auth_cookie_secure else 'ccdr_session'
    origin = request.headers.get('origin')
    data = dict(request_id=request_id, method=request.method, path=request.url.path,
                origin=origin_label(origin), host=origin_label('https://' + request.headers.get('host', '')),
                user_agent=browser_label(request.headers.get('user-agent', '')),
                origin_allowed=origin in config.cors_origins, origin_validation_passed=None,
                cookie_name=expected, cookie_secure=config.auth_cookie_secure, cookie_httponly=True,
                cookie_samesite=config.auth_cookie_samesite, cookie_path='/', cookie_domain='<host-only>',
                session_cookie_present=expected in request.cookies,
                cookie_names=[name for name in ['ccdr_session', '__Host-ccdr_session'] if name in request.cookies],
                other_cookie_count=sum(name not in {'ccdr_session', '__Host-ccdr_session'} for name in request.cookies),
                session_created=False)
    request.state.auth_diagnostic = data
    event = 'AUTH_LOGIN' if request.url.path == '/auth/login' else 'AUTH_ME'
    def emit(phase, **extra):
        logger.info(json.dumps(dict(data, timestamp=datetime.now(timezone.utc).isoformat(),
                                    event=event, phase=phase, **extra), separators=(',', ':')))
    emit('request')
    try:
        response = await call_next(request)
    except Exception:
        data['reason'] = 'request_failed'
        emit('response', status=500, result='error')
        raise
    response.headers['X-Request-ID'] = request_id
    emit('response', status=response.status_code, result='success' if response.status_code < 400 else 'rejected',
         set_cookie_header_present='set-cookie' in response.headers)
    return response
