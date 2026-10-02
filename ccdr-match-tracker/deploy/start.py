"""Supervise one API worker, one Next server and Caddy; no migrations."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def public_port():
    try:
        port = int(os.environ.get('PORT', '8080'))
    except ValueError:
        raise ValueError('PORT must be an integer') from None
    if not 1 <= port <= 65535 or port in {3000, 8000}:
        raise ValueError('PORT must be valid and different from internal ports 3000/8000')
    return port


def commands():
    return [
        ([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000',
          '--workers', '1', '--proxy-headers', '--forwarded-allow-ips', '127.0.0.1', '--root-path', '/api'], ROOT / 'backend'),
        (['node', 'server.js'], ROOT / 'frontend'),
        (['caddy', 'run', '--config', str(ROOT / 'deploy' / 'Caddyfile'), '--adapter', 'caddyfile'], ROOT),
    ]


def main():
    if os.environ.get('APP_ENV') == 'production' and os.environ.get('AUTH_COOKIE_SAMESITE', 'lax') != 'lax':
        raise ValueError('Combined same-origin deployment requires AUTH_COOKIE_SAMESITE=lax')
    port = public_port()
    os.environ['PORT'] = str(port)
    processes = []
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        for index, (command, cwd) in enumerate(commands()):
            if stopping:
                return 0
            env = dict(os.environ)
            if index == 1:
                # Next receives no DB/session configuration.
                env = {key: value for key, value in env.items() if key in {'PATH', 'HOME', 'NODE_ENV', 'NEXT_TELEMETRY_DISABLED'}}
                env.update(PORT='3000', HOSTNAME='127.0.0.1')
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, start_new_session=True))
            if index < 2:
                url = 'http://127.0.0.1:8000/health' if index == 0 else 'http://127.0.0.1:3000/login'
                deadline = time.monotonic() + 60
                while not stopping:
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError('Application process exited during startup')
                    try:
                        with urlopen(url, timeout=1) as response:
                            if response.status == 200: break
                    except OSError:
                        pass
                    if time.monotonic() > deadline:
                        raise RuntimeError('Application startup timed out')
                    time.sleep(.2)
        while not stopping:
            if any(process.poll() is not None for process in processes):
                return 1
            time.sleep(.2)
        return 0
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        deadline = time.monotonic() + 20
        for process in reversed(processes):
            try:
                process.wait(timeout=max(.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()


if __name__ == '__main__':
    raise SystemExit(main())
