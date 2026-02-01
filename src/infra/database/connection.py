from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def ensure_parent_dir(db_path: Path) -> None:
    """
    Ensure the directory that will contain the SQLite DB file exists.
    Example:
      db_path = data/bitcoin_wallet.db
      parent  = data/
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)


def create_connection(db_path: Path) -> sqlite3.Connection:
    """
    Create and configure a new SQLite connection.

    - Creates the parent directory if needed.
    - Sets row_factory so rows behave like dicts (row["col"]).
    - Enables foreign key enforcement (off by default in SQLite).
    """
    ensure_parent_dir(db_path)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


@contextmanager
def db_session(db_path: Path) -> Iterator[sqlite3.Connection]:
    """
    Transaction/session scope.

    Usage:
        with db_session(db_path) as conn:
            conn.execute(...)
            ...

    Behavior:
      - commits if block succeeds
      - rolls back if exception occurs
      - always closes the connection
    """
    conn = create_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
