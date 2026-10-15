"""Manually authorized metadata probe, never a deployment/startup command.

No app imports, dotenv reads, environment changes, migrations or backups.
CONFIRMED covers these checks only, not external Railway identity or workers.
See READ_ONLY_PROBE.md for operator prerequisites and stop conditions.
"""
import argparse
from dataclasses import dataclass
import ipaddress
import json
import os
from pathlib import Path
import re
from uuid import UUID

CORE = ("users", "seasons", "teams", "players", "matches", "match_squads", "match_events")
AUTH = ("auth_sessions", "login_throttles")
COMPETITION = ("competitions", "competition_teams", "competition_fixtures")
TABLES = ("alembic_version", *CORE, *AUTH, *COMPETITION)
KNOWN_REVISIONS = frozenset(f"{number:04d}" for number in range(1, 8))
TLS_PARAMETERS = frozenset(("sslmode", "sslrootcert", "sslcert", "sslkey", "channel_binding"))
AMBIGUOUS_ENV = ("PGHOST", "PGHOSTADDR", "PGPORT", "PGDATABASE", "PGSERVICE",
                 "PGSERVICEFILE", "PGOPTIONS", "PGLOADBALANCEHOSTS", "PGTARGETSESSIONATTRS")
BEGIN = "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
SETTINGS = (
    "SET LOCAL statement_timeout = '5000ms'",
    "SET LOCAL lock_timeout = '1500ms'",
    "SET LOCAL idle_in_transaction_session_timeout = '10000ms'",
    "SET LOCAL search_path = pg_catalog",
    "SET LOCAL row_security = off",
)
POLICY_QUERY = """SELECT
    pg_catalog.current_setting('transaction_read_only'),
    pg_catalog.current_setting('transaction_isolation'),
    pg_catalog.current_setting('statement_timeout'),
    pg_catalog.current_setting('lock_timeout'),
    pg_catalog.current_setting('idle_in_transaction_session_timeout'),
    pg_catalog.current_database(),
    pg_catalog.current_setting('server_version_num'),
    pg_catalog.inet_server_addr()::text"""
CATALOG_QUERY = """SELECT n.nspname, c.relname, c.relkind,
    pg_catalog.has_table_privilege(c.oid, 'SELECT')
    FROM pg_catalog.pg_class AS c
    JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
    WHERE c.relname = ANY(%s)
      AND pg_catalog.left(n.nspname, 3) <> 'pg_'
      AND n.nspname <> 'information_schema'
    ORDER BY n.nspname, c.relname LIMIT 129"""


@dataclass(frozen=True)
class Expected:
    project_id: str
    environment_id: str
    service_id: str
    host: str
    port: int
    database: str
    schema: str


class StopCheck(Exception):
    def __init__(self, reason):
        self.reason = reason  # Fixed codes only; never input or exception text.


def outcome(status, reason, **details):
    return dict(status=status, reason=reason,
                scope="service_environment_and_database_metadata_only",
                railway_identity_verified_externally=False,
                backend_worker_connection_verified=False, **details)


def canonical_uuid(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise StopCheck("EXECUTION_IDENTIFIERS_INVALID") from None


def normalize_host(host):
    if not isinstance(host, str) or not host or host != host.strip():
        raise StopCheck("HOST_INVALID")
    host = host.lower().rstrip(".")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", host):
            raise StopCheck("HOST_INVALID") from None
        if host == "localhost" or host.endswith(".localhost"):
            raise StopCheck("LOOPBACK_TARGET")
    else:
        mapped = getattr(address, "ipv4_mapped", None)
        if address.is_loopback or address.is_unspecified or (mapped is not None and mapped.is_loopback):
            raise StopCheck("LOOPBACK_TARGET")
        host = str(address)
    return host


def connection_parameters(expected, environment):
    from sqlalchemy.engine import make_url

    for key, value in (("RAILWAY_PROJECT_ID", expected.project_id),
                       ("RAILWAY_ENVIRONMENT_ID", expected.environment_id),
                       ("RAILWAY_SERVICE_ID", expected.service_id)):
        if not environment.get(key):
            raise StopCheck("EXECUTION_IDENTIFIERS_MISSING")
        if canonical_uuid(environment[key]) != canonical_uuid(value):
            raise StopCheck("EXECUTION_IDENTIFIERS_MISMATCH")
    if environment.get("APP_ENV") != "production":
        raise StopCheck("APP_ENV_NOT_PRODUCTION")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,62}", expected.schema) or expected.schema.startswith("pg_") or expected.schema == "information_schema":
        raise StopCheck("EXPECTED_SCHEMA_INVALID")
    if any(environment.get(key) for key in AMBIGUOUS_ENV):
        raise StopCheck("LIBPQ_TARGET_OVERRIDES_PRESENT")
    raw = environment.get("DATABASE_URL")
    if not raw:
        raise StopCheck("DATABASE_URL_MISSING")
    try:
        url = make_url(raw)
        port = url.port
    except Exception:
        raise StopCheck("DATABASE_URL_INVALID") from None
    if url.drivername not in {"postgres", "postgresql", "postgresql+psycopg"}:
        raise StopCheck("DATABASE_DRIVER_UNSUPPORTED")
    if not url.host or not url.database or port is None or not url.username or not url.password:
        raise StopCheck("CONNECTION_FIELDS_INCOMPLETE")
    # libpq expands dbname containing '=' or a PostgreSQL URI as conninfo,
    # potentially overriding separately supplied host/port/auth parameters.
    if "=" in url.database or url.database.startswith(("postgresql://", "postgres://")):
        raise StopCheck("DATABASE_NAME_CONNINFO_NOT_ALLOWED")
    if not 1 <= port <= 65535 or not 1 <= expected.port <= 65535:
        raise StopCheck("PORT_INVALID")
    host = normalize_host(url.host)
    if host != normalize_host(expected.host) or port != expected.port or url.database != expected.database:
        raise StopCheck("CONNECTION_TARGET_MISMATCH")
    if set(url.query) - TLS_PARAMETERS or any(not isinstance(value, str) or not value for value in url.query.values()):
        raise StopCheck("URL_PARAMETERS_NOT_APPROVED")
    # Explicit target/auth fields; no conninfo string or implicit service/host override.
    return dict(host=host, port=port, dbname=url.database, user=url.username, password=url.password,
                **url.query, connect_timeout=5, autocommit=True,
                application_name="futanalysis_read_only_probe")


def milliseconds(value):
    match = re.fullmatch(r"([0-9]+)(ms|s|min)", value)
    return int(match[1]) * {"ms": 1, "s": 1000, "min": 60000}[match[2]] if match else None


def read_metadata(cursor, expected, environment, base_dir):
    from psycopg import sql

    cursor.execute(POLICY_QUERY)
    read_only, isolation, statement, lock, idle, database, version, server_address = cursor.fetchone()
    if (read_only, isolation, milliseconds(statement), milliseconds(lock), milliseconds(idle)) != (
        "on", "repeatable read", 5000, 1500, 10000
    ):
        raise StopCheck("TRANSACTION_POLICY_NOT_ENFORCED")
    if database != expected.database:
        raise StopCheck("CONNECTED_DATABASE_MISMATCH")
    if not server_address:
        raise StopCheck("SERVER_ADDRESS_UNCONFIRMED")
    normalize_host(server_address)  # Actual address checked but never printed.
    if not re.fullmatch(r"[0-9]{5,6}", version):
        raise StopCheck("SERVER_VERSION_UNEXPECTED")
    cursor.execute(CATALOG_QUERY, (list(TABLES),))
    rows = cursor.fetchall()
    if len(rows) >= 129:
        raise StopCheck("CATALOG_RESULT_AMBIGUOUS")
    present = set()
    for schema, table, kind, can_select in rows:
        if schema != expected.schema or table in present:
            raise StopCheck("TABLE_SCHEMA_AMBIGUOUS_OR_UNEXPECTED")
        if table not in TABLES or kind not in {"r", "p"}:
            raise StopCheck("RELATION_TYPE_UNEXPECTED")
        if not can_select:
            raise StopCheck("TABLE_SELECT_NOT_PERMITTED")
        present.add(table)
    if "alembic_version" not in present:
        raise StopCheck("ALEMBIC_TABLE_MISSING")
    cursor.execute(sql.SQL("SELECT version_num FROM {}.{} LIMIT 2").format(
        sql.Identifier(expected.schema), sql.Identifier("alembic_version")))
    revisions = cursor.fetchall()
    if not revisions:
        raise StopCheck("ALEMBIC_REVISION_MISSING")
    if len(revisions) != 1:
        raise StopCheck("ALEMBIC_REVISIONS_MULTIPLE")
    revision = revisions[0][0]
    if revision not in KNOWN_REVISIONS:
        raise StopCheck("ALEMBIC_REVISION_UNRECOGNIZED")
    required = {"alembic_version", *CORE}
    if revision in {"0006", "0007"}:
        required.update(AUTH)
    if revision == "0007":
        required.update(COMPETITION)
    if present != required:
        raise StopCheck("REVISION_TABLES_INCONSISTENT")
    commit = environment.get("RAILWAY_GIT_COMMIT_SHA", "")
    return outcome("CONFIRMED", "READ_ONLY_CHECKS_COMPLETED",
                   environment_identifiers_match=True, connection_target_matches_operator_input=True,
                   fresh_database_connection=True, app_env="production", schema=expected.schema,
                   transaction=dict(read_only=True, isolation="repeatable read", statement_timeout_ms=5000,
                                    lock_timeout_ms=1500, idle_timeout_ms=10000, completion="rollback"),
                   server_version_num=int(version), alembic_revision=revision,
                   table_schemas={table: expected.schema for table in sorted(present)},
                   competition_tables={table: table in present for table in COMPETITION},
                   deployed_commit=commit if re.fullmatch(r"[0-9a-fA-F]{40}", commit) else None,
                   migration_0007_in_image=(base_dir / "alembic/versions/0007_competitions.py").is_file(),
                   competition_api_in_image=(base_dir / "app/competition_api.py").is_file())


def error_reason(error):
    state = getattr(error, "sqlstate", None)
    state = state if isinstance(state, str) else None
    if state == "42501":
        return "PERMISSION_DENIED"
    if state == "57014":
        return "STATEMENT_TIMEOUT_OR_CANCELLED"
    if state == "55P03":
        return "LOCK_NOT_AVAILABLE_OR_TIMEOUT"
    if state in {"28000", "28P01"}:
        return "AUTHENTICATION_FAILED"
    if isinstance(error, ImportError):
        return "DEPENDENCY_UNAVAILABLE"
    if isinstance(state, str) and state.startswith("08"):
        return "CONNECTION_FAILED"
    return "DIAGNOSTIC_EXECUTION_FAILED"


def probe(expected, *, environment=None, connect_factory=None, base_dir=None):
    environment = os.environ if environment is None else environment
    connection, started = None, False
    try:
        parameters = connection_parameters(expected, environment)
        if connect_factory is None:
            from psycopg import connect
            connect_factory = connect
        connection = connect_factory(**parameters)
        with connection.cursor() as cursor:
            cursor.execute(BEGIN)
            started = True
            for command in SETTINGS:
                cursor.execute(command)
            result = read_metadata(cursor, expected, environment, base_dir or Path.cwd())
    except StopCheck as error:
        result = outcome("UNCONFIRMED", error.reason)
    except Exception as error:
        result = outcome("ERROR", error_reason(error))
    finally:
        if connection is not None:
            try:
                if started:
                    connection.execute("ROLLBACK")
            except Exception:
                result = outcome("ERROR", "TRANSACTION_CLEANUP_FAILED")
            finally:
                try:
                    connection.close()
                except Exception:
                    result = outcome("ERROR", "CONNECTION_CLEANUP_FAILED")
    return result


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes invalid arguments, possibly exposing secrets.
        print(json.dumps(outcome("ERROR", "ARGUMENTS_INVALID")))
        raise SystemExit(2)


def main(argv=None):
    parser = SafeArgumentParser(description=__doc__)
    for name in ("project-id", "environment-id", "service-id", "host", "database", "schema"):
        parser.add_argument(f"--expected-{name}", required=True)
    parser.add_argument("--expected-port", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        result = probe(Expected(**{key.removeprefix("expected_"): value for key, value in vars(args).items()}))
    except Exception:
        result = outcome("ERROR", "DIAGNOSTIC_EXECUTION_FAILED")
    print(json.dumps(result, indent=2))
    return {"CONFIRMED": 0, "UNCONFIRMED": 1, "ERROR": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
