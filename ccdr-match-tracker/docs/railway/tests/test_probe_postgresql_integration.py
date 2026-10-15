"""Opt-in disposable cluster only; never accepts a URL or existing database.

Prepared, not executed. Direct invocation with --run-disposable is required.
No Alembic execution: fixtures reproduce table names, not the full schema.
"""
from dataclasses import replace
from pathlib import Path
import shutil
import os
import json
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote, quote_plus, unquote, unquote_plus
import unicodedata
from unittest.mock import patch

import psycopg
from psycopg import sql

from test_read_only_probe import probe, EXPECTED, environment

ENABLED = False
OUTPUT_LIMIT = 65536


def sanitize_output(value, known_secrets=()):
    """Fail closed per line: never preserve fragments of a sensitive line."""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    value = value or ""
    # Ambiguous multiline credential blocks must not preserve their value lines.
    if re.search(r"(?im)(?:password|passwd|token|secret|authorization)\s*[:=]\s*$", value):
        return "[REDACTED_MULTILINE_CREDENTIAL_OUTPUT]"
    if re.search(r"-----BEGIN .*PRIVATE KEY-----", value):
        return "[REDACTED_PRIVATE_KEY_OUTPUT]"
    variants = {variant for secret in known_secrets if secret for variant in
                (secret, quote(secret, safe=""), quote_plus(secret), json.dumps(secret)[1:-1])}
    sensitive = re.compile(r"(?i)([a-z][a-z0-9+.-]{0,31}://|(?:password|passwd|pwd|passfile|pwfile|"
                           r"token|secret|authorization|credential|api[_-]?key|cookie)|\bbearer\s+|"
                           r"\b(?:host|hostaddr|dbname|user|username|service|sslkey)\s*=)")
    lines = []
    # Redact BEFORE truncating: truncation must not expose a partial secret.
    for line in value.splitlines():
        inspected = unicodedata.normalize("NFKC", unquote_plus(unquote(line)))
        inspected = "".join(character for character in inspected if not unicodedata.category(character).startswith("C"))
        if sensitive.search(inspected) or any(secret in line or secret in inspected for secret in variants):
            lines.append("[REDACTED_SENSITIVE_LINE]")
        else:
            lines.append("".join(character if character.isprintable() else "?" for character in line))
    result = "\n".join(lines)
    return result[:OUTPUT_LIMIT] + ("\n[TRUNCATED]" if len(result) > OUTPUT_LIMIT else "")


@unittest.skipUnless(ENABLED, "Requires explicit --run-disposable; no existing DB is accepted")
class DisposablePostgreSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.initdb = shutil.which("initdb")
        cls.pg_ctl = shutil.which("pg_ctl")
        if not cls.initdb or not cls.pg_ctl:
            raise unittest.SkipTest("initdb and pg_ctl are required; nothing installed automatically")
        if Path(cls.initdb).parent.resolve() != Path(cls.pg_ctl).parent.resolve():
            raise RuntimeError("PostgreSQL binaries must belong to the same installation")
        # Inspect names only; do not read inherited credentials or allow libpq
        # service/options settings to affect even the disposable connections.
        if any(key.upper().startswith("PG") for key in os.environ):
            raise RuntimeError("Inherited PG variables present; review isolation without changing application settings")
        cls.process_environment = {key: os.environ[key] for key in os.environ
                                   if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC", "PATHEXT", "SYSTEMDRIVE"}}
        cls.directory = Path(tempfile.mkdtemp(prefix="futanalysis_probe_disposable_"))
        cls.root_directory = cls.directory.resolve()
        cls.root_identity = (cls.directory.stat().st_dev, cls.directory.stat().st_ino)
        cls.observed_server_identity = None
        cls.data = cls.directory / "data"
        cls.password = secrets.token_urlsafe(32)
        cls.admin_user = "fixture_" + secrets.token_hex(12)
        cls.password_file = cls.directory / "initdb-password"
        cls.addClassCleanup(cls.stop)
        cls.password_file.write_text(cls.password + "\n", encoding="utf-8")
        cls.password_file.chmod(0o600)
        # Register before initdb/start, including setup failure and KeyboardInterrupt.
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            cls.port = reservation.getsockname()[1]
        try:
            cls.command([cls.initdb, "-D", str(cls.data), "-U", cls.admin_user,
                         "-A", "scram-sha-256", "--pwfile", str(cls.password_file), "--no-locale", "--encoding=UTF8"])
        finally:
            cls.verify_root()
            cls.password_file.unlink(missing_ok=True)
        with (cls.data / "postgresql.conf").open("a", encoding="utf-8") as configuration:
            configuration.write("\nunix_socket_directories = ''\nlog_statement = 'none'\nlog_min_error_statement = 'panic'\n")
        # Fail before launch if the pg_ctl -l destination cannot be created.
        with cls.diagnostic_path("server.log").open("xb"):
            pass
        cls.diagnostic_path("server.log").chmod(0o600)
        cls.command([cls.pg_ctl, "-D", str(cls.data), "-l", str(cls.directory / "server.log"),
                     "-o", f"-h 127.0.0.1 -p {cls.port}", "-t", "30", "-w", "start"])
        cls.verify_owned_server()

    @classmethod
    def command(cls, args):
        cls.diagnostic_path("server.log")
        cls.diagnostic_path("command-diagnostics.jsonl")
        stage = "start" if "start" in args else "stop" if "stop" in args else "initdb" if Path(args[0]).stem == "initdb" else "command"
        record = {"stage": stage, "returncode": None, "stdout": "", "stderr": ""}
        cls.command_sequence = getattr(cls, "command_sequence", 0) + 1
        names = [f"command-{cls.command_sequence}.{stream}.raw" for stream in ("stdout", "stderr")]
        from contextlib import ExitStack
        try:
            with ExitStack() as stack:
                files = []
                for name in names:
                    path = cls.diagnostic_path(name)
                    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
                    files.append(stack.enter_context(os.fdopen(fd, "wb")))
                completed = subprocess.run(args, stdout=files[0], stderr=files[1],
                                           timeout=45, env=cls.process_environment)
                record.update(returncode=completed.returncode, event="completed")
        except subprocess.TimeoutExpired as error:
            record.update(event="timeout")
        except OSError as error:
            record.update(event="os_error", errno=error.errno)  # No exception text/arguments.
        for name, stream in zip(names, ("stdout", "stderr")):
            record[stream], record[stream + "_truncated"] = cls.read_excerpt(name)
        record["raw_capture_files"] = names
        cls.save_diagnostic(record)
        if record["event"] != "completed" or record["returncode"] != 0:
            raise RuntimeError("Disposable cluster subprocess failed or timed out; sanitized details in command-diagnostics.jsonl; no fallback") from None

    @classmethod
    def diagnostic_path(cls, name):
        cls.verify_root()
        if name not in {"server.log", "command-diagnostics.jsonl"} and not re.fullmatch(r"command-[0-9]+\.(stdout|stderr)\.raw", name):
            raise RuntimeError("Diagnostic filename not approved")
        path = cls.directory / name
        if path.is_symlink() or path.resolve().parent != cls.directory.resolve():
            raise RuntimeError("Diagnostic path outside owned directory or symlink; stop")
        if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
            raise RuntimeError("Diagnostic file ownership ambiguous; stop")
        return path

    @classmethod
    def verify_root(cls):
        try:
            current = cls.directory.stat()
            if (cls.directory.is_symlink() or getattr(cls.directory, "is_junction", lambda: False)()
                    or cls.directory.resolve() != cls.root_directory
                    or (current.st_dev, current.st_ino) != cls.root_identity):
                raise ValueError()
        except (OSError, ValueError):
            raise RuntimeError("Temporary directory identity changed or symlink; stop") from None

    @classmethod
    def read_excerpt(cls, name):
        path = cls.diagnostic_path(name)
        if not path.exists():
            return b"", False
        expected = path.stat(follow_symlinks=False)
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as source:
            actual = os.fstat(source.fileno())
            if ((expected.st_dev, expected.st_ino) != (actual.st_dev, actual.st_ino)
                    or actual.st_nlink != 1):
                raise RuntimeError("Capture identity changed before read; stop")
            cls.verify_root()
            raw = source.read(OUTPUT_LIMIT + 1)
        truncated = len(raw) > OUTPUT_LIMIT
        if truncated:
            raw = raw[:OUTPUT_LIMIT].rsplit(b"\n", 1)[0] if b"\n" in raw[:OUTPUT_LIMIT] else b""
        return raw, truncated

    @classmethod
    def save_diagnostic(cls, record):
        try:
            secrets_to_remove = (cls.password, cls.admin_user)
            record = dict(record)
            for stream in ("stdout", "stderr"):
                record[stream] = sanitize_output(record.get(stream), secrets_to_remove)
            log = cls.diagnostic_path("server.log")
            record["server_log_exists"] = log.exists()
            if log.exists():
                raw, truncated = cls.read_excerpt("server.log")
                record["server_log_excerpt"] = sanitize_output(raw, secrets_to_remove)
                record["server_log_truncated"] = truncated
            record["pid_file_exists"] = (cls.data / "postmaster.pid").exists()
            record["port_candidate"] = getattr(cls, "port", None)
            path = cls.diagnostic_path("command-diagnostics.jsonl")
            fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as destination:
                destination.write(json.dumps(record, ensure_ascii=True) + "\n")
            path.chmod(0o600)
        except (OSError, ValueError):
            raise RuntimeError("Diagnostic persistence failed; stop and preserve owned directory") from None

    @classmethod
    def stop(cls):
        try:
            cls.stop_server()
        finally:
            cls.verify_root()
            cls.password_file.unlink(missing_ok=True)

    @classmethod
    def stop_server(cls):
        # No existing cluster fallback, arbitrary PID kill or recursive deletion.
        cls.verify_root()
        if not (cls.data / "postmaster.pid").exists():
            return  # initdb failed, or pg_ctl already shut the server down.
        cls.verify_owned_server()
        for mode in ("fast", "immediate"):
            cls.verify_owned_server()
            try:
                cls.command([cls.pg_ctl, "-D", str(cls.data), "-m", mode, "-t", "15", "-w", "stop"])
            except RuntimeError:
                if (cls.data / "postmaster.pid").exists():
                    continue
            if not (cls.data / "postmaster.pid").exists():
                return
        raise RuntimeError("Disposable cluster shutdown NOT confirmed; inspect retained test directory")

    @classmethod
    def verify_owned_server(cls):
        cls.verify_root()
        try:
            if cls.data.is_symlink() or getattr(cls.data, "is_junction", lambda: False)() or (cls.data / "postmaster.pid").is_symlink():
                raise ValueError()
            lines = (cls.data / "postmaster.pid").read_text(encoding="utf-8").splitlines()
            if (int(lines[0]) <= 0 or Path(lines[1]).resolve() != cls.data.resolve()
                    or int(lines[2]) <= 0 or int(lines[3]) != cls.port
                    or (cls.data / "postmaster.pid").stat().st_nlink != 1):
                raise ValueError()
            identity = (int(lines[0]), int(lines[2]), str(cls.data.resolve()), int(lines[3]))
            previous = getattr(cls, "observed_server_identity", None)
            if previous is not None and previous != identity:
                raise ValueError()
            cls.observed_server_identity = identity
        except (OSError, ValueError, IndexError):
            raise RuntimeError("Disposable server ownership not confirmed; no connection or stop attempted") from None

    @classmethod
    def connect(cls, database="postgres", user=None):
        cls.verify_owned_server()  # Check the owned server BEFORE opening a socket.
        connection = None
        try:
            connection = psycopg.connect(host="127.0.0.1", hostaddr="127.0.0.1", port=cls.port, dbname=database,
                               user=user or cls.admin_user, password=cls.password,
                               sslmode="disable", gssencmode="disable",
                               autocommit=True, connect_timeout=5,
                               options="-c default_transaction_read_only=on -c statement_timeout=5000 -c lock_timeout=1500")
            # Verify the fresh cluster before any fixture write.
            actual = connection.execute("SELECT pg_catalog.current_setting('data_directory')").fetchone()[0]
            if Path(actual).resolve() != cls.data.resolve():
                raise RuntimeError("Not the disposable cluster; stop before fixture writes")
            connection.execute("SET default_transaction_read_only = off")
        except Exception:
            if connection is not None:
                connection.close()
            raise RuntimeError("Disposable cluster identity could not be verified") from None
        return connection

    def setUp(self):
        # Unique fixture schema, deliberately retained in this disposable cluster.
        import uuid
        self.schema = "fixture_" + uuid.uuid4().hex
        self.database = "probe_" + uuid.uuid4().hex
        with self.connect() as connection:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database)))
        self.admin = self.connect(self.database)
        self.addCleanup(self.admin.close)
        self.admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        for table in ("alembic_version", *probe.CORE, *probe.AUTH):
            self.admin.execute(sql.SQL("CREATE TABLE {}.{} (version_num text)").format(
                sql.Identifier(self.schema), sql.Identifier(table)))
        self.admin.execute(sql.SQL("INSERT INTO {}.alembic_version VALUES ('0006')").format(sql.Identifier(self.schema)))

    def run_probe(self, *, user=None, cursor_hook=None):
        expected = replace(EXPECTED, schema=self.schema)
        connections = []

        def connector(**parameters):
            # Test-only adapter: production guard stays unchanged. A synthetic URL
            # is checked, then transport is forced to the cluster just created.
            connection = self.connect(self.database, user)
            connections.append(connection)
            return connection

        original = probe.normalize_host
        metadata = probe.read_metadata

        def read(cursor, expected, env, directory):
            if cursor_hook:
                cursor_hook(cursor)
            return metadata(cursor, expected, env, directory)

        # Policy query must match the real database. Host loopback exception is
        # strictly test-local, required because production deliberately rejects it.
        expected = replace(expected, database=self.database)
        env = environment()
        from sqlalchemy.engine import make_url
        env["DATABASE_URL"] = make_url(env["DATABASE_URL"]).set(database=expected.database).render_as_string(hide_password=False)
        with patch.object(probe, "normalize_host", side_effect=lambda host: host if host == "127.0.0.1" else original(host)), \
             patch.object(probe, "read_metadata", side_effect=read):
            result = probe.probe(expected, environment=env, connect_factory=connector)
        self.assertTrue(all(connection.closed for connection in connections))
        return result

    def test_real_catalog_explicit_schema_and_transaction(self):
        result = self.run_probe()
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertEqual(result["alembic_revision"], "0006")
        self.assertEqual(result["schema"], self.schema)

    def test_multiple_and_missing_revisions(self):
        query = sql.SQL("INSERT INTO {}.alembic_version VALUES ('0007')").format(sql.Identifier(self.schema))
        self.admin.execute(query)
        self.assertEqual(self.run_probe()["reason"], "ALEMBIC_REVISIONS_MULTIPLE")
        self.admin.execute(sql.SQL("DELETE FROM {}.alembic_version").format(sql.Identifier(self.schema)))
        self.assertEqual(self.run_probe()["reason"], "ALEMBIC_REVISION_MISSING")

    def test_wrong_schema(self):
        original_schema = self.schema
        self.schema = "absent_fixture_schema"
        self.assertEqual(self.run_probe()["reason"], "TABLE_SCHEMA_AMBIGUOUS_OR_UNEXPECTED")
        self.schema = original_schema

    def test_statement_timeout(self):
        result = self.run_probe(cursor_hook=lambda cursor: cursor.execute("SELECT pg_catalog.pg_sleep(6)"))
        self.assertEqual(result["reason"], "STATEMENT_TIMEOUT_OR_CANCELLED")

    def test_lock_timeout(self):
        with self.connect(self.database) as locker:
            locker.execute("BEGIN")
            locker.execute(sql.SQL("LOCK TABLE {}.alembic_version IN ACCESS EXCLUSIVE MODE").format(sql.Identifier(self.schema)))
            try:
                self.assertEqual(self.run_probe()["reason"], "LOCK_NOT_AVAILABLE_OR_TIMEOUT")
            finally:
                locker.execute("ROLLBACK")

    def test_snapshot_read_only_and_local_settings_rollback(self):
        with self.connect(self.database) as connection:
            before = connection.execute("SHOW statement_timeout").fetchone()
            connection.execute(probe.BEGIN)
            for command in probe.SETTINGS:
                connection.execute(command)
            query = sql.SQL("SELECT count(*) FROM {}.alembic_version").format(sql.Identifier(self.schema))
            self.assertEqual(connection.execute(query).fetchone()[0], 1)
            self.admin.execute(sql.SQL("INSERT INTO {}.alembic_version VALUES ('0007')").format(sql.Identifier(self.schema)))
            self.assertEqual(connection.execute(query).fetchone()[0], 1)
            with self.assertRaises(psycopg.errors.ReadOnlySqlTransaction):
                connection.execute(sql.SQL("INSERT INTO {}.alembic_version VALUES ('0005')").format(sql.Identifier(self.schema)))
            connection.execute("ROLLBACK")
            self.assertEqual(connection.execute("SHOW statement_timeout").fetchone(), before)
            self.assertEqual(connection.execute(query).fetchone()[0], 2)

    def test_insufficient_select_permission(self):
        role = "limited_" + self.schema
        self.admin.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role), sql.Literal(self.password)))
        self.admin.execute(sql.SQL("GRANT pg_read_all_settings TO {}").format(sql.Identifier(role)))
        self.admin.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
            sql.Identifier(self.schema), sql.Identifier(role)))
        self.assertEqual(self.run_probe(user=role)["reason"], "TABLE_SELECT_NOT_PERMITTED")

    def test_row_security_cannot_hide_an_alembic_head(self):
        role = "rls_" + self.schema
        self.admin.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role), sql.Literal(self.password)))
        # Test-only ability to read data_directory for the identity guard.
        self.admin.execute(sql.SQL("GRANT pg_read_all_settings TO {}").format(sql.Identifier(role)))
        self.admin.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(sql.Identifier(self.schema), sql.Identifier(role)))
        self.admin.execute(sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA {} TO {}").format(sql.Identifier(self.schema), sql.Identifier(role)))
        self.admin.execute(sql.SQL("INSERT INTO {}.alembic_version VALUES ('0007')").format(sql.Identifier(self.schema)))
        self.admin.execute(sql.SQL("ALTER TABLE {}.alembic_version ENABLE ROW LEVEL SECURITY").format(sql.Identifier(self.schema)))
        self.admin.execute(sql.SQL("CREATE POLICY hide_head ON {}.alembic_version USING (version_num = '0006')").format(sql.Identifier(self.schema)))
        self.assertEqual(self.run_probe(user=role)["reason"], "PERMISSION_DENIED")


if __name__ == "__main__":
    if sys.argv[1:] != ["--run-disposable"]:
        raise SystemExit("Not executed: explicit --run-disposable required")
    ENABLED = True
    DisposablePostgreSQLTests.__unittest_skip__ = False
    unittest.main(argv=[sys.argv[0]], failfast=True)
