"""Harness regressions: fake sockets/processes/connections, no PostgreSQL execution."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import json
import io
from contextlib import redirect_stdout, redirect_stderr
import unittest
from unittest.mock import Mock, patch

import test_probe_postgresql_integration as integration


class DisposableClusterSafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="probe_harness_unit_")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.harness = type("Harness", (integration.DisposablePostgreSQLTests,), {"_class_cleanups": []})
        self.harness.directory = self.root
        self.harness.root_directory = self.root.resolve()
        self.harness.root_identity = (self.root.stat().st_dev, self.root.stat().st_ino)
        self.harness.data = self.root / "data"
        self.harness.data.mkdir()
        self.harness.password_file = self.root / "initdb-password"
        self.harness.password = "SYNTHETIC_UNIT_VALUE"
        self.harness.admin_user = "fixture_unit"
        self.harness.port = 45678
        self.harness.pg_ctl = "pg_ctl"
        self.harness.process_environment = {"PATH": "synthetic"}
        for target in ("psycopg.connect", "subprocess.run", "socket.socket"):
            guard = patch("test_probe_postgresql_integration." + target,
                          side_effect=AssertionError("Real I/O forbidden"))
            self.addCleanup(guard.stop)
            guard.start()

    def pidfile(self, *, path=None, port=None):
        (self.harness.data / "postmaster.pid").write_text(
            f"1234\n{path or self.harness.data}\n123456\n{port or self.harness.port}\n", encoding="utf-8")

    def test_no_pid_means_no_network_or_stop_command(self):
        with patch.object(self.harness, "command") as command:
            self.harness.stop()
            command.assert_not_called()
        with self.assertRaises(RuntimeError):
            self.harness.connect()

    def test_wrong_pid_path_port_or_malformed_file_refuses_connection_and_stop(self):
        for value in ("bad", f"1234\n{self.root}\n123\n45678\n",
                      f"1234\n{self.harness.data}\n123\n5432\n"):
            (self.harness.data / "postmaster.pid").write_text(value)
            with self.assertRaises(RuntimeError):
                self.harness.connect()
            with self.assertRaises(RuntimeError):
                self.harness.stop()

    def test_data_directory_mismatch_closes_without_enabling_writes(self):
        self.pidfile()
        connection = Mock()
        connection.execute.return_value.fetchone.return_value = (str(self.root / "other"),)
        with patch.object(integration.psycopg, "connect", return_value=connection):
            with self.assertRaises(RuntimeError):
                self.harness.connect()
        connection.close.assert_called_once()
        self.assertEqual(connection.execute.call_count, 1)

    def test_owned_connection_starts_read_only_and_enables_fixtures_after_identity(self):
        self.pidfile()
        connection = Mock()
        connection.execute.return_value.fetchone.return_value = (str(self.harness.data),)
        with patch.object(integration.psycopg, "connect", return_value=connection) as connect:
            self.assertIs(self.harness.connect(), connection)
        kwargs = connect.call_args.kwargs
        self.assertEqual(kwargs["hostaddr"], "127.0.0.1")
        self.assertIn("default_transaction_read_only=on", kwargs["options"])
        self.assertEqual(connection.execute.call_args.args[0], "SET default_transaction_read_only = off")

    def test_connection_failure_is_sanitized(self):
        self.pidfile()
        with patch.object(integration.psycopg, "connect", side_effect=RuntimeError("SENTINEL")):
            with self.assertRaisesRegex(RuntimeError, "identity could not be verified") as error:
                self.harness.connect()
        self.assertNotIn("SENTINEL", str(error.exception))

    def test_stop_fast_then_immediate_and_idempotence(self):
        self.pidfile()
        calls = []
        def command(args):
            calls.append(args)
            if "fast" in args:
                raise RuntimeError("simulated")
            (self.harness.data / "postmaster.pid").unlink()
        with patch.object(self.harness, "command", side_effect=command):
            self.harness.stop()
            self.harness.stop()
        self.assertEqual(len(calls), 2)
        self.assertIn("immediate", calls[1])

    def test_failed_shutdown_is_reported_and_password_file_removed(self):
        self.pidfile()
        self.harness.password_file.write_text("synthetic")
        with patch.object(self.harness, "command", side_effect=RuntimeError("simulated")):
            with self.assertRaisesRegex(RuntimeError, "NOT confirmed"):
                self.harness.stop()
        self.assertFalse(self.harness.password_file.exists())

    def setup_patches(self, command):
        fake_socket = Mock()
        fake_socket.__enter__ = Mock(return_value=fake_socket)
        fake_socket.__exit__ = Mock(return_value=False)
        fake_socket.getsockname.return_value = ("127.0.0.1", 45678)
        return [patch.object(integration, "os", SimpleNamespace(environ={"PATH": "synthetic"})),
                patch.object(integration.shutil, "which", side_effect=lambda name: str(self.root / name)),
                patch.object(integration.tempfile, "mkdtemp", return_value=str(self.root)),
                patch.object(integration.socket, "socket", return_value=fake_socket),
                patch.object(self.harness, "command", side_effect=command)]

    def run_setup_failure(self, stage):
        from contextlib import ExitStack
        def command(args):
            if args[0].endswith("initdb"):
                if stage == "initdb":
                    raise RuntimeError("simulated initdb failure")
                (self.harness.data / "postgresql.conf").write_text("")
            else:
                self.pidfile()
                raise RuntimeError("simulated startup failure")
        with ExitStack() as stack:
            for context in self.setup_patches(command):
                stack.enter_context(context)
            with self.assertRaises(RuntimeError):
                self.harness.setUpClass()
        self.assertEqual(len(self.harness._class_cleanups), 1)
        with patch.object(self.harness, "stop_server") as stop:
            self.harness.doClassCleanups()
            stop.assert_called_once()
        self.assertFalse(self.harness.password_file.exists())

    def test_initdb_failure_has_registered_cleanup(self):
        self.run_setup_failure("initdb")

    def test_startup_failure_has_registered_cleanup(self):
        self.run_setup_failure("start")

    def test_subprocess_timeout_is_sanitized(self):
        with patch.object(integration.subprocess, "run", side_effect=integration.subprocess.TimeoutExpired("synthetic", 45)):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                self.harness.command(["synthetic"])

    def test_inherited_pg_variables_stop_before_tempfiles_or_processes(self):
        with patch.object(integration.shutil, "which", side_effect=lambda name: str(self.root / name)), \
             patch.object(integration, "os", SimpleNamespace(environ={"PGSERVICE": "not-read"})), \
             patch.object(integration.tempfile, "mkdtemp") as directory:
            with self.assertRaisesRegex(RuntimeError, "Inherited PG variables"):
                self.harness.setUpClass()
        directory.assert_not_called()

    def diagnostics(self):
        path = self.root / "command-diagnostics.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def captured_command(self, completed, *, timeout=False):
        def execute(*args, **kwargs):
            kwargs["stdout"].write(completed.stdout or b"")
            kwargs["stderr"].write(completed.stderr or b"")
            if timeout:
                raise completed
            return SimpleNamespace(returncode=completed.returncode)
        return execute

    def test_capture_failed_start_and_server_log_without_console_secrets(self):
        (self.root / "server.log").write_text("FATAL: could not bind socket\npassword=do-not-share\n")
        completed = SimpleNamespace(returncode=1, stdout=b"waiting for server\n", stderr=b"Permission denied\npostgresql://u:pass@host/db\n")
        output = io.StringIO()
        with patch.object(integration.subprocess, "run", side_effect=self.captured_command(completed)) as run, \
             redirect_stdout(output), redirect_stderr(output):
            with self.assertRaisesRegex(RuntimeError, "sanitized details"):
                self.harness.command(["pg_ctl", "start"])
        record, = self.diagnostics()
        self.assertEqual(record["returncode"], 1)
        self.assertEqual(record["stage"], "start")
        self.assertIn("Permission denied", record["stderr"])
        self.assertIn("could not bind socket", record["server_log_excerpt"])
        self.assertNotIn("postgresql://", json.dumps(record))
        self.assertNotIn("do-not-share", json.dumps(record))
        self.assertEqual(output.getvalue(), "")
        self.assertTrue(run.call_args.kwargs["stderr"].closed)
        self.assertIn("password=do-not-share", (self.root / "server.log").read_text())

    def test_known_encoded_secrets_conninfo_tokens_and_control_characters(self):
        secret = "test secret/@"
        raw = "\n".join((secret, integration.quote(secret, safe=""), integration.quote_plus(secret),
                          "host=x dbname=x user=x", "ACCESS_TOKEN=value", "Bearer value", "PGPASSWORD=value", "safe\x1b[31m"))
        result = integration.sanitize_output(raw, (secret,))
        for value in (secret, "value", "host=", "\x1b"):
            self.assertNotIn(value, result)
        self.assertIn("safe", result)
        self.assertEqual(integration.sanitize_output("-----BEGIN PRIVATE KEY-----\nsensitive\n-----END PRIVATE KEY-----"),
                         "[REDACTED_PRIVATE_KEY_OUTPUT]")

    def test_timeout_preserves_partial_streams_and_no_exception_text(self):
        error = integration.subprocess.TimeoutExpired("PASSWORD_SHOULD_NOT_APPEAR", 45,
                    output=b"partial stdout", stderr=b"partial stderr\npassword=hidden")
        with patch.object(integration.subprocess, "run", side_effect=self.captured_command(error, timeout=True)):
            with self.assertRaises(RuntimeError):
                self.harness.command(["pg_ctl", "start"])
        record, = self.diagnostics()
        self.assertEqual(record["event"], "timeout")
        self.assertIsNone(record["returncode"])
        self.assertIn("partial stdout", record["stdout"])
        self.assertNotIn("hidden", json.dumps(record))
        self.assertNotIn("PASSWORD_SHOULD_NOT_APPEAR", json.dumps(record))

    def test_os_error_retains_errno_without_raw_exception(self):
        with patch.object(integration.subprocess, "run", side_effect=PermissionError(13, "SECRET_ERROR")):
            with self.assertRaises(RuntimeError):
                self.harness.command(["pg_ctl", "start"])
        record, = self.diagnostics()
        self.assertEqual(record["errno"], 13)
        self.assertEqual(record["event"], "os_error")
        self.assertNotIn("SECRET_ERROR", json.dumps(record))

    def test_success_is_captured_and_failure_evidence_is_appended_not_overwritten(self):
        with patch.object(integration.subprocess, "run", side_effect=self.captured_command(SimpleNamespace(returncode=1, stdout=b"failed", stderr=b"failure"))):
            with self.assertRaises(RuntimeError):
                self.harness.command(["pg_ctl", "start"])
        with patch.object(integration.subprocess, "run", side_effect=self.captured_command(SimpleNamespace(returncode=0, stdout=b"stopped", stderr=b""))):
            self.harness.command(["pg_ctl", "stop"])
        records = self.diagnostics()
        self.assertEqual([record["stage"] for record in records], ["start", "stop"])
        self.assertEqual(records[0]["returncode"], 1)

    def test_missing_log_is_explicit_and_output_is_bounded_after_redaction(self):
        self.harness.save_diagnostic({"stage": "start", "stdout": b"x" * 70000, "stderr": b""})
        record, = self.diagnostics()
        self.assertFalse(record["server_log_exists"])
        self.assertTrue(record["stdout"].endswith("[TRUNCATED]"))

    def test_path_escape_is_refused_without_subprocess(self):
        with self.assertRaises(RuntimeError):
            self.harness.diagnostic_path("../outside.log")
        with patch.object(self.harness, "diagnostic_path", side_effect=RuntimeError("unsafe path")), \
             patch.object(integration.subprocess, "run") as run:
            with self.assertRaises(RuntimeError):
                self.harness.command(["pg_ctl", "start"])
        run.assert_not_called()

    def test_invalid_utf8_and_log_truncation_do_not_leak_partial_sensitive_line(self):
        (self.root / "server.log").write_bytes(b"safe line\npassword=" + b"a" * 70000)
        self.harness.save_diagnostic({"stage": "start", "stdout": b"\xff", "stderr": b""})
        record, = self.diagnostics()
        self.assertTrue(record["server_log_truncated"])
        self.assertEqual(record["server_log_excerpt"], "safe line")

    def test_symlink_diagnostic_is_refused_before_command(self):
        with patch.object(Path, "is_symlink", return_value=True), \
             patch.object(integration.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "symlink"):
                self.harness.command(["pg_ctl", "start"])
        run.assert_not_called()

    def test_persistence_failure_is_explicit_and_preserves_evidence(self):
        log = self.root / "server.log"
        log.write_text("original evidence")
        with patch.object(integration.os, "open", side_effect=PermissionError("SENSITIVE_ERROR")):
            with self.assertRaisesRegex(RuntimeError, "persistence failed") as raised:
                self.harness.save_diagnostic({"stage": "start", "stdout": "safe"})
        self.assertNotIn("SENSITIVE_ERROR", str(raised.exception))
        self.assertEqual(log.read_text(), "original evidence")

    def test_obfuscated_and_multiline_credentials_are_redacted(self):
        for value in ("postgresql%3A%2F%2Fu%3Ap%40h%2Fdb", "pa\x00ssword=hidden", "password:\nhidden", "token=\nhidden"):
            result = integration.sanitize_output(value)
            self.assertIn("REDACTED", result)
            self.assertNotIn("hidden", result)

    def test_changed_root_identity_refuses_commands(self):
        self.harness.root_identity = (0, -1)
        with self.assertRaisesRegex(RuntimeError, "identity changed"):
            self.harness.command(["pg_ctl", "start"])

    def test_cleanup_rechecks_identity_before_immediate(self):
        self.pidfile()
        def failed_fast(args):
            (self.harness.data / "postmaster.pid").write_text("untrusted PID")
            raise RuntimeError("failed fast")
        with patch.object(self.harness, "command", side_effect=failed_fast) as command:
            with self.assertRaisesRegex(RuntimeError, "ownership not confirmed"):
                self.harness.stop()
        self.assertEqual(command.call_count, 1)

    def test_large_capture_keeps_raw_evidence_and_reads_bounded_excerpt(self):
        completed = SimpleNamespace(returncode=1, stdout=b"safe\n" + b"x" * 200000, stderr=b"failure")
        with patch.object(integration.subprocess, "run", side_effect=self.captured_command(completed)):
            with self.assertRaises(RuntimeError):
                self.harness.command(["pg_ctl", "start"])
        record, = self.diagnostics()
        self.assertTrue(record["stdout_truncated"])
        self.assertEqual(record["stdout"], "safe")
        self.assertGreater((self.root / record["raw_capture_files"][0]).stat().st_size, integration.OUTPUT_LIMIT)

    def test_changed_pid_or_start_timestamp_refuses_cleanup_before_command(self):
        for index, replacement in ((0, "2345"), (2, "654321")):
            self.harness.observed_server_identity = None
            self.pidfile()
            self.harness.verify_owned_server()
            path = self.harness.data / "postmaster.pid"
            lines = path.read_text().splitlines()
            lines[index] = replacement
            path.write_text("\n".join(lines))
            with patch.object(self.harness, "command") as command:
                with self.assertRaisesRegex(RuntimeError, "ownership not confirmed"):
                    self.harness.stop()
            command.assert_not_called()

    def test_changed_descriptor_identity_refuses_read(self):
        (self.root / "server.log").write_text("must not be read")
        real_fstat = integration.os.fstat
        def changed(fd):
            result = real_fstat(fd)
            return SimpleNamespace(st_dev=result.st_dev, st_ino=result.st_ino + 1, st_nlink=1)
        with patch.object(integration.os, "fstat", side_effect=changed):
            with self.assertRaisesRegex(RuntimeError, "identity changed before read"):
                self.harness.read_excerpt("server.log")

    def test_multiple_links_refuse_read_and_pid_use(self):
        self.pidfile()
        # Simulate OS metadata; no links or processes are created.
        original_stat = Path.stat
        def linked(path, *args, **kwargs):
            result = original_stat(path, *args, **kwargs)
            if path.name == "postmaster.pid":
                return SimpleNamespace(st_nlink=2, st_mode=result.st_mode)
            return result
        with patch.object(Path, "stat", linked), patch.object(self.harness, "command") as command:
            with self.assertRaises(RuntimeError):
                self.harness.verify_owned_server()
        command.assert_not_called()
