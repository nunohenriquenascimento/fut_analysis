"""Opt-in browser integration against real HTTP, WebSockets and isolated PostgreSQL.

Build frontend first, then set RUN_LIVE_BROWSER_E2E=1 and TEST_DATABASE_URL.
Uses port 8000 because the development frontend build embeds that API origin.
"""
import os
from pathlib import Path
import shutil
import socket
import subprocess
from threading import Thread
import time

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

from app.config import get_settings
from app.main import app
from app.models import Match, MatchEvent, MatchSquad, Player
from app import statistics_service
from test_auth import PASSWORD
from test_auth_live_socket import sockets, password_hash  # noqa: F401


@pytest.mark.skipif(os.getenv("RUN_LIVE_BROWSER_E2E") != "1", reason="Set RUN_LIVE_BROWSER_E2E=1 after frontend build")
@pytest.mark.parametrize("width", [360, 390])
@pytest.mark.parametrize("scenario", ["live_browser.cjs", "merge_browser.cjs"])
def test_real_browser_reopen_clock_history_statistics_and_second_device(sockets, monkeypatch, width, scenario):
    _, engine, ids, users, _, _ = sockets
    frontend = Path(__file__).resolve().parents[2] / "frontend"
    node = shutil.which("node")
    assert node and (frontend / ".next/BUILD_ID").exists(), "Node and a frontend production build are required"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        frontend_port = probe.getsockname()[1]
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", 8000))
        except OSError:
            pytest.fail("Port 8000 is occupied; stop the development API before this integration test")
    with Session(engine) as db:
        player_id = db.scalar(select(Player.id).where(Player.name == "Socket scorer"))
        if scenario == "merge_browser.cjs":
            for match_id, seconds in zip(ids, [3780, 900]):
                match = db.get(Match, match_id)
                match.status = "FINISHED"
                match.elapsed_seconds = seconds
                db.add(MatchSquad(match_id=match_id, player_id=player_id, is_starter=match_id == ids[0]))
            db.add(MatchEvent(match_id=ids[0], event_type="GOAL", team="US", player_id=player_id,
                              period=2, elapsed_seconds=3700, recorded_by_id=users["ADMIN"]))
            for kind, seconds in [("GOAL", 270), ("OWN_GOAL", 300), ("SHOT_ON_TARGET", 330), ("YELLOW_CARD", 400)]:
                db.add(MatchEvent(match_id=ids[1], event_type=kind, team="US", player_id=player_id,
                                  period=1, elapsed_seconds=seconds, recorded_by_id=users["ADMIN"], notes="Historical event"))
            db.commit()
    monkeypatch.setattr(statistics_service, "SEASON_NAME", "Socket test")
    monkeypatch.setattr(statistics_service, "CLUB_NAME", "Socket club")
    origin = f"http://localhost:{frontend_port}"
    origins = get_settings().cors_origins
    origins.append(origin)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error"))
    thread = Thread(target=server.run, daemon=True)
    process = None
    try:
        thread.start()
        process = subprocess.Popen([node, str(frontend / "node_modules/next/dist/bin/next"), "start",
                                    "--hostname", "127.0.0.1", "--port", str(frontend_port)], cwd=frontend,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        deadline = time.monotonic() + 20
        with httpx.Client(trust_env=False) as client:
            while True:
                try:
                    if server.started and client.get(origin + "/login").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline, "Integration servers did not start"
                time.sleep(.1)
        script = (Path(__file__).parent / scenario).read_text(encoding="utf-8")
        result = subprocess.run([node, "-"], input=script, text=True, encoding="utf-8", cwd=frontend,
                                env={**os.environ, "BROWSER_ORIGIN": origin, "BROWSER_WIDTH": str(width),
                                     "BROWSER_MATCH_ID": str(ids[0]), "BROWSER_PLAYER_ID": str(player_id),
                                     "BROWSER_CONTINUATION_ID": str(ids[1]),
                                     "BROWSER_PASSWORD": PASSWORD}, capture_output=True, timeout=90)
        assert result.returncode == 0, result.stdout + result.stderr
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=10)
        server.should_exit = True
        thread.join(timeout=10)
        origins.remove(origin)
