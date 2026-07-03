"""
Dataset repository.

Metadata (name, row count, date range, detected columns) always lives
in a SQL table (`datasets`); which SQL engine depends on
`settings.database_url`:

- Unset (the default -- local dev, all existing tests): SQLite, with
  the actual OHLCV data stored as a CSV file per dataset on local
  disk. Fast, hermetic, no external dependency -- exactly how this
  worked before Postgres support existed.
- Set (e.g. a free-tier hosted Postgres in production): Postgres, with
  the CSV content stored as a column ALONGSIDE the metadata in the
  same row, rather than a local file. This is what makes data survive
  on hosts with ephemeral disk (e.g. Render's free tier) -- nothing is
  ever written to the container's own filesystem in this mode.

Both modes are exercised through the exact same public methods below,
so nothing else in the app (DatasetService and everything built on top
of it) needs to know or care which one is active.
"""

import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd

from app.config.settings import settings
from app.core.exceptions import NotFoundError

_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    original_filename TEXT,
    row_count INTEGER NOT NULL,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT NOT NULL
);
"""

_POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    original_filename TEXT,
    row_count INTEGER NOT NULL,
    start_date TEXT,
    end_date TEXT,
    created_at TEXT NOT NULL,
    csv_data TEXT NOT NULL
);
"""

_METADATA_COLUMNS = "id, name, original_filename, row_count, start_date, end_date, created_at"


@dataclass(frozen=True)
class DatasetRecord:
    id: str
    name: str
    original_filename: str
    row_count: int
    start_date: str | None
    end_date: str | None
    created_at: str


class DatasetRepository:
    def __init__(self):
        self._use_postgres = bool(settings.database_url)
        if self._use_postgres:
            import psycopg2  # local import: only needed in this mode

            self._psycopg2 = psycopg2
        else:
            settings.ensure_dirs()
            self._db_path = settings.db_path
            self._storage_dir = settings.dataset_storage_dir
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
        schema = _POSTGRES_SCHEMA if self._use_postgres else _SQLITE_SCHEMA
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(schema)
            conn.commit()

    def _csv_path(self, dataset_id: str) -> Path:
        return self._storage_dir / f"{dataset_id}.csv"

    def save(self, df: pd.DataFrame, name: str, original_filename: str) -> DatasetRecord:
        dataset_id = str(uuid.uuid4())
        record = DatasetRecord(
            id=dataset_id,
            name=name,
            original_filename=original_filename,
            row_count=len(df),
            start_date=str(df.index.min()) if not df.empty else None,
            end_date=str(df.index.max()) if not df.empty else None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            if self._use_postgres:
                csv_buffer = StringIO()
                df.to_csv(csv_buffer)
                cur.execute(
                    f"INSERT INTO datasets ({_METADATA_COLUMNS}, csv_data) "
                    f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                    (
                        record.id,
                        record.name,
                        record.original_filename,
                        record.row_count,
                        record.start_date,
                        record.end_date,
                        record.created_at,
                        csv_buffer.getvalue(),
                    ),
                )
            else:
                df.to_csv(self._csv_path(dataset_id))
                cur.execute(
                    f"INSERT INTO datasets ({_METADATA_COLUMNS}) "
                    f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                    (
                        record.id,
                        record.name,
                        record.original_filename,
                        record.row_count,
                        record.start_date,
                        record.end_date,
                        record.created_at,
                    ),
                )
            conn.commit()
        return record

    def get_metadata(self, dataset_id: str) -> DatasetRecord:
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_METADATA_COLUMNS} FROM datasets WHERE id = {ph}", (dataset_id,))
            row = cur.fetchone()
        if row is None:
            raise NotFoundError(f"Dataset '{dataset_id}' not found.")
        return DatasetRecord(*row)

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame:
        if self._use_postgres:
            ph = self._ph()
            with self._connection() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT csv_data FROM datasets WHERE id = {ph}", (dataset_id,))
                row = cur.fetchone()
            if row is None:
                raise NotFoundError(f"Dataset '{dataset_id}' not found.")
            return pd.read_csv(StringIO(row[0]), index_col="timestamp", parse_dates=["timestamp"])

        self.get_metadata(dataset_id)  # raises NotFoundError if missing
        path = self._csv_path(dataset_id)
        return pd.read_csv(path, index_col="timestamp", parse_dates=["timestamp"])

    def list_all(self) -> list[DatasetRecord]:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {_METADATA_COLUMNS} FROM datasets ORDER BY created_at DESC")
            rows = cur.fetchall()
        return [DatasetRecord(*row) for row in rows]

    def delete(self, dataset_id: str) -> None:
        self.get_metadata(dataset_id)  # raises NotFoundError if missing
        ph = self._ph()
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM datasets WHERE id = {ph}", (dataset_id,))
            conn.commit()
        if not self._use_postgres:
            self._csv_path(dataset_id).unlink(missing_ok=True)
