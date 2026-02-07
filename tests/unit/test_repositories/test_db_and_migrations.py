from __future__ import annotations

from pathlib import Path
import sqlite3

from src.infra.database.connection import create_connection
from src.infra.database.migrate import run_migrations, default_migrations_dir


def test_sqlite_connection_works(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"

    conn = create_connection(db_file)
    try:
        val = conn.execute("SELECT 1;").fetchone()[0]
        assert val == 1
    finally:
        conn.close()

    assert db_file.exists()


def test_migrations_create_tables(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"

    applied = run_migrations(db_path=db_file, migrations_dir=default_migrations_dir())
    assert len(applied) >= 3

    conn = sqlite3.connect(db_file)
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            ).fetchall()
        }
    finally:
        conn.close()

    assert "schema_migrations" in tables
    assert "users" in tables
    assert "wallets" in tables


def test_migrations_are_idempotent(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"

    first = run_migrations(db_path=db_file, migrations_dir=default_migrations_dir())
    second = run_migrations(db_path=db_file, migrations_dir=default_migrations_dir())

    assert len(first) >= 3
    assert second == []
