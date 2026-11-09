"""Guardas offline: nenhum URL operacional pode chegar ao serviço CI."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from alembic.config import Config

import ci_postgres_tests
from ci_postgres_tests import CI_URL, migrated_engine, require_disposable_ci


def test_exact_disposable_configuration() -> None:
    """O URL operacional herdado nunca serve de alternativa ao URL exclusivo."""
    assert (
        require_disposable_ci(
            {
                "GITHUB_ACTIONS": "true",
                "TRACKER_DISPOSABLE_CI": "true",
                "TRACKER_CI_DATABASE_URL": CI_URL,
                "DATABASE_URL": "ignored-operational-url",
            }
        )
        == CI_URL
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"GITHUB_ACTIONS": "false"},
        {"TRACKER_DISPOSABLE_CI": "false"},
        {"TRACKER_CI_DATABASE_URL": "postgresql://operational/db"},
        {"TRACKER_CI_DATABASE_URL": ""},
        {"PGSERVICE": "operational"},
        {"PGOPTIONS": "-csearch_path=operational"},
    ],
)
def test_reject_configuration_before_connecting(changes: dict[str, str]) -> None:
    """Configurações incompletas ou influências libpq falham antes da ligação."""
    environment = {
        "GITHUB_ACTIONS": "true",
        "TRACKER_DISPOSABLE_CI": "true",
        "TRACKER_CI_DATABASE_URL": CI_URL,
    } | changes
    with pytest.raises(RuntimeError, match="descartável"):
        require_disposable_ci(environment)


@pytest.mark.parametrize(
    "missing", ["TRACKER_DISPOSABLE_CI", "TRACKER_CI_DATABASE_URL"]
)
def test_ci_fixture_fails_instead_of_skipping(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    """No runner, configuracao obrigatoria ausente e erro antes de abrir ligacoes."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("TRACKER_DISPOSABLE_CI", "true")
    monkeypatch.setenv("TRACKER_CI_DATABASE_URL", CI_URL)
    monkeypatch.delenv(missing, raising=False)
    with pytest.raises(RuntimeError, match="descart"):
        next(migrated_engine.__wrapped__())


def test_migration_fixture_resolves_configuration_without_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o cwd real da fixture e gera SQL com todas as ligações bloqueadas."""
    backend = Path(ci_postgres_tests.__file__).resolve().parent
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.scalar.side_effect = ["tracker_export_ci", "tracker_ci", 0]
    monkeypatch.setattr(
        ci_postgres_tests, "create_engine", lambda *args, **kwargs: engine
    )
    for key in list(ci_postgres_tests.os.environ):
        if key.upper().startswith("PG"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("TRACKER_DISPOSABLE_CI", "true")
    monkeypatch.setenv("TRACKER_CI_DATABASE_URL", CI_URL)
    real_run = ci_postgres_tests.subprocess.run
    calls = []

    def offline_run(command, **kwargs):
        calls.append(command)
        assert command[1:] == ["-m", "alembic", "upgrade", "head"]
        assert kwargs["cwd"] == backend
        config_path = kwargs["cwd"] / "alembic.ini"
        assert config_path.is_file()
        configuration = Config(str(config_path))
        assert (
            Path(configuration.get_main_option("script_location"))
            == backend / "alembic"
        )
        assert kwargs["env"]["DATABASE_URL"] == CI_URL
        # O subprocesso carrega a configuração e as migrações reais em modo SQL.
        # Os bloqueios impedem uma ligação acidental, mesmo por regressão.
        script = """
import runpy, socket, sys
from unittest.mock import patch

def forbidden(*args, **kwargs):
    raise AssertionError("Offline migration regression must never connect")

sys.argv = ["alembic", "upgrade", "head", "--sql"]
with patch("sqlalchemy.engine.Engine.connect", forbidden), patch.object(socket.socket, "connect", forbidden), patch.object(socket, "create_connection", forbidden):
    runpy.run_module("alembic", run_name="__main__")
"""
        result = real_run([command[0], "-B", "-c", script], **kwargs)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "CREATE TABLE users" in result.stdout
        assert "0008" in result.stdout
        return result

    monkeypatch.setattr(ci_postgres_tests.subprocess, "run", offline_run)
    fixture = migrated_engine.__wrapped__()
    try:
        assert next(fixture) is engine
        assert len(calls) == 1
    finally:
        fixture.close()
    engine.dispose.assert_called_once_with()
