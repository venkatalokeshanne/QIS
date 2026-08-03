"""
Level watch repository.

A "level watch" is a standing request to poll one symbol on a fixed
cadence (see app.services.poller) and send a Telegram message whenever
its Auto Support/Resistance levels (app.services.levels_service.
get_daily_levels's auto_support_resistance) change versus the last
notified set. Same dual SQLite/Postgres backend switch as
WatchRepository -- see that module's docstring.
"""

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

from app.config.settings import settings
from app.core.exceptions import DataValidationError, NotFoundError

_SCHEMA = """
CREATE TABLE IF NOT EXISTS level_watches (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    last_levels TEXT,
    last_checked_at TEXT,
    created_at TEXT NOT NULL
);
"""

_COLUMNS = "id, symbol, last_levels, last_checked_at, created_at"


@dataclass(frozen=True)
class LevelWatchRecord:
    id: str
    symbol: str
    last_levels: list[float] | None
    last_checked_at: str | None
    created_at: str


def _row_to_record(row) -> LevelWatchRecord:
    return LevelWatchRecord(
        id=row[0],
        symbol=row[1],
        last_levels=json.loads(row[2]) if row[2] else None,
        last_checked_at=row[3],
        created_at=row[4],
    )


class LevelWatchRepository:
    def __init__(self):
        self._use_postgres = bool(settings.database_url)
        if self._use_postgres:
            import psycopg2  # local import: only needed in this mode

            self._psycopg2 = psycopg2
        else:
            settings.ensure_dirs()
            self._db_path = settings.db_path
        self._init_db()

    @contextmanager
    def _connection(self):
        if self._use_postgres:
            conn = self._psycopg2.connect(settings.database_url)
        else:
            import sqlite3

            conn = sqlite3.connect(self._db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _ph(self) -> str:
        """Parameter placeholder -- psycopg2 uses %s, sqlite3 uses ?."""
        return "%s" if self._use_postgres else "?"

    def _init_db(self) -> None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(_SCHEMA)
            conn.commit()

    def create(self, symbol: str) -> LevelWatchRecord:
        """
        Raises DataValidationError if a level watch already exists for
        this symbol -- app-level uniqueness check (not DB-enforced); a
        race between two near-simultaneous creates is harmless for a
        single-user app, at worst producing one duplicate watch.
        """
        symbol = symbol.upper()
        if any(w.symbol == symbol for w in self.list_all()):
            raise DataValidationError(f"A level watch for '{symbol}' already exists.")

        record = LevelWatchRecord(
            id=str(uuid.uuid4()),
            symbol=symbol,
            last_levels=None,
            last_checked_at=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO level_watches ({_COLUMNS}) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})",
                (record.id, record.symbol, None, record.last_checked_at, record.created_at),
            )
            conn.commit()
        return record

    def get(self, watch_id: str) -> LevelWatchRecord:
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_COLUMNS} FROM level_watches WHERE id = {ph}", (watch_id,))
            row = cur.fetchone()
        if row is None:
            raise NotFoundError(f"Level watch '{watch_id}' not found.")
        return _row_to_record(row)

    def list_all(self) -> list[LevelWatchRecord]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_COLUMNS} FROM level_watches ORDER BY created_at DESC")
            rows = cur.fetchall()
        return [_row_to_record(row) for row in rows]

    def update_levels(self, watch_id: str, levels: list[float], checked_at: str) -> None:
        self.get(watch_id)  # raises NotFoundError if missing
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE level_watches SET last_levels = {ph}, last_checked_at = {ph} WHERE id = {ph}",
                (json.dumps(levels), checked_at, watch_id),
            )
            conn.commit()

    def mark_checked(self, watch_id: str, checked_at: str) -> None:
        """Same-levels case: bump last_checked_at without touching last_levels."""
        self.get(watch_id)
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE level_watches SET last_checked_at = {ph} WHERE id = {ph}", (checked_at, watch_id))
            conn.commit()

    def delete(self, watch_id: str) -> None:
        self.get(watch_id)  # raises NotFoundError if missing
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM level_watches WHERE id = {ph}", (watch_id,))
            conn.commit()
