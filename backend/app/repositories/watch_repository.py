"""
Watch repository.

A "watch" is a standing request to poll one symbol+interval on a
schedule and re-run one strategy's entry/exit logic against the
freshest bar, pushing an Expo notification when a new signal appears.
Same dual SQLite/Postgres backend switch as DatasetRepository (see
that module's docstring) -- Postgres in production so watches survive
Render's ephemeral disk, plain SQLite locally.
"""

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.config.settings import settings
from app.core.exceptions import NotFoundError

_SCHEMA = """
CREATE TABLE IF NOT EXISTS watches (
    id TEXT PRIMARY KEY,
    expo_push_token TEXT NOT NULL,
    symbol TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    strategy_params TEXT NOT NULL,
    interval TEXT NOT NULL,
    last_notified_bar_time TEXT,
    last_checked_at TEXT,
    created_at TEXT NOT NULL
);
"""

_COLUMNS = (
    "id, expo_push_token, symbol, strategy_name, strategy_params, interval, "
    "last_notified_bar_time, last_checked_at, created_at"
)


@dataclass(frozen=True)
class WatchRecord:
    id: str
    expo_push_token: str
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any]
    interval: str
    last_notified_bar_time: str | None
    last_checked_at: str | None
    created_at: str


def _row_to_record(row) -> WatchRecord:
    return WatchRecord(
        id=row[0],
        expo_push_token=row[1],
        symbol=row[2],
        strategy_name=row[3],
        strategy_params=json.loads(row[4]) if row[4] else {},
        interval=row[5],
        last_notified_bar_time=row[6],
        last_checked_at=row[7],
        created_at=row[8],
    )


class WatchRepository:
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

    def create(
        self,
        expo_push_token: str,
        symbol: str,
        strategy_name: str,
        strategy_params: dict[str, Any],
        interval: str,
    ) -> WatchRecord:
        record = WatchRecord(
            id=str(uuid.uuid4()),
            expo_push_token=expo_push_token,
            symbol=symbol.upper(),
            strategy_name=strategy_name,
            strategy_params=strategy_params or {},
            interval=interval,
            last_notified_bar_time=None,
            last_checked_at=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO watches ({_COLUMNS}) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                (
                    record.id,
                    record.expo_push_token,
                    record.symbol,
                    record.strategy_name,
                    json.dumps(record.strategy_params),
                    record.interval,
                    record.last_notified_bar_time,
                    record.last_checked_at,
                    record.created_at,
                ),
            )
            conn.commit()
        return record

    def get(self, watch_id: str) -> WatchRecord:
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_COLUMNS} FROM watches WHERE id = {ph}", (watch_id,))
            row = cur.fetchone()
        if row is None:
            raise NotFoundError(f"Watch '{watch_id}' not found.")
        return _row_to_record(row)

    def list_all(self) -> list[WatchRecord]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_COLUMNS} FROM watches ORDER BY created_at DESC")
            rows = cur.fetchall()
        return [_row_to_record(row) for row in rows]

    def list_for_token(self, expo_push_token: str) -> list[WatchRecord]:
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"SELECT {_COLUMNS} FROM watches WHERE expo_push_token = {ph} ORDER BY created_at DESC",
                (expo_push_token,),
            )
            rows = cur.fetchall()
        return [_row_to_record(row) for row in rows]

    def mark_checked(self, watch_id: str, checked_at: str, notified_bar_time: str | None = None) -> None:
        """
        Called by the poller after every evaluation. `notified_bar_time`
        is only passed (and persisted) when a new signal actually fired
        this check -- omitting it leaves the previous value in place, so
        an unchanged signal state doesn't repeatedly re-notify.
        """
        self.get(watch_id)  # raises NotFoundError if missing
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            if notified_bar_time is not None:
                cur.execute(
                    f"UPDATE watches SET last_checked_at = {ph}, last_notified_bar_time = {ph} WHERE id = {ph}",
                    (checked_at, notified_bar_time, watch_id),
                )
            else:
                cur.execute(
                    f"UPDATE watches SET last_checked_at = {ph} WHERE id = {ph}",
                    (checked_at, watch_id),
                )
            conn.commit()

    def delete(self, watch_id: str) -> None:
        self.get(watch_id)  # raises NotFoundError if missing
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM watches WHERE id = {ph}", (watch_id,))
            conn.commit()
