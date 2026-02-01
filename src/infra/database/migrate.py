from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from src.infra.database.connection import db_session


@dataclass(frozen=True)
class Migration:
    filename: str
    path: Path


def default_migrations_dir() -> Path:
    """
    Compute migrations directory reliably regardless of current working directory.

    This file is: src/infra/database/migrate.py
    parents[0] -> database/
    parents[1] -> infra/
    parents[2] -> src/
    So migrations directory is: src/migrations/
    """
    return Path(__file__).resolve().parents[2] / "migrations"


def list_migrations(migrations_dir: Path) -> List[Migration]:
    """
    List .sql files in deterministic order by filename.
    Expect names like 001_init_db.sql, 002_create_wallets.sql, etc.
    """
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Missing migrations directory: {migrations_dir}")

    files = sorted(migrations_dir.glob("*.sql"), key=lambda p: p.name)
    return [Migration(filename=f.name, path=f) for f in files]


def ensure_migrations_table(conn) -> None:
    """
    Create schema_migrations table if it doesn't exist.
    This tracks which migration filenames were applied.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename   TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )


def get_applied(conn) -> Set[str]:
    rows = conn.execute("SELECT filename FROM schema_migrations;").fetchall()
    return {row["filename"] for row in rows}


def apply_one(conn, migration: Migration) -> None:
    """
    Apply a single migration and record it.
    """
    sql = migration.path.read_text(encoding="utf-8")

    conn.executescript(sql)

    conn.execute(
        "INSERT INTO schema_migrations(filename) VALUES (?);",
        (migration.filename,),
    )


def run_migrations(*, db_path: Path, migrations_dir: Path | None = None) -> List[str]:
    """
    Apply all pending migrations in order.

    Args:
        db_path: Path to SQLite database file.
        migrations_dir: Directory containing migration .sql files.
                       If None, uses default_migrations_dir().

    Returns:
        List of filenames applied during this run.
    """
    mig_dir = migrations_dir or default_migrations_dir()
    migrations = list_migrations(mig_dir)
    applied_now: List[str] = []

    with db_session(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE;")

        ensure_migrations_table(conn)
        already = get_applied(conn)

        for m in migrations:
            if m.filename in already:
                continue
            apply_one(conn, m)
            applied_now.append(m.filename)

    return applied_now
