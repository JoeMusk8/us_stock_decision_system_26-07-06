from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from app.core.config import settings


def _db_path() -> Path:
    path = Path(settings.database_url)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS x_accounts (
                handle TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                since_id TEXT
            );

            CREATE TABLE IF NOT EXISTS x_posts (
                id TEXT PRIMARY KEY,
                handle TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                raw_json TEXT NOT NULL DEFAULT '{}',
                inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analyses (
                key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

