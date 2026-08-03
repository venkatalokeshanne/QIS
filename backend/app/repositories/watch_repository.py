"""
Watch repository.

A "watch" is a standing request to poll one symbol+interval on a
schedule and re-run one strategy's entry/exit logic against the
freshest bar, sending a Telegram message the moment a new signal
appears. Its execution_settings snapshot (commission, slippage, stop
loss/take profit, direction filter, etc.) is captured at creation time
from whatever the user's Settings page held then -- app.services.
live_signal_engine and app.services.signal_service.check_signal both
run the strategy through that same execution config, so a live alert's
entries/exits match what a backtest with those same settings would
have produced (force_close_at_session_end is always forced off for
live checks regardless of what's stored -- see check_signal's
docstring for why). Same dual SQLite/Postgres backend switch as other
repositories in this app -- Postgres in production so watches survive
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
    symbol TEXT NOT NULL,
    strategy_name TEXT NOT NULL,
    strategy_params TEXT NOT NULL,
    interval TEXT NOT NULL,
    execution_settings TEXT NOT NULL,
    last_notified_bar_time TEXT,
    last_checked_at TEXT,
    created_at TEXT NOT NULL
);
"""

_COLUMNS = (
    "id, symbol, strategy_name, strategy_params, interval, execution_settings, "
    "last_notified_bar_time, last_checked_at, created_at"
)

# Columns _SCHEMA must have -- used to detect a stale pre-existing local
# table (e.g. from before execution_settings or expo_push_token was
# removed) and rebuild it rather than silently failing on the first
# insert with a mismatched column set. Old rows are moot either way
# (expo tokens are gone, and pre-existing watches never had a captured
# execution snapshot to migrate), so dropping is simpler and safe for
# this single-user app's local/dev data.
_REQUIRED_COLUMNS = {"execution_settings"}


@dataclass(frozen=True)
class WatchRecord:
    id: str
    symbol: str
    strategy_name: str
    strategy_params: dict[str, Any]
    interval: str
    execution_settings: dict[str, Any]
    last_notified_bar_time: str | None
    last_checked_at: str | None
    created_at: str


def _row_to_record(row) -> WatchRecord:
    return WatchRecord(
        id=row[0],
        symbol=row[1],
        strategy_name=row[2],
        strategy_params=json.loads(row[3]) if row[3] else {},
        interval=row[4],
        execution_settings=json.loads(row[5]) if row[5] else {},
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
            if self._use_postgres:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'watches'")
                existing_columns = {row[0] for row in cur.fetchall()}
            else:
                cur.execute("PRAGMA table_info(watches)")
                existing_columns = {row[1] for row in cur.fetchall()}
            table_exists = bool(existing_columns)
            has_stale_schema = table_exists and not _REQUIRED_COLUMNS.issubset(existing_columns)
            if has_stale_schema:
                cur.execute("DROP TABLE watches")
            cur.execute(_SCHEMA)
            conn.commit()

    def create(
        self,
        symbol: str,
        strategy_name: str,
        strategy_params: dict[str, Any],
        interval: str,
        execution_settings: dict[str, Any] | None = None,
    ) -> WatchRecord:
        record = WatchRecord(
            id=str(uuid.uuid4()),
            symbol=symbol.upper(),
            strategy_name=strategy_name,
            strategy_params=strategy_params or {},
            interval=interval,
            execution_settings=execution_settings or {},
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
                    record.symbol,
                    record.strategy_name,
                    json.dumps(record.strategy_params),
                    record.interval,
                    json.dumps(record.execution_settings),
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
