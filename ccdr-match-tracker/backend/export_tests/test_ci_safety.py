"""Guardas offline: nenhum URL operacional pode chegar ao serviço CI."""

import pytest

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
