"""
SQLite schema and helpers for kaggle-claude-plugin.

Status flow: pending_notify → shown
Only non-Other competitions are stored (Other is filtered by Claude).
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("KAGGLE_PLUGIN_DB", Path(__file__).parent / "kaggle.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS competitions (
    title           TEXT PRIMARY KEY,
    link            TEXT NOT NULL,
    date_start      TEXT,
    deadline        TEXT,
    description     TEXT,
    tags            TEXT,
    competition_type TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending_notify',
    saved_at        TEXT NOT NULL DEFAULT (datetime('now')),
    notified_at     TEXT
);

CREATE TABLE IF NOT EXISTS import_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_at    TEXT NOT NULL DEFAULT (datetime('now')),
    fetched_count  INTEGER NOT NULL DEFAULT 0,
    saved_count    INTEGER NOT NULL DEFAULT 0
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(_SCHEMA)


def upsert_competition(
    title: str,
    link: str,
    date_start: str,
    deadline: str,
    description: str,
    tags: str,
    competition_type: str,
) -> bool:
    """Insert or update competition. Returns True if newly inserted."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT title, status FROM competitions WHERE title = ?", (title,)
        ).fetchone()

        if existing:
            # Update metadata but don't change status
            conn.execute(
                """UPDATE competitions
                   SET link=?, date_start=?, deadline=?, description=?, tags=?, competition_type=?
                   WHERE title=?""",
                (link, date_start, deadline, description, tags, competition_type, title),
            )
            return False
        else:
            conn.execute(
                """INSERT INTO competitions
                   (title, link, date_start, deadline, description, tags, competition_type, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_notify')""",
                (title, link, date_start, deadline, description, tags, competition_type),
            )
            return True


def get_pending(limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT title, link, date_start, deadline, description, tags, competition_type
               FROM competitions WHERE status = 'pending_notify'
               ORDER BY deadline ASC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def mark_shown(title: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE competitions SET status='shown', notified_at=datetime('now') WHERE title=?",
            (title,),
        )


def log_import(fetched_count: int, saved_count: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO import_log (fetched_count, saved_count) VALUES (?, ?)",
            (fetched_count, saved_count),
        )


def get_last_import() -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT imported_at, fetched_count, saved_count FROM import_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_stats() -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM competitions").fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM competitions WHERE status='pending_notify'"
        ).fetchone()[0]
        shown = conn.execute(
            "SELECT COUNT(*) FROM competitions WHERE status='shown'"
        ).fetchone()[0]
        by_type = conn.execute(
            "SELECT competition_type, COUNT(*) as cnt FROM competitions GROUP BY competition_type"
        ).fetchall()
        last_import = get_last_import()

        return {
            "total": total,
            "pending_notify": pending,
            "shown": shown,
            "by_type": {row["competition_type"]: row["cnt"] for row in by_type},
            "last_import": last_import,
        }


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
