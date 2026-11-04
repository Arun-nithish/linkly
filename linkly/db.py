import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    clicked_at TEXT NOT NULL,
    user_agent TEXT
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_link(db_path: str, code: str, url: str) -> bool:
    """Insert a link. Returns False if the code is already taken."""
    try:
        with connect(db_path) as conn:
            conn.execute(
                "INSERT INTO links (code, url, created_at) VALUES (?, ?, ?)",
                (code, url, now()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_link(db_path: str, code: str):
    with connect(db_path) as conn:
        return conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()


def record_click(db_path: str, link_id: int, user_agent: str | None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO clicks (link_id, clicked_at, user_agent) VALUES (?, ?, ?)",
            (link_id, now(), user_agent),
        )


def get_stats(db_path: str, code: str):
    with connect(db_path) as conn:
        link = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
        if link is None:
            return None
        total = conn.execute(
            "SELECT COUNT(*) FROM clicks WHERE link_id = ?", (link["id"],)
        ).fetchone()[0]
        per_day = conn.execute(
            "SELECT substr(clicked_at, 1, 10) AS day, COUNT(*) AS clicks "
            "FROM clicks WHERE link_id = ? GROUP BY day ORDER BY day",
            (link["id"],),
        ).fetchall()
        return {
            "code": link["code"],
            "url": link["url"],
            "created_at": link["created_at"],
            "total_clicks": total,
            "clicks_per_day": [dict(r) for r in per_day],
        }
