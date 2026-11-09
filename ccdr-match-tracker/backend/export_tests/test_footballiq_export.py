"""Testes offline: ORM transitório, SQL compilado e DTOs reais em subprocesso.

Esta pasta fica fora de backend/tests para não carregar fixtures com DDL ou
administração de utilizadores. Nunca usa TEST_DATABASE_URL nem serviços reais.
"""

from __future__ import annotations

import copy
import json
import os
import socket
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from app.enums import EventTeam, EventType, MatchStatus
from app.footballiq_export import (
    AUTHORIZATION_BLOCKER,
    AuthorizationUnavailable,
    ExportSelection,
    ExportSettings,
    build_export_draft,
    compute_snapshot_version,
    emit_authorized_package,
    read_export_draft,
    recent_matches_query,
)
from app.models import (
    Competition,
    CompetitionFixture,
    Match,
    MatchEvent,
    MatchSquad,
    Player,
    Team,
)

AS_OF = datetime(2026, 11, 9, 10, tzinfo=UTC)
SETTINGS = ExportSettings(
    source_instance_id="fictional-export-test", timezone="Europe/Lisbon"
)
SYNTHETIC_SCOPE = {
    "scope_id": "fictional-test-scope",
    "club_id": "fictional-test-club",
    "team_id": "42",
    "permission": "matches:export",
}


@pytest.fixture(autouse=True)
def forbid_real_connections():
    """Uma tentativa de rede ou ligação SQLAlchemy real faz falhar o teste."""

    def forbidden(*args, **kwargs):
        raise AssertionError("Este teste não pode ligar a serviços reais")

    with (
        patch.object(socket.socket, "connect", forbidden),
        patch.object(socket, "create_connection", forbidden),
        patch("sqlalchemy.engine.Engine.connect", forbidden),
    ):
        yield


def selection(**changes) -> ExportSelection:
    """Seleção fictícia explícita, sem implicar autorização."""
    return ExportSelection(
        **(
            {
                "team_id": 42,
                "season_id": 7,
                "as_of": AS_OF,
                "competition_scope": "all",
                "competition_id": None,
            }
            | changes
        )
    )


def game(
    mid: int,
    *,
    home: bool = True,
    day: int = 8,
    status=MatchStatus.FINISHED,
    team_id: int = 42,
    season_id: int = 7,
) -> Match:
    """Cria um objeto ORM transitório; não cria linhas em qualquer base."""
    return Match(
        id=mid,
        team_id=team_id,
        opponent_id=55,
        season_id=season_id,
        team=Team(id=team_id, name="Equipa Fictícia A"),
        opponent=Team(id=55, name="Equipa Fictícia B"),
        matchday=1,
        kickoff_at=datetime(2026, 11, day, 15, tzinfo=UTC),
        status=status,
        is_home=home,
        elapsed_seconds=5400,
        clock_started_at=None,
    )


def event(
    eid: int,
    mid: int,
    *,
    kind=EventType.GOAL,
    side=EventTeam.US,
    seconds: int = 600,
    player_id=None,
    related_player_id=None,
) -> MatchEvent:
    """Acontecimento sintético com relógio acumulado e sem notas pessoais."""
    return MatchEvent(
        id=eid,
        match_id=mid,
        event_type=kind,
        team=side,
        period=1,
        elapsed_seconds=seconds,
        player_id=player_id,
        related_player_id=related_player_id,
        notes="Não exportar esta nota",
        recorded_by_id=999,
    )


def fixture(
    mid: int, *, competition_id: int = 3, fid: int = 20, home: bool = True
) -> CompetitionFixture:
    """Ligação fictícia a um jogo interno, sem resultado externo duplicado."""
    return CompetitionFixture(
        id=fid,
        internal_match_id=mid,
        competition_id=competition_id,
        home_team_id=42 if home else 55,
        away_team_id=55 if home else 42,
        matchday=1,
        home_goals=None,
        away_goals=None,
    )


def draft(matches=None, **changes):
    """Executa apenas o adaptador puro com os detalhes explicitamente fornecidos."""
    arguments = dict(
        matches=[game(10)] if matches is None else matches,
        events=[],
        squads=[],
        players={},
        fixtures=[],
        competitions={},
        exported_at=AS_OF,
    )
    arguments.update(changes)
    return build_export_draft(selection(), SETTINGS, **arguments)


def synthetic_package(export_draft):
    """Acrescenta scope fictício SÓ NOS TESTES; não é um emissor de produção."""
    return copy.deepcopy(export_draft.content) | {
        "authorized_scope": dict(SYNTHETIC_SCOPE),
        "snapshot_version": compute_snapshot_version(export_draft, SYNTHETIC_SCOPE),
    }


def representative_draft():
    """Dois jogos fictícios, com casa/fora, autogolos e uma convocatória observada."""
    player = Player(id=70, team_id=42, season_id=7, name="Jogador Fictício")
    squads = [MatchSquad(id=80, match_id=10, player_id=70, is_starter=True)]
    rows = [
        event(100, 10, player_id=70),
        event(101, 10, kind=EventType.OWN_GOAL, side=EventTeam.OPPONENT, seconds=800),
        event(102, 10, kind=EventType.OWN_GOAL, seconds=900),
        event(103, 9, side=EventTeam.OPPONENT),
    ]
    return draft(
        [game(10), game(9, home=False)],
        events=rows,
        squads=squads,
        players={70: player},
        fixtures=[fixture(10)],
        competitions={3: Competition(id=3, season_id=7, internal_team_id=42)},
    )


def test_sql_filters_order_limit_and_exists_compile_for_postgresql():
    sql = str(
        recent_matches_query(selection()).compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
    assert "matches.team_id = 42" in sql and "matches.season_id = 7" in sql
    assert "matches.status = 'FINISHED'" in sql and "matches.kickoff_at <=" in sql
    assert "ORDER BY matches.kickoff_at DESC, matches.id DESC" in sql
    assert "LIMIT 5" in sql
    assert "competition_fixtures" not in sql
    sql = str(
        recent_matches_query(
            selection(competition_scope="single", competition_id=3)
        ).compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    )
    assert "EXISTS (SELECT competition_fixtures.id" in sql
    assert "competition_fixtures.internal_match_id = matches.id" in sql
    assert "competition_fixtures.competition_id = 3" in sql
    assert "JOIN competition_fixtures" not in sql


@pytest.mark.parametrize(
    "changes",
    [
        {"team_id": True},
        {"season_id": 0},
        {"as_of": AS_OF.replace(tzinfo=None)},
        {"competition_scope": "single"},
        {"competition_id": 3},
        {"competition_scope": "unexpected"},
    ],
)
def test_selection_rejects_ambiguous_or_implicit_values(changes):
    with pytest.raises(ValueError):
        selection(**changes)


def test_settings_require_explicit_stable_identity_and_timezone():
    with pytest.raises(ValueError):
        ExportSettings(" ", "Europe/Lisbon")
    with pytest.raises(ValueError):
        ExportSettings(" fictional ", "Europe/Lisbon")
    with pytest.raises((KeyError, ValueError)):
        ExportSettings("fictional", "Invalid/Zone")


@pytest.mark.parametrize("count", range(6))
def test_core_accepts_zero_to_five_games_and_never_fabricates_scope(count):
    result = draft([game(mid) for mid in range(10, 10 - count, -1)])
    assert (
        len(result.content["matches"])
        == result.content["selection"]["returned_count"]
        == count
    )
    assert "authorized_scope" not in result.content
    assert "snapshot_version" not in result.content
    assert result.authorization_blocker == AUTHORIZATION_BLOCKER


@pytest.mark.parametrize(
    "matches",
    [
        [game(9), game(10)],
        [game(10), game(10)],
        [game(mid) for mid in range(10, 4, -1)],
        [game(10, status=MatchStatus.CANCELLED)],
        [game(10, team_id=99)],
        [game(10, season_id=8)],
    ],
)
def test_core_rejects_wrong_selection_instead_of_repairing_it(matches):
    with pytest.raises(ValueError):
        draft(matches)


def test_home_away_own_goals_and_unknown_categories():
    result = representative_draft()
    home, away = result.content["matches"]
    assert (home["score"]["home_goals"], home["score"]["away_goals"]) == (2, 1)
    assert (away["score"]["home_goals"], away["score"]["away_goals"]) == (1, 0)
    assert home["home_team"]["team_id"] == away["away_team"]["team_id"] == "42"
    assert home["events"][1]["team_id"] == "55"
    assert home["events"][0]["player"]["source_player_id"] == "70"
    assert home["squad"][0]["is_starter"] is True
    assert home["competition_id"] == "3" and away["competition_id"] is None
    assert home["external_references"] == [
        {"resource": "competition_fixture", "id": "20"}
    ]
    for match in result.content["matches"]:
        assert match["score"]["status"] == "unverified"
        assert match["score"]["provenance"]["verified_at"] is None
        assert match["updated_at"] is None
        assert all(
            category == {"status": "unknown", "evidence": None, "assessed_at": None}
            for category in match["quality"].values()
        )
    serialized = json.dumps(result.content)
    assert "recorded_by_id" not in serialized and "notes" not in serialized


def test_no_events_does_not_certify_nil_nil_or_zero_shots():
    row = draft().content["matches"][0]
    assert row["score"]["home_goals"] is row["score"]["away_goals"] is None
    assert row["score"]["provenance"]["reference_ids"] == []
    assert row["quality"]["shots"]["status"] == "unknown"
    assert row["squad"] is None


def test_finished_is_not_evidence_for_partial_or_complete():
    row = game(10)
    # Atributos inventados pelo chamador não são fontes de certificação.
    row.collection_status = "complete"
    row.collection_evidence = "Não existe tal coluna/regra no schema"
    result = draft([row])
    assert all(
        category["status"] == "unknown"
        for category in result.content["matches"][0]["quality"].values()
    )


def test_fixture_duplicates_and_stale_links_fail_closed():
    competition = Competition(id=3, season_id=7, internal_team_id=42)
    with pytest.raises(ValueError, match="Mais de um fixture"):
        draft(
            fixtures=[fixture(10), fixture(10, fid=21)], competitions={3: competition}
        )
    stale = fixture(10)
    stale.home_team_id = 99
    with pytest.raises(ValueError, match="desatualizada"):
        draft(fixtures=[stale], competitions={3: competition})


def test_single_requires_actual_link_and_all_keeps_unlinked_games():
    assert draft().content["matches"][0]["competition_id"] is None
    with pytest.raises(ValueError, match="competição"):
        build_export_draft(
            selection(competition_scope="single", competition_id=3),
            SETTINGS,
            matches=[game(10)],
            events=[],
            squads=[],
            players={},
            fixtures=[],
            competitions={},
            exported_at=AS_OF,
        )


def test_datetime_offsets_normalize_without_guessing_updated_at():
    match = game(10)
    first = draft([match])
    match.kickoff_at = match.kickoff_at.astimezone(tz=UTC).replace(hour=16, tzinfo=None)
    with pytest.raises(ValueError, match="timezone"):
        draft([match])
    assert first.content["matches"][0]["kickoff_at"].endswith("Z")


@pytest.mark.parametrize(
    "change", ["event", "delete_event", "squad", "kickoff", "name", "fixture"]
)
def test_relevant_corrections_change_match_and_selection_versions(change):
    match = game(10)
    rows = [event(100, 10)]
    kwargs = dict(
        matches=[match],
        events=rows,
        squads=[],
        players={},
        fixtures=[],
        competitions={},
    )
    previous = draft(**kwargs)
    if change == "event":
        rows[0].event_type = EventType.OWN_GOAL
    elif change == "delete_event":
        rows.clear()
    elif change == "squad":
        kwargs["players"] = {
            70: Player(id=70, team_id=42, season_id=7, name="Fictício")
        }
        kwargs["squads"] = [
            MatchSquad(id=80, match_id=10, player_id=70, is_starter=False)
        ]
    elif change == "kickoff":
        match.kickoff_at -= timedelta(hours=1)
    elif change == "name":
        match.opponent.name = "Outra designação fictícia"
    else:
        kwargs["fixtures"] = [fixture(10)]
        kwargs["competitions"] = {
            3: Competition(id=3, season_id=7, internal_team_id=42)
        }
    current = draft(**kwargs)
    assert (
        previous.content["matches"][0]["data_version"]
        != current.content["matches"][0]["data_version"]
    )
    assert previous.selection_version != current.selection_version
    assert compute_snapshot_version(
        previous, SYNTHETIC_SCOPE
    ) != compute_snapshot_version(current, SYNTHETIC_SCOPE)


def test_export_time_and_input_detail_order_do_not_change_content_versions():
    kwargs = dict(events=[event(101, 10, seconds=800), event(100, 10, seconds=600)])
    previous = draft(**kwargs)
    kwargs["events"].reverse()
    current = draft(**kwargs, exported_at=AS_OF + timedelta(hours=1))
    assert previous.content["exported_at"] != current.content["exported_at"]
    assert previous.selection_version == current.selection_version
    assert previous.content["matches"] == current.content["matches"]
    assert compute_snapshot_version(
        previous, SYNTHETIC_SCOPE
    ) == compute_snapshot_version(current, SYNTHETIC_SCOPE)


def test_snapshot_includes_scope_selection_and_instance():
    result = draft()
    changed_scope = SYNTHETIC_SCOPE | {"scope_id": "fictional-second-scope"}
    assert compute_snapshot_version(result, changed_scope) != compute_snapshot_version(
        result, SYNTHETIC_SCOPE
    )
    with pytest.raises(ValueError):
        compute_snapshot_version(result, SYNTHETIC_SCOPE | {"team_id": "99"})
    other = build_export_draft(
        selection(),
        ExportSettings("other-fictional-instance", "Europe/Lisbon"),
        matches=[game(10)],
        events=[],
        squads=[],
        players={},
        fixtures=[],
        competitions={},
        exported_at=AS_OF,
    )
    assert (
        other.content["matches"][0]["data_version"]
        != result.content["matches"][0]["data_version"]
    )


def test_transform_does_not_mutate_orm_state_or_use_private_data():
    match, row = game(10), event(100, 10)
    before = [
        dict(inspect(obj).dict) for obj in (match, row, match.team, match.opponent)
    ]
    draft([match], events=[row])
    assert before == [
        dict(inspect(obj).dict) for obj in (match, row, match.team, match.opponent)
    ]


def test_arbitrary_team_role_or_declared_scope_never_authorizes_real_package():
    for args in ((), (draft(),), (draft(), SYNTHETIC_SCOPE), (42, "ADMIN")):
        with pytest.raises(AuthorizationUnavailable, match="autorização"):
            emit_authorized_package(*args)


class FakeSession:
    """Simula apenas SELECTs; a compilação SQL é testada separadamente."""

    def __init__(self, engine, **kwargs):
        assert kwargs == {
            "bind": engine,
            "autoflush": False,
            "expire_on_commit": False,
            "join_transaction_mode": "rollback_only",
        }
        self.engine = engine

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def scalars(self, statement):
        params = statement.compile().params
        model = statement.column_descriptions[0]["entity"]
        self.engine.queries.append(model)
        if model is Match:
            assert self.engine.readonly
            rows = [
                m
                for m in self.engine.matches
                if m.team_id == params["team_id_1"]
                and m.season_id == params["season_id_1"]
                and m.status == params["status_1"]
                and m.kickoff_at <= params["kickoff_at_1"]
            ]
            if "competition_id_1" in params:
                linked = {
                    f.internal_match_id
                    for f in self.engine.fixtures
                    if f.competition_id == params["competition_id_1"]
                }
                rows = [m for m in rows if m.id in linked]
            rows = sorted(rows, key=lambda m: (m.kickoff_at, m.id), reverse=True)[
                : params["param_1"]
            ]
            self.engine.selected = {m.id for m in rows}
            return rows
        if model is CompetitionFixture:
            return [
                f
                for f in self.engine.fixtures
                if f.internal_match_id in self.engine.selected
            ]
        if model is Competition:
            return list(self.engine.competitions.values())
        if model is MatchEvent:
            assert set(params["match_id_1"]) == self.engine.selected
            return [e for e in self.engine.events if e.match_id in self.engine.selected]
        if model is MatchSquad:
            assert set(params["match_id_1"]) == self.engine.selected
            return [
                row
                for row in self.engine.squads
                if row.match_id in self.engine.selected
            ]
        if model is Player:
            return [
                row for row in self.engine.players.values() if row.id in params["id_1"]
            ]
        raise AssertionError(f"SELECT inesperado: {model}")


class FakeEngine:
    """Regista a orquestração transacional sem abrir uma ligação real."""

    dialect = SimpleNamespace(name="postgresql")

    def __init__(self, matches, fixtures=(), events=()):
        self.matches, self.fixtures, self.events = matches, fixtures, events
        self.squads, self.players = [], {}
        self.competitions = {3: Competition(id=3, season_id=7, internal_team_id=42)}
        self.queries, self.steps = [], []
        self.readonly = False

    def connect(self):
        self.steps.append("connect")
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.steps.append("exit")

    def execution_options(self, **options):
        assert options == {"isolation_level": "REPEATABLE READ"}
        self.steps.append("isolation")
        return self

    def begin(self):
        self.steps.append("begin")
        return self

    def exec_driver_sql(self, statement):
        assert statement == "SET TRANSACTION READ ONLY"
        self.steps.append("readonly")
        self.readonly = True


def test_reader_limits_before_details_and_excludes_wrong_scope_status_and_future():
    games = [game(mid) for mid in range(5, 12)]
    games += [
        game(100, status=MatchStatus.FIRST_HALF),
        game(101, day=10),
        game(102, team_id=77),
        game(103, season_id=8),
    ]
    engine = FakeEngine(games, events=[event(700, 5), event(701, 11)])
    with patch(
        "app.footballiq_export.Session",
        side_effect=lambda **kw: FakeSession(engine, **kw),
    ):
        result = read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)
    assert [m["source_match_id"] for m in result.content["matches"]] == [
        "11",
        "10",
        "9",
        "8",
        "7",
    ]
    assert {
        e["source_event_id"] for m in result.content["matches"] for e in m["events"]
    } == {"701"}
    assert engine.queries[0] is Match
    assert engine.steps[:4] == ["connect", "isolation", "begin", "readonly"]
    assert engine.steps[-2:] == ["exit", "exit"]


def test_reader_single_uses_linked_games_only_and_does_not_duplicate():
    engine = FakeEngine(
        [game(10), game(9), game(8)], fixtures=[fixture(10), fixture(8, fid=21)]
    )
    with patch(
        "app.footballiq_export.Session",
        side_effect=lambda **kw: FakeSession(engine, **kw),
    ):
        result = read_export_draft(
            engine,
            selection(competition_scope="single", competition_id=3),
            SETTINGS,
            exported_at=AS_OF,
        )
    assert [m["source_match_id"] for m in result.content["matches"]] == ["10", "8"]


def test_reader_empty_does_not_query_details_and_rejects_non_postgres():
    engine = FakeEngine([])
    with patch(
        "app.footballiq_export.Session",
        side_effect=lambda **kw: FakeSession(engine, **kw),
    ):
        result = read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)
    assert result.content["matches"] == [] and engine.queries == [Match]
    engine.dialect = SimpleNamespace(name="sqlite")
    with pytest.raises(ValueError, match="PostgreSQL"):
        read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)


@pytest.mark.parametrize("case", ["representative", "empty", "fixture"])
def test_output_against_real_footballiq_dtos_in_isolated_process(case):
    checkout = os.environ.get("FOOTBALLIQ_CHECKOUT")
    if not checkout:
        pytest.skip(
            "Definir FOOTBALLIQ_CHECKOUT explicitamente para testar os DTOs reais"
        )
    if case == "fixture":
        payload = json.loads(
            (Path(__file__).parent / "fixtures" / "fictional_package.json").read_text(
                encoding="utf-8"
            )
        )
    else:
        payload = synthetic_package(
            representative_draft() if case == "representative" else draft([])
        )
    script = """
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / 'src'))
from footballiq.analytics import analyze_recent_matches
from footballiq.schemas.integration import ExportPackage
payload = sys.stdin.read()
package = ExportPackage.model_validate_json(payload)
report = analyze_recent_matches(package)
assert report.authorization_verified is False
assert all(metric.values is None for metric in report.metrics.values())
print('DTOs FootballIQ v1: OK; métricas não verificadas: null')
"""
    completed = subprocess.run(
        [sys.executable, "-B", "-I", "-c", script, checkout],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_static_fixture_is_generated_from_synthetic_source_only():
    stored = json.loads(
        (Path(__file__).parent / "fixtures" / "fictional_package.json").read_text(
            encoding="utf-8"
        )
    )
    assert stored == synthetic_package(representative_draft())


@pytest.mark.parametrize(
    "invalid", ["missing", "wrong_id", "wrong_season", "not_in_squad"]
)
def test_player_references_fail_closed(invalid):
    row = Player(id=70, team_id=42, season_id=7, name="Fictício")
    players = {70: row}
    squads = [MatchSquad(id=80, match_id=10, player_id=70, is_starter=True)]
    if invalid == "missing":
        players.clear()
    elif invalid == "wrong_id":
        row.id = 71
    elif invalid == "wrong_season":
        row.season_id = 99
    else:
        squads = []
    with pytest.raises(ValueError):
        draft(events=[event(100, 10, player_id=70)], squads=squads, players=players)


def test_reader_loads_player_and_squad_only_for_selected_matches():
    engine = FakeEngine([game(10)], events=[event(100, 10, player_id=70)])
    engine.players = {70: Player(id=70, team_id=42, season_id=7, name="Fictício")}
    engine.squads = [MatchSquad(id=80, match_id=10, player_id=70, is_starter=True)]
    with patch(
        "app.footballiq_export.Session",
        side_effect=lambda **kw: FakeSession(engine, **kw),
    ):
        result = read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)
    assert (
        result.content["matches"][0]["squad"][0]["player"]["source_player_id"] == "70"
    )
    assert (
        result.content["matches"][0]["events"][0]["player"]["source_player_id"] == "70"
    )
    assert Player in engine.queries


def test_failure_in_snapshot_closes_contexts_without_emitting_partial_result():
    engine = FakeEngine([game(10)])

    class FailingSession(FakeSession):
        def scalars(self, statement):
            raise RuntimeError("Falha sintética durante a leitura")

    with patch(
        "app.footballiq_export.Session",
        side_effect=lambda **kw: FailingSession(engine, **kw),
    ):
        with pytest.raises(RuntimeError, match="Falha sintética"):
            read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)
    assert engine.steps[-2:] == ["exit", "exit"]


def test_tampered_draft_cannot_reuse_old_versions():
    result = representative_draft()
    result.content["matches"][0]["score"]["home_goals"] = 99
    with pytest.raises(ValueError, match="Rascunho alterado"):
        compute_snapshot_version(result, SYNTHETIC_SCOPE)


def test_import_does_not_open_connection_or_load_settings():
    script = """
from unittest.mock import patch
import socket
from sqlalchemy.engine import Engine
from app import config

def forbidden(*args, **kwargs):
    raise AssertionError('Import não pode abrir ligação ou ler configuração operacional')

with patch.object(Engine, 'connect', forbidden), patch.object(socket.socket, 'connect', forbidden), patch.object(config, 'get_settings', forbidden):
    import app.footballiq_export
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_reopening_newer_game_reselects_window_without_touching_older_versions():
    matches = [game(mid) for mid in range(6, 12)]

    def read(rows):
        engine = FakeEngine(rows)
        with patch(
            "app.footballiq_export.Session",
            side_effect=lambda **kw: FakeSession(engine, **kw),
        ):
            return read_export_draft(engine, selection(), SETTINGS, exported_at=AS_OF)

    before = read(matches)
    matches[-1].status = MatchStatus.SECOND_HALF
    after = read(matches)
    assert [m["source_match_id"] for m in before.content["matches"]] == [
        "11",
        "10",
        "9",
        "8",
        "7",
    ]
    assert [m["source_match_id"] for m in after.content["matches"]] == [
        "10",
        "9",
        "8",
        "7",
        "6",
    ]
    assert before.selection_version != after.selection_version
    old = {m["source_match_id"]: m["data_version"] for m in before.content["matches"]}
    assert all(
        old[m["source_match_id"]] == m["data_version"]
        for m in after.content["matches"]
        if m["source_match_id"] in old
    )
