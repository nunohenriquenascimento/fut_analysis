"""Read-only fingerprints for the 0006 -> 0007 maintenance procedure.

Never applies migrations, writes to PostgreSQL, or prints rows/credentials.
"""
import argparse
import hashlib
import json
from pathlib import Path

from sqlalchemy import text

from app.database import get_engine

TABLES = ("users", "seasons", "teams", "players", "matches", "match_squads",
          "match_events", "auth_sessions", "login_throttles")


def snapshot(engine):
    result = {"version": None, "tables": {}}
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            result["version"] = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            for table in TABLES:
                digest, count = hashlib.sha256(), 0
                # Static allowlist; canonical ordering makes fingerprints independent of scan order.
                rows = connection.execution_options(stream_results=True).execute(text(
                    f'SELECT row_to_json(t)::text FROM "{table}" t ORDER BY row_to_json(t)::text'
                ))
                for row in rows:
                    encoded = row[0].encode("utf-8")
                    digest.update(len(encoded).to_bytes(8, "big"))
                    digest.update(encoded)
                    count += 1
                rows.close()
                result["tables"][table] = {"rows": count, "sha256": digest.hexdigest()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture", help="Capture fingerprints at 0006, without overwriting a file")
    capture.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify", help="Verify 0007 preserves every row/column present at 0006")
    verify.add_argument("--before", type=Path, required=True)
    args = parser.parse_args()
    current = snapshot(get_engine())
    if args.command == "capture":
        if current["version"] != "0006":
            parser.error("Capture requires revision 0006.")
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(current, output, indent=2)
        print("Read-only snapshot captured. No database rows were changed.")
    else:
        before = json.loads(args.before.read_text(encoding="utf-8"))
        if before.get("version") != "0006" or current["version"] != "0007":
            parser.error("Verification requires a 0006 snapshot and a database at 0007.")
        if current["tables"] != before.get("tables"):
            parser.error("Existing data differs. Keep maintenance active and investigate; do not auto-restore.")
        print("Verified: revision 0007 and all nine existing tables unchanged.")


if __name__ == "__main__":
    main()
