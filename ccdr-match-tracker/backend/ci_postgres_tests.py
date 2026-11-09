"""Integração exclusiva do serviço PostgreSQL descartável do GitHub Actions."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, select, text, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.enums import EventTeam, EventType, MatchStatus, PlayerPosition
from app.footballiq_export import (
    ExportDraft,
    ExportSelection,
    ExportSettings,
    read_export_draft,
)
from app.models import (
    Competition,
    CompetitionFixture,
    Match,
    MatchEvent,
    MatchSquad,
    Player,
    Season,
    Team,
)

CI_URL = (
    "postgresql+psycopg://tracker_ci:tracker_ci_only@127.0.0.1:55439/tracker_export_ci"
)
AS_OF = datetime(2026, 11, 9, 10, tzinfo=UTC)
SETTINGS = ExportSettings("fictional-ci", "Europe/Lisbon")


def require_disposable_ci(environment: dict[str, str]) -> str:
    """Recusa URLs arbitrários e execução local antes de criar qualquer engine.

    O endereço é reservado ao service container deste workflow. Estas guardas
    evitam erros de configuração; não são uma fronteira contra código malicioso.
    """
    if (
        environment.get("GITHUB_ACTIONS") != "true"
        or environment.get("TRACKER_DISPOSABLE_CI") != "true"
        or environment.get("TRACKER_CI_DATABASE_URL") != CI_URL
        or any(key.upper().startswith("PG") for key in environment)
    ):
        raise RuntimeError("É obrigatório o serviço descartável exclusivo do CI")
    return CI_URL


@pytest.fixture(scope="session")
def migrated_engine() -> Iterator[Engine]:
    """Migra uma base nova do serviço CI, sem consultar DATABASE_URL herdado."""
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        and os.environ.get("TRACKER_DISPOSABLE_CI") != "true"
    ):
        pytest.skip("PostgreSQL real reservado ao workflow descartável")
    url = require_disposable_ci(dict(os.environ))
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as connection:
            assert (
                connection.scalar(text("SELECT current_database()"))
                == "tracker_export_ci"
            )
            assert connection.scalar(text("SELECT current_user")) == "tracker_ci"
            assert (
                connection.scalar(
                    text(
                        "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"
                    )
                )
                == 0
            ), "Migrações exigem base nova e vazia"
        # DATABASE_URL só é definido no subprocesso Alembic e recebe o URL validado.
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, "DATABASE_URL": url, "APP_ENV": "development"},
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def prepared_engine(migrated_engine: Engine) -> Engine:
    """Prepara dados fictícios; toda a escrita pertence a esta ligação."""
    engine = migrated_engine
    with engine.begin() as connection:
        # Apenas tabelas do serviço descartável já validado; nunca dados locais.
        connection.execute(text("TRUNCATE seasons, teams CASCADE"))
    with Session(engine) as db, db.begin():
        db.add_all(
            [
                Season(
                    id=i,
                    name=f"Fictional {i}",
                    starts_on=date(2026, 1, 1),
                    ends_on=date(2026, 12, 31),
                )
                for i in (7, 8)
            ]
        )
        db.add_all([Team(id=i, name=f"Fictional {i}") for i in (42, 55, 99)])
        db.flush()
        db.add(
            Competition(
                id=3, season_id=7, internal_team_id=42, name="Fictional cup", rules={}
            )
        )
        db.add(
            Player(
                id=70,
                team_id=42,
                season_id=7,
                name="Fictional player",
                position=PlayerPosition.GR,
            )
        )
        for mid in (2, 9, 10, 11, 12, 13, 14, 15, 16, 17):
            db.add(
                Match(
                    id=mid,
                    team_id=99 if mid == 15 else 42,
                    opponent_id=55,
                    season_id=8 if mid == 16 else 7,
                    matchday=mid,
                    kickoff_at=datetime(
                        2026, 11, 10 if mid == 17 else 8, 15, tzinfo=UTC
                    ),
                    status=MatchStatus.CANCELLED if mid == 14 else MatchStatus.FINISHED,
                    is_home=True,
                    elapsed_seconds=5400,
                )
            )
        db.flush()
        db.add(MatchSquad(id=80, match_id=13, player_id=70, is_starter=True))
        db.add_all(
            [
                MatchEvent(
                    id=100,
                    match_id=13,
                    event_type=EventType.GOAL,
                    team=EventTeam.US,
                    player_id=70,
                    period=1,
                    elapsed_seconds=60,
                ),
                MatchEvent(
                    id=101,
                    match_id=13,
                    event_type=EventType.OWN_GOAL,
                    team=EventTeam.OPPONENT,
                    period=1,
                    elapsed_seconds=80,
                ),
                MatchEvent(
                    id=102,
                    match_id=13,
                    event_type=EventType.OWN_GOAL,
                    team=EventTeam.US,
                    period=1,
                    elapsed_seconds=90,
                ),
                MatchEvent(
                    id=103,
                    match_id=2,
                    event_type=EventType.GOAL,
                    team=EventTeam.US,
                    period=1,
                    elapsed_seconds=60,
                ),
            ]
        )
        db.add_all(
            [
                CompetitionFixture(
                    id=mid,
                    competition_id=3,
                    external_key=f"fictional-{mid}",
                    matchday=mid,
                    home_team_id=42,
                    away_team_id=55,
                    internal_match_id=mid if mid != 20 else None,
                    source="fictional-ci",
                )
                for mid in (10, 13, 20)
            ]
        )
    return engine


def export(engine: Engine, scope: str = "all") -> ExportDraft:
    """Lê o rascunho; não emite pacotes autorizados nem certificações."""
    return read_export_draft(
        engine,
        ExportSelection(
            team_id=42,
            season_id=7,
            as_of=AS_OF,
            competition_scope=scope,
            competition_id=3 if scope == "single" else None,
        ),
        SETTINGS,
        exported_at=AS_OF,
    )


def test_selection_events_squad_and_competition(prepared_engine: Engine) -> None:
    """Confirma a janela numérica e os detalhes fictícios filtrados no PostgreSQL."""
    result = export(prepared_engine)
    assert [row["source_match_id"] for row in result.content["matches"]] == [
        "13",
        "12",
        "11",
        "10",
        "9",
    ]
    first = result.content["matches"][0]
    assert (first["score"]["home_goals"], first["score"]["away_goals"]) == (2, 1)
    assert first["squad"][0]["is_starter"] is True
    assert len(first["events"]) == 3
    assert first["events"][0]["player"]["source_player_id"] == "70"
    assert [
        row["source_match_id"]
        for row in export(prepared_engine, "single").content["matches"]
    ] == ["13", "10"]


def test_repeatable_read_concurrent_correction_and_no_writes(
    prepared_engine: Engine,
) -> None:
    """Mantém o primeiro snapshot estável perante uma correção concorrente."""
    engine = prepared_engine
    corrected = False
    statements: list[str] = []
    detail_ids: list[set[int]] = []

    def observe(connection, cursor, statement, parameters, context, executemany):
        nonlocal corrected
        if connection.info.get("fixture_writer"):
            return
        statements.append(statement)
        if "FROM match_events" in statement:
            assert corrected, "A seleção deve terminar antes de carregar eventos"
            detail_ids.append(
                {
                    value
                    for key, value in parameters.items()
                    if key.startswith("match_id_")
                }
            )
        if "FROM matches " in statement or "FROM matches\n" in statement:
            with connection.connection.cursor() as probe:
                probe.execute("SHOW transaction_isolation")
                assert probe.fetchone()[0] == "repeatable read"
                probe.execute("SHOW transaction_read_only")
                assert probe.fetchone()[0] == "on"
            if not corrected:
                # Outra ligação confirma a correção depois do SELECT inicial.
                with engine.connect() as writer:
                    writer.info["fixture_writer"] = True
                    try:
                        assert writer.connection is not connection.connection
                        with writer.begin():
                            writer.execute(
                                update(MatchEvent)
                                .where(MatchEvent.id == 100)
                                .values(event_type=EventType.SHOT_OFF_TARGET)
                            )
                    finally:
                        writer.info.pop("fixture_writer", None)
                corrected = True

    event.listen(engine, "after_cursor_execute", observe)
    try:
        previous = export(engine)
    finally:
        event.remove(engine, "after_cursor_execute", observe)
    current = export(engine)
    assert corrected and detail_ids == [{9, 10, 11, 12, 13}]
    assert previous.content["matches"][0]["score"]["home_goals"] == 2
    assert current.content["matches"][0]["score"]["home_goals"] == 1
    assert previous.selection_version != current.selection_version
    assert all(
        sql.lstrip().upper().startswith(("SELECT", "SET TRANSACTION READ ONLY"))
        for sql in statements
    )
    with engine.connect() as connection:
        assert (
            connection.scalar(select(MatchEvent.event_type).where(MatchEvent.id == 100))
            == EventType.SHOT_OFF_TARGET
        )
