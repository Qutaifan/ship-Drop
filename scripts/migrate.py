#!/usr/bin/env python3
"""Database Migration Runner for Project: Dropship | Framework: Hermes."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "scripts" / "migrations"
DB_PATH = ROOT / "data" / "dropship.db"


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def apply_migrations(db_path: Path) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    applied = {row[0] for row in cursor.execute("SELECT version FROM schema_migrations").fetchall()}

    migration_files = sorted(MIGRATIONS_DIR.glob("[0-9]*.sql"))
    for f in migration_files:
        if "rollback" in f.name:
            continue
        version = f.stem
        if version in applied:
            print(f"  ✓ {version} already applied.")
            continue

        print(f"  🚀 Applying migration: {version}...")
        sql = f.read_text(encoding="utf-8")
        cursor.executescript(sql)
        cursor.execute(
            "INSERT INTO schema_migrations (version, applied_at) VALUES (?, datetime('now'))",
            (version,),
        )
        conn.commit()
        print(f"  ✅ Applied: {version}")

    conn.close()
    print("✨ All migrations applied successfully.")


def rollback_migration(db_path: Path, version: str) -> None:
    rollback_file = MIGRATIONS_DIR / f"{version}_rollback.sql"
    if not rollback_file.exists():
        # Check alternate naming
        parts = version.split("_", 1)
        if len(parts) == 2:
            alt = MIGRATIONS_DIR / f"{parts[0]}_rollback_{parts[1]}.sql"
            if alt.exists():
                rollback_file = alt

    if not rollback_file.exists():
        print(f"❌ Rollback file not found for version: {version}")
        sys.exit(1)

    conn = get_connection(db_path)
    cursor = conn.cursor()
    print(f"  ⚠️ Executing rollback for: {version}...")
    sql = rollback_file.read_text(encoding="utf-8")
    cursor.executescript(sql)
    cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
    conn.commit()
    conn.close()
    print(f"  ✅ Rolled back: {version}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dropship DB Migration Tool")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("up", help="Apply all pending migrations")
    roll_parser = subparsers.add_parser("rollback", aliases=["down"], help="Rollback a migration")
    roll_parser.add_argument("version", help="Migration version (e.g. 002_supplier_verifications)")

    subparsers.add_parser("status", help="List applied migrations")

    args = parser.parse_args()
    db_path = DB_PATH

    if args.command == "up" or not args.command:
        apply_migrations(db_path)
    elif args.command in ["rollback", "down"]:
        rollback_migration(db_path, args.version)
    elif args.command == "status":
        conn = get_connection(db_path)
        rows = conn.execute("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at").fetchall()
        print(f"\nApplied Migrations ({len(rows)}):")
        for v, t in rows:
            print(f"  - {v} (applied at {t})")
        conn.close()


if __name__ == "__main__":
    main()
