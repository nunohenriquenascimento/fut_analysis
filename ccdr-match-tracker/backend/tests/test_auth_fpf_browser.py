"""Opt-in real HTML upload UI, exclusively in postgres_schema's isolated target."""
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
from threading import Thread
import time

import httpx
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
import uvicorn

from conftest import alembic
from app.config import get_settings
from app.database import get_db
from app.main import app
from app.fpf_parser import parse_competition
from app.models import Competition, CompetitionFixture, CompetitionTeam, Match, MatchEvent, MatchSquad, Player, Season, Team, User
from test_auth import PASSWORD, password_hash  # noqa: F401
from fpf_calendar_data import calendar_data, SOURCES


@pytest.mark.skipif(os.getenv("RUN_LIVE_BROWSER_E2E") != "1", reason="Real browser requires test-only opt-in and frontend build")
@pytest.mark.parametrize("width", [360, 390, 1440])
def test_real_fpf_upload_mapping_confirmation_and_internal_preservation(postgres_schema, password_hash, width):
    backend = Path(__file__).resolve().parents[1]
    frontend = backend.parent / "frontend"
    captures = backend / "tests/fixtures/fpf"
    assert (frontend / ".next/BUILD_ID").is_file()
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", 8000))
        except OSError:
            pytest.fail("Port 8000 occupied; no existing API will be reused or stopped")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    url = postgres_schema()
    assert alembic(url, "upgrade", "head").returncode == 0
    engine = create_engine(url)
    names = [r["name"] for r in parse_competition((captures / "competition_30369_season_106.html").read_text(encoding="utf-8-sig"))["series"][0]["standings"]]
    with Session(engine) as db:
        season = Season(name="FPF browser", starts_on=date(2026, 7, 1), ends_on=date(2027, 6, 30))
        teams = [Team(name=name) for name in names]
        admin = User(name="FPF test", email="fpf-browser@test.local", role="ADMIN", is_active=True, password_hash=password_hash)
        db.add_all([season, admin, *teams]); db.flush()
        mapping = {team.name: team.id for team in teams}
        own = mapping["V. Cortez Mondego-Guarda"]
        competition = Competition(name="FPF browser", season_id=season.id, internal_team_id=own,
                                  rules=dict(win=3, draw=1, loss=0, tiebreakers=[]))
        db.add(competition); db.flush()
        db.add_all(CompetitionTeam(competition_id=competition.id, team_id=t.id) for t in teams)
        match = Match(season_id=season.id, team_id=own, opponent_id=mapping["Guarda Fc"], matchday=3,
                      kickoff_at=datetime(2026, 10, 17, 15, tzinfo=timezone.utc), is_home=True,
                      status="FINISHED", elapsed_seconds=60, venue="Internal stadium")
        player = Player(name="Synthetic internal player", season_id=season.id, team_id=own, position="MC", shirt_number=1)
        db.add_all([match, player]); db.flush()
        db.add(MatchSquad(match_id=match.id, player_id=player.id, is_starter=True))
        db.add(MatchEvent(match_id=match.id, player_id=player.id, event_type="GOAL", team="US", period=1,
                          elapsed_seconds=13, recorded_by_id=admin.id))
        db.commit(); cid, mid = competition.id, match.id
    def fingerprint():
        with engine.connect() as c:
            return {model.__tablename__: c.execute(select(*model.__table__.columns).order_by(model.id)).all()
                    for model in (Match, MatchEvent, MatchSquad, Player)}
    before = fingerprint()
    def database():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = database
    origin = f"http://localhost:{port}"
    origins = get_settings().cors_origins
    origins.append(origin)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error"))
    thread = Thread(target=server.run, daemon=True)
    process = None
    try:
        thread.start()
        node = shutil.which("node"); assert node
        process = subprocess.Popen([node, str(frontend / "node_modules/next/dist/bin/next"), "start", "--hostname", "127.0.0.1", "--port", str(port)],
                                   cwd=frontend, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        deadline = time.monotonic() + 20
        with httpx.Client(trust_env=False) as client:
            while True:
                try:
                    if server.started and client.get(origin + "/login").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline, "Test servers failed to start"
                time.sleep(.1)
        result = subprocess.run([node, "-"], input=(backend / "tests/fpf_browser.cjs").read_text(encoding="utf-8"),
            cwd=frontend, capture_output=True, text=True, encoding="utf-8", timeout=120,
            env={**os.environ, "BROWSER_ORIGIN": origin, "BROWSER_WIDTH": str(width), "BROWSER_PASSWORD": PASSWORD,
                 "BROWSER_COMPETITION_ID": str(cid), "BROWSER_MATCH_ID": str(mid), "BROWSER_TEAM_MAP": json.dumps(mapping), "FPF_FIXTURES": str(captures),
                 "BROWSER_CALENDAR_SOURCES": json.dumps([dict(file=name, fixture_id=fid,
                     url=f"https://resultados.fpf.pt/Competition/GetClassificationAndMatchesByFixture?fixtureId={fid}")
                     for fid,name in SOURCES.items()]), "BROWSER_CALENDAR_GAMES": json.dumps(calendar_data()[1])})
        assert result.returncode == 0, result.stdout + result.stderr
        assert fingerprint() == before
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(CompetitionFixture)) == 56
            assert db.get(Competition, cid).fpf_data["mode"] == "captured_html"
    finally:
        if process is not None:
            process.terminate(); process.wait(timeout=10)
        server.should_exit = True; thread.join(timeout=10)
        origins.remove(origin)
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()
