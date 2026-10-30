"""SQLite storage. Only YOUR progress lives here; the checklists themselves come from the repo."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
    item_key   TEXT PRIMARY KEY,
    project    TEXT NOT NULL,
    checked    INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hours (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    day        TEXT NOT NULL,
    project    TEXT NOT NULL,
    hours      REAL NOT NULL,
    note       TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ratings (
    project    TEXT PRIMARY KEY,
    enjoyed    INTEGER,
    natural    INTEGER,
    want_more  INTEGER,
    notes      TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    text       TEXT NOT NULL,
    done       INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    done_at    TEXT
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as c:
            c.executescript(SCHEMA)
            c.execute("PRAGMA journal_mode=WAL")

    @contextmanager
    def conn(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        finally:
            con.close()

    # --- checks -------------------------------------------------------------------------------
    def checked_keys(self) -> set[str]:
        with self.conn() as c:
            return {r["item_key"] for r in c.execute("SELECT item_key FROM checks WHERE checked = 1")}

    def set_check(self, key: str, project: str, checked: bool) -> None:
        with self.conn() as c:
            c.execute(
                "INSERT INTO checks (item_key, project, checked, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(item_key) DO UPDATE SET checked = excluded.checked, updated_at = excluded.updated_at",
                (key, project, int(checked), now()),
            )

    # --- hours --------------------------------------------------------------------------------
    def add_hours(self, day: str, project: str, hours: float, note: str) -> int:
        with self.conn() as c:
            cur = c.execute("INSERT INTO hours (day, project, hours, note, created_at) VALUES (?, ?, ?, ?, ?)",
                            (day, project, hours, note, now()))
            return int(cur.lastrowid)

    def delete_hours(self, entry_id: int) -> bool:
        with self.conn() as c:
            return c.execute("DELETE FROM hours WHERE id = ?", (entry_id,)).rowcount > 0

    def hours_entries(self, project: str | None = None) -> list[sqlite3.Row]:
        with self.conn() as c:
            if project:
                return list(c.execute("SELECT * FROM hours WHERE project = ? ORDER BY day DESC, id DESC", (project,)))
            return list(c.execute("SELECT * FROM hours ORDER BY day DESC, id DESC"))

    def hours_by_project(self) -> dict[str, float]:
        with self.conn() as c:
            return {r["project"]: r["total"] for r in
                    c.execute("SELECT project, SUM(hours) AS total FROM hours GROUP BY project")}

    # --- ratings ------------------------------------------------------------------------------
    def ratings(self) -> dict[str, sqlite3.Row]:
        with self.conn() as c:
            return {r["project"]: r for r in c.execute("SELECT * FROM ratings")}

    def set_rating(self, project: str, enjoyed: int | None, natural: int | None,
                   want_more: bool | None, notes: str) -> None:
        with self.conn() as c:
            c.execute(
                "INSERT INTO ratings (project, enjoyed, natural, want_more, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(project) DO UPDATE SET enjoyed = excluded.enjoyed, natural = excluded.natural, "
                "want_more = excluded.want_more, notes = excluded.notes, updated_at = excluded.updated_at",
                (project, enjoyed, natural, None if want_more is None else int(want_more), notes, now()),
            )

    # --- custom tasks -------------------------------------------------------------------------
    def tasks(self) -> list[sqlite3.Row]:
        with self.conn() as c:
            return list(c.execute("SELECT * FROM tasks ORDER BY done, id DESC"))

    def add_task(self, text: str) -> int:
        with self.conn() as c:
            return int(c.execute("INSERT INTO tasks (text, created_at) VALUES (?, ?)", (text, now())).lastrowid)

    def set_task(self, task_id: int, done: bool) -> bool:
        with self.conn() as c:
            return c.execute("UPDATE tasks SET done = ?, done_at = ? WHERE id = ?",
                             (int(done), now() if done else None, task_id)).rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with self.conn() as c:
            return c.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount > 0

    # --- backup -------------------------------------------------------------------------------
    def export(self) -> dict:
        with self.conn() as c:
            return {t: [dict(r) for r in c.execute(f"SELECT * FROM {t}")]  # table names are constants
                    for t in ("checks", "hours", "ratings", "tasks")}
