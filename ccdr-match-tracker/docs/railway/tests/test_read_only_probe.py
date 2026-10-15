"""Local unit tests only. No app imports, dotenv, environment edits or DB access."""
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import replace
import importlib.util
import ast
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

import psycopg
from sqlalchemy.engine import URL

SCRIPT = Path(__file__).resolve().parents[1] / "read_only_probe.py"
spec = importlib.util.spec_from_file_location("isolated_read_only_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)

PROJECT = "11111111-1111-4111-8111-111111111111"
ENVIRONMENT = "22222222-2222-4222-8222-222222222222"
SERVICE = "33333333-3333-4333-8333-333333333333"
SECRET = "SENTINEL_NOT_A_REAL_PASSWORD"
EXPECTED = probe.Expected(PROJECT, ENVIRONMENT, SERVICE, "db.example.invalid", 5432, "test_database", "public")


def environment(query=None, **updates):
    url = URL.create("postgresql", username="synthetic_user", password=SECRET,
                     host=EXPECTED.host, port=EXPECTED.port, database=EXPECTED.database, query=query or {})
    return {"RAILWAY_PROJECT_ID": PROJECT, "RAILWAY_ENVIRONMENT_ID": ENVIRONMENT,
            "RAILWAY_SERVICE_ID": SERVICE, "APP_ENV": "production",
            "DATABASE_URL": url.render_as_string(hide_password=False), **updates}


class DatabaseFailure(Exception):
    def __init__(self, sqlstate=None):
        super().__init__(SECRET)
        self.sqlstate = sqlstate


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.last = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, parameters=None):
        rendered = query if isinstance(query, str) else query.as_string()
        self.last = rendered
        self.connection.commands.append(rendered)
        self.connection.parameters.append(parameters)
        if rendered == self.connection.fail_at:
            raise self.connection.failure

    def fetchone(self):
        if self.last != probe.POLICY_QUERY:
            raise AssertionError("Unexpected fetchone")
        return self.connection.policy

    def fetchall(self):
        if self.last == probe.CATALOG_QUERY:
            return self.connection.tables
        if self.last.startswith("SELECT version_num FROM "):
            return self.connection.revisions
        raise AssertionError("Unexpected fetchall")


class FakeConnection:
    def __init__(self, revision="0006", schema="public"):
        self.commands, self.parameters = [], []
        self.closed, self.fail_at = False, None
        self.failure = DatabaseFailure()
        self.close_failure = False
        self.policy = ("on", "repeatable read", "5s", "1500ms", "10s", EXPECTED.database, "180006", "10.42.0.2")
        self.revisions = [(revision,)]
        names = ["alembic_version", *probe.CORE]
        if revision in {"0006", "0007"}:
            names.extend(probe.AUTH)
        if revision == "0007":
            names.extend(probe.COMPETITION)
        self.tables = [(schema, name, "r", True) for name in names]

    def cursor(self):
        return FakeCursor(self)

    def execute(self, query):
        self.commands.append(query)
        if query == self.fail_at:
            raise self.failure

    def close(self):
        self.closed = True
        if self.close_failure:
            raise DatabaseFailure()


class ProbeTests(unittest.TestCase):
    def setUp(self):
        # Any accidental use of the real connector fails, even on developer machines.
        guard = patch.object(psycopg, "connect", side_effect=AssertionError("Real connection forbidden"))
        self.addCleanup(guard.stop)
        self.real_connect = guard.start()

    def run_probe(self, connection=None, expected=EXPECTED, env=None):
        connection = connection or FakeConnection()
        connector = Mock(return_value=connection)
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = probe.probe(expected, environment=environment() if env is None else env,
                                 connect_factory=connector, base_dir=SCRIPT.parent)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(errors.getvalue(), "")
        encoded = json.dumps(result)
        self.assertNotIn(SECRET, encoded)
        self.assertNotIn("synthetic_user", encoded)
        self.assertNotIn("postgresql://", encoded)
        self.real_connect.assert_not_called()
        return result, connection, connector

    def assert_stops_before_connect(self, reason, *, expected=EXPECTED, env=None):
        result, connection, connector = self.run_probe(expected=expected, env=env)
        self.assertEqual(result["status"], "UNCONFIRMED")
        self.assertEqual(result["reason"], reason)
        connector.assert_not_called()
        self.assertEqual(connection.commands, [])

    def test_one_explicit_transaction_local_settings_rollback_and_close(self):
        result, connection, connector = self.run_probe()
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertEqual(result["alembic_revision"], "0006")
        self.assertFalse(result["railway_identity_verified_externally"])
        self.assertFalse(result["backend_worker_connection_verified"])
        revision_sql = 'SELECT version_num FROM "public"."alembic_version" LIMIT 2'
        self.assertEqual(connection.commands, [probe.BEGIN, *probe.SETTINGS, probe.POLICY_QUERY, probe.CATALOG_QUERY, revision_sql, "ROLLBACK"])
        self.assertTrue(connection.closed)
        self.assertEqual(connector.call_count, 1)
        self.assertTrue(connector.call_args.kwargs["autocommit"])
        self.assertEqual(connector.call_args.kwargs["connect_timeout"], 5)
        self.assertNotIn("options", connector.call_args.kwargs)
        self.assertIn("SET LOCAL row_security = off", connection.commands)

    def test_does_not_assume_revision_0006(self):
        for revision in ("0001", "0005", "0007"):
            with self.subTest(revision=revision):
                result, _, _ = self.run_probe(FakeConnection(revision=revision))
                self.assertEqual(result["status"], "CONFIRMED")
                self.assertEqual(result["alembic_revision"], revision)

    def test_database_name_cannot_expand_as_libpq_conninfo(self):
        for database in ("host=other.invalid dbname=other", "postgresql://other.invalid/other", "postgres://other.invalid/other"):
            url = URL.create("postgresql", username="synthetic_user", password=SECRET,
                             host=EXPECTED.host, port=EXPECTED.port, database=database)
            self.assert_stops_before_connect("DATABASE_NAME_CONNINFO_NOT_ALLOWED",
                expected=replace(EXPECTED, database=database),
                env=environment(DATABASE_URL=url.render_as_string(hide_password=False)))

    def test_table_inventory_matches_actual_migration_history_without_execution(self):
        directory = SCRIPT.parents[2] / "backend/alembic/versions"
        present = set()
        for number in range(1, 8):
            path, = directory.glob(f"{number:04d}_*.py")
            tree = ast.parse(path.read_text(encoding="utf-8"))
            assignments = {node.targets[0].id: ast.literal_eval(node.value)
                           for node in tree.body if isinstance(node, ast.Assign)
                           and isinstance(node.targets[0], ast.Name)
                           and node.targets[0].id in {"revision", "down_revision"}}
            self.assertEqual(assignments["revision"], f"{number:04d}")
            self.assertEqual(assignments["down_revision"], f"{number - 1:04d}" if number > 1 else None)
            upgrade, = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "upgrade"]
            for node in ast.walk(upgrade):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "create_table":
                        present.add(ast.literal_eval(node.args[0]))
                    self.assertNotEqual(node.func.attr, "drop_table")
                    if node.func.attr == "execute" and isinstance(node.args[0], ast.Constant):
                        self.assertNotRegex(str(node.args[0].value).upper(), r"\b(CREATE|DROP)\s+TABLE\b")
            fake = FakeConnection(revision=f"{number:04d}")
            self.assertEqual(present, {row[1] for row in fake.tables} - {"alembic_version"})
            result, _, _ = self.run_probe(fake)
            self.assertEqual(result["status"], "CONFIRMED")

    def test_explicit_schema_and_quoted_identifier(self):
        result, connection, _ = self.run_probe(FakeConnection(schema="League"), expected=replace(EXPECTED, schema="League"))
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertIn('SELECT version_num FROM "League"."alembic_version" LIMIT 2', connection.commands)

    def test_missing_or_mismatching_environment_identity(self):
        for key in ("RAILWAY_PROJECT_ID", "RAILWAY_ENVIRONMENT_ID", "RAILWAY_SERVICE_ID"):
            for value, reason in (("", "EXECUTION_IDENTIFIERS_MISSING"),
                                  ("44444444-4444-4444-8444-444444444444", "EXECUTION_IDENTIFIERS_MISMATCH"),
                                  (SECRET, "EXECUTION_IDENTIFIERS_INVALID")):
                with self.subTest(key=key, reason=reason):
                    self.assert_stops_before_connect(reason, env=environment(**{key: value}))

    def test_requires_production_and_no_dotenv_fallback(self):
        self.assert_stops_before_connect("APP_ENV_NOT_PRODUCTION", env=environment(APP_ENV="development"))
        self.assert_stops_before_connect("DATABASE_URL_MISSING", env=environment(DATABASE_URL=""))

    def test_host_port_and_database_require_independent_operator_match(self):
        for changes in ({"host": "other.example.invalid"}, {"port": 6432}, {"database": "another_database"}):
            with self.subTest(changes=changes):
                self.assert_stops_before_connect("CONNECTION_TARGET_MISMATCH", expected=replace(EXPECTED, **changes))

    def test_loopback_aliases_and_multi_host_are_rejected(self):
        for host in ("localhost", "localhost.", "db.localhost", "127.0.0.2", "::1", "::ffff:127.0.0.1", "0.0.0.0", "::"):
            with self.subTest(host=host):
                url = URL.create("postgresql", username="synthetic_user", password=SECRET, host=host, port=5432, database=EXPECTED.database)
                self.assert_stops_before_connect("LOOPBACK_TARGET", env=environment(DATABASE_URL=url.render_as_string(hide_password=False)))
        self.assert_stops_before_connect("HOST_INVALID", expected=replace(EXPECTED, host="one.invalid,two.invalid"))

    def test_connection_override_parameters_and_ambiguous_environment(self):
        for key in ("host", "hostaddr", "port", "dbname", "service", "options", "connect_timeout"):
            with self.subTest(query=key):
                self.assert_stops_before_connect("URL_PARAMETERS_NOT_APPROVED", env=environment(query={key: SECRET}))
        for key in probe.AMBIGUOUS_ENV:
            with self.subTest(environment=key):
                self.assert_stops_before_connect("LIBPQ_TARGET_OVERRIDES_PRESENT", env=environment(**{key: SECRET}))
        self.assert_stops_before_connect("URL_PARAMETERS_NOT_APPROVED", env=environment(query={"sslmode": ("require", "disable")}))

    def test_tls_parameters_are_preserved_without_changing_environment(self):
        env = environment(query={"sslmode": "verify-full", "channel_binding": "require"})
        before = dict(env)
        result, _, connector = self.run_probe(env=env)
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertEqual(connector.call_args.kwargs["sslmode"], "verify-full")
        self.assertEqual(connector.call_args.kwargs["channel_binding"], "require")
        self.assertEqual(env, before)

    def test_invalid_or_incomplete_url_is_sanitized(self):
        for raw, reason in ((SECRET, "DATABASE_URL_INVALID"),
                            ("sqlite:///synthetic", "DATABASE_DRIVER_UNSUPPORTED"),
                            ("postgresql://db.example.invalid/test_database", "CONNECTION_FIELDS_INCOMPLETE")):
            with self.subTest(reason=reason):
                self.assert_stops_before_connect(reason, env=environment(DATABASE_URL=raw))

    def test_unexpected_schema_or_duplicate_table_stops_before_revision_read(self):
        for rows in ([('other_schema', *FakeConnection().tables[0][1:])],
                     [*FakeConnection().tables, ('other_schema', 'alembic_version', 'r', True)]):
            connection = FakeConnection()
            connection.tables = rows
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["reason"], "TABLE_SCHEMA_AMBIGUOUS_OR_UNEXPECTED")
            self.assertFalse(any(command.startswith("SELECT version_num") for command in connection.commands))
            self.assertEqual(connection.commands[-1], "ROLLBACK")
            self.assertTrue(connection.closed)

    def test_schema_input_cannot_be_interpolated_as_sql(self):
        self.assert_stops_before_connect("EXPECTED_SCHEMA_INVALID", expected=replace(EXPECTED, schema='public"; SELECT 1; --'))

    def test_missing_revision_table_or_select_permission_or_view(self):
        for variant, reason in (("missing", "ALEMBIC_TABLE_MISSING"),
                                ("permission", "TABLE_SELECT_NOT_PERMITTED"),
                                ("view", "RELATION_TYPE_UNEXPECTED")):
            connection = FakeConnection()
            if variant == "missing":
                connection.tables = connection.tables[1:]
            else:
                connection.tables[0] = ("public", "alembic_version", "v" if variant == "view" else "r", variant != "permission")
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["reason"], reason)
            self.assertFalse(any(command.startswith("SELECT version_num") for command in connection.commands))

    def test_absent_multiple_and_unrecognized_revisions(self):
        for revisions, reason in (([], "ALEMBIC_REVISION_MISSING"),
                                  ([("0006",), ("0007",)], "ALEMBIC_REVISIONS_MULTIPLE"),
                                  ([(SECRET,)], "ALEMBIC_REVISION_UNRECOGNIZED")):
            connection = FakeConnection()
            connection.revisions = revisions
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["status"], "UNCONFIRMED")
            self.assertEqual(result["reason"], reason)
            self.assertEqual(connection.commands[-1], "ROLLBACK")

    def test_revision_and_table_presence_must_be_consistent(self):
        connection = FakeConnection()
        connection.tables.append(("public", "competitions", "r", True))
        result, _, _ = self.run_probe(connection)
        self.assertEqual(result["reason"], "REVISION_TABLES_INCONSISTENT")

    def test_server_policy_and_database_are_checked_before_catalog(self):
        for index, value, reason in ((0, "off", "TRANSACTION_POLICY_NOT_ENFORCED"),
                                    (1, "read committed", "TRANSACTION_POLICY_NOT_ENFORCED"),
                                    (2, "0", "TRANSACTION_POLICY_NOT_ENFORCED"),
                                    (5, "wrong_database", "CONNECTED_DATABASE_MISMATCH"),
                                    (7, "127.0.0.1", "LOOPBACK_TARGET")):
            connection = FakeConnection()
            policy = list(connection.policy); policy[index] = value; connection.policy = tuple(policy)
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["reason"], reason)
            self.assertNotIn(probe.CATALOG_QUERY, connection.commands)

    def test_connection_failure_never_echoes_exception_or_url(self):
        connector = Mock(side_effect=DatabaseFailure("08001"))
        with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
            result = probe.probe(EXPECTED, environment=environment(), connect_factory=connector)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["reason"], "CONNECTION_FAILED")
        self.assertNotIn(SECRET, json.dumps(result) + output.getvalue() + errors.getvalue())

    def test_timeout_permission_and_auth_errors_stop_and_cleanup(self):
        for state, reason in (("57014", "STATEMENT_TIMEOUT_OR_CANCELLED"),
                              ("55P03", "LOCK_NOT_AVAILABLE_OR_TIMEOUT"),
                              ("42501", "PERMISSION_DENIED"), ("28P01", "AUTHENTICATION_FAILED")):
            connection = FakeConnection()
            connection.fail_at, connection.failure = probe.POLICY_QUERY, DatabaseFailure(state)
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["status"], "ERROR")
            self.assertEqual(result["reason"], reason)
            self.assertNotIn(probe.CATALOG_QUERY, connection.commands)
            self.assertEqual(connection.commands[-1], "ROLLBACK")
            self.assertTrue(connection.closed)

    def test_rls_guard_or_revision_permission_failure_stops_and_rolls_back(self):
        for command in ("SET LOCAL row_security = off", 'SELECT version_num FROM "public"."alembic_version" LIMIT 2'):
            connection = FakeConnection()
            connection.fail_at = command
            connection.failure = DatabaseFailure("42501")
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["status"], "ERROR")
            self.assertEqual(result["reason"], "PERMISSION_DENIED")
            self.assertEqual(connection.commands[-1], "ROLLBACK")
            self.assertTrue(connection.closed)

    def test_rollback_or_close_failure_cannot_report_confirmed(self):
        for stage, reason in (("rollback", "TRANSACTION_CLEANUP_FAILED"), ("close", "CONNECTION_CLEANUP_FAILED")):
            connection = FakeConnection()
            if stage == "rollback":
                connection.fail_at = "ROLLBACK"
            else:
                connection.close_failure = True
            result, connection, _ = self.run_probe(connection)
            self.assertEqual(result["status"], "ERROR")
            self.assertEqual(result["reason"], reason)
            self.assertTrue(connection.closed)

    def test_cli_exit_status_and_json_only(self):
        argv = ["--expected-project-id", PROJECT, "--expected-environment-id", ENVIRONMENT,
                "--expected-service-id", SERVICE, "--expected-host", EXPECTED.host,
                "--expected-port", "5432", "--expected-database", EXPECTED.database, "--expected-schema", "public"]
        for status, exit_code in (("CONFIRMED", 0), ("UNCONFIRMED", 1), ("ERROR", 2)):
            with patch.object(probe, "probe", return_value=probe.outcome(status, "TEST")), redirect_stdout(io.StringIO()) as output:
                actual = probe.main(argv)
            self.assertEqual(actual, exit_code)
            self.assertEqual(json.loads(output.getvalue())["status"], status)

    def test_cli_invalid_arguments_do_not_echo_input(self):
        with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
            with self.assertRaises(SystemExit) as raised:
                probe.main(["--unexpected", SECRET])
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(json.loads(output.getvalue())["reason"], "ARGUMENTS_INVALID")
        self.assertNotIn(SECRET, output.getvalue() + errors.getvalue())


if __name__ == "__main__":
    unittest.main()
