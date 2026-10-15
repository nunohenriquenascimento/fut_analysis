"""Rehearse 0007 with synthetic data on a new, isolated PostgreSQL cluster.

The configured application database is inspected in READ ONLY mode. All DDL,
seed data, pg_dump and pg_restore target the temporary cluster, never that DB.
The isolated cluster is stopped at the end; its files are retained for review.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

from sqlalchemy import create_engine, inspect, text

from app.database import get_engine
from app.migration_audit import TABLES, snapshot

BACKEND = Path(__file__).resolve().parents[1]


def schema_signature(engine):
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            inspector = inspect(connection)
            tables = {}
            for table in (*TABLES, "alembic_version"):
                tables[table] = dict(
                    columns=[(c["name"], str(c["type"]), c["nullable"], c["default"]) for c in inspector.get_columns(table)],
                    pk=inspector.get_pk_constraint(table),
                    foreign_keys=inspector.get_foreign_keys(table),
                    unique=inspector.get_unique_constraints(table),
                    checks=inspector.get_check_constraints(table),
                    indexes=inspector.get_indexes(table),
                )
            return dict(tables=tables, names=sorted(inspector.get_table_names()),
                        enums=[(e["name"], e["labels"]) for e in inspector.get_enums()])


def sequence_state(engine):
    with engine.connect() as connection:
        connection.execute(text("SET TRANSACTION READ ONLY"))
        return {table: list(connection.execute(text(f'SELECT last_value,is_called FROM "{table}_id_seq"')).one())
                for table in TABLES[:7]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True, help="New directory; existing directories are refused")
    args = parser.parse_args()
    root = args.directory.resolve()
    root.mkdir(parents=True, exist_ok=False)
    binaries = {name: shutil.which(name) for name in ("initdb", "pg_ctl", "pg_dump", "pg_restore")}
    if not all(binaries.values()):
        parser.error("PostgreSQL initdb, pg_ctl, pg_dump and pg_restore must be on PATH.")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    data = root / "cluster"
    # All data is synthetic. Bind only to loopback on a fresh random port.
    command_number = 0
    def run(command, env=None):
        nonlocal command_number
        command_number += 1
        log = root / f"command-{command_number}.log"
        # A PostgreSQL child on Windows can inherit pipes and keep communicate()
        # waiting after pg_ctl exits. File-backed logs avoid that lifecycle trap.
        with log.open("w", encoding="utf-8") as output:
            result = subprocess.run(command, cwd=BACKEND, env=env, stdout=output, stderr=subprocess.STDOUT, text=True)
        contents = log.read_text(encoding="utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(contents)
        return contents
    def migrate(url, *arguments):
        return run([sys.executable, "-m", "alembic", *arguments], {**os.environ, "DATABASE_URL": url})
    report = {"synthetic_only": True, "port": port}
    started = False
    engines = []
    try:
        run([binaries["initdb"], "-D", str(data), "--username=ccdr_rehearsal", "--auth=trust", "--encoding=UTF8", "--locale=C"])
        run([binaries["pg_ctl"], "-D", str(data), "-l", str(root / "postgres.log"), "-o", f"-p {port} -h 127.0.0.1", "-w", "start"])
        started = True
        admin = create_engine(f"postgresql+psycopg://ccdr_rehearsal@127.0.0.1:{port}/postgres")
        engines.append(admin)
        with admin.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            for name in ("rehearsal_source", "rehearsal_restored"):
                connection.execute(text(f'CREATE DATABASE "{name}"'))
        source_url = f"postgresql+psycopg://ccdr_rehearsal@127.0.0.1:{port}/rehearsal_source"
        restored_url = f"postgresql+psycopg://ccdr_rehearsal@127.0.0.1:{port}/rehearsal_restored"
        source, restored = create_engine(source_url), create_engine(restored_url)
        engines.extend([source, restored])
        migrate(source_url, "upgrade", "0006")
        with source.begin() as connection:
            for statement in (
                "INSERT INTO seasons(id,name,starts_on,ends_on) VALUES(1,'ENSAIO 2026/27','2026-07-01','2027-06-30')",
                "INSERT INTO teams(id,name) VALUES(1,'ENSAIO CCDR'),(2,'ENSAIO Adversário')",
                "INSERT INTO users(id,name,email,role,is_active) VALUES(1,'ENSAIO Admin','ensaio@example.invalid','ADMIN',true)",
                "INSERT INTO players(id,season_id,team_id,name,position,shirt_number,is_active) VALUES(1,1,1,'ENSAIO Jogador','MC',8,true)",
                "INSERT INTO matches(id,season_id,team_id,opponent_id,matchday,kickoff_at,is_home,status,elapsed_seconds) VALUES(1,1,1,2,1,'2026-10-15T14:00:00Z',true,'FINISHED',5400)",
                "INSERT INTO match_squads(id,match_id,player_id,is_starter) VALUES(1,1,1,true)",
                "INSERT INTO match_events(id,match_id,event_type,team,player_id,recorded_by_id,period,elapsed_seconds) VALUES(1,1,'GOAL','US',1,1,1,60)",
                "INSERT INTO auth_sessions(token_hash,user_id,csrf_token,expires_at) VALUES('synthetic-session',1,'synthetic-csrf','2027-01-01T00:00:00Z')",
                "INSERT INTO login_throttles(key,attempts,resets_at) VALUES('synthetic-key',1,'2027-01-01T00:00:00Z')",
            ):
                connection.execute(text(statement))
            for table in TABLES[:7]:
                connection.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}','id'), (SELECT max(id) FROM {table}), true)"))
        before = snapshot(source)
        before_sequences = sequence_state(source)
        (root / "before.json").write_text(json.dumps(before, indent=2), encoding="utf-8")
        expected = schema_signature(source)
        actual = schema_signature(get_engine())
        with get_engine().connect() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            report["application_revision"] = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        report["application_schema_matches_0006"] = actual == expected
        if report["application_revision"] != "0006" or not report["application_schema_matches_0006"]:
            raise RuntimeError("Application schema/revision does not match the isolated 0006 baseline.")
        archive = root / "synthetic-0006.dump"
        pg_env = {**os.environ, "PGHOST": "127.0.0.1", "PGPORT": str(port), "PGUSER": "ccdr_rehearsal", "PGDATABASE": "rehearsal_source"}
        # Remove inherited connection settings that could redirect PostgreSQL tools.
        for key in ("PGSERVICE", "PGSERVICEFILE", "PGOPTIONS", "PGPASSWORD"):
            pg_env.pop(key, None)
        pg_env["PGHOSTADDR"] = "127.0.0.1"
        pg_env["PGSSLMODE"] = "disable"
        run([binaries["pg_dump"], "--format=custom", f"--file={archive}"], pg_env)
        toc = run([binaries["pg_restore"], "--list", str(archive)], pg_env)
        (root / "archive-list.txt").write_text(toc, encoding="utf-8")
        report["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        run([binaries["pg_restore"], "--exit-on-error", "--no-owner", "--no-privileges", "--dbname=rehearsal_restored", str(archive)], pg_env)
        report["restored_data_identical"] = snapshot(restored) == before
        report["restored_schema_identical"] = schema_signature(restored) == expected
        report["sequences_restored"] = sequence_state(restored) == before_sequences
        if not all(report[key] for key in ("restored_data_identical", "restored_schema_identical", "sequences_restored")):
            raise RuntimeError("Restored synthetic data differs from the source.")
        migrate(restored_url, "upgrade", "0007")
        after = snapshot(restored)
        report["after_revision"] = after["version"]
        report["existing_data_preserved"] = after["tables"] == before["tables"]
        if after["version"] != "0007" or not report["existing_data_preserved"]:
            raise RuntimeError("Migration did not preserve the synthetic baseline.")
        report["alembic_check"] = migrate(restored_url, "check").strip()
        from fastapi.testclient import TestClient
        from sqlalchemy.orm import Session
        from app.auth import current_user
        from app.database import get_db
        from app.main import app
        from app.models import User
        with Session(restored) as db:
            actor = db.get(User, 1)
            app.dependency_overrides[get_db] = lambda: db
            app.dependency_overrides[current_user] = lambda: actor
            try:
                with TestClient(app) as client:
                    report["read_smoke_statuses"] = {path: client.get(path).status_code for path in (
                        "/competitions", "/players", "/matches/1", "/matches/1/live", "/matches/1/stats"
                    )}
                if any(status != 200 for status in report["read_smoke_statuses"].values()):
                    raise RuntimeError("Read smoke check failed on the isolated database.")
            finally:
                app.dependency_overrides.clear()
        (root / "after.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
        report["success"] = True
    finally:
        for engine in engines:
            engine.dispose()
        if started:
            run([binaries["pg_ctl"], "-D", str(data), "-w", "stop"])
            report["isolated_server_stopped"] = True
        (root / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
