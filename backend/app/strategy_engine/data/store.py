"""
Local bar store (SQLite).

Bars are downloaded once and kept, so:
  * a selection for a historical timestamp is reproducible (same bars ->
    same answer), identified by `data_version` -- a hash of exactly the
    rows used;
  * backtests don't spend API credits re-downloading;
  * premarket history accumulates from the day collection starts (the
    providers only serve ~3 months of intraday history).

Rows are keyed by (symbol, timeframe, source, ts). Re-downloading a range
upserts, so late corrections from a provider replace old values -- and
change the data_version of any range that includes them.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pandas as pd

from app.strategy_engine.models import Timeframe

DEFAULT_DB = Path(__file__).resolve().parents[3] / "data" / "strategy_engine" / "bars.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS bars (
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    source TEXT NOT NULL,
    ts INTEGER NOT NULL,          -- bar start, unix seconds UTC
    open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL,
    volume REAL NOT NULL,
    session TEXT NOT NULL,
    PRIMARY KEY (symbol, timeframe, source, ts)
);
CREATE TABLE IF NOT EXISTS fetch_log (
    symbol TEXT, timeframe TEXT, source TEXT,
    fetched_at TEXT, range_start INTEGER, range_end INTEGER, rows INTEGER, note TEXT
);
"""


class BarStore:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self):
        return sqlite3.connect(self.path)

    def upsert(self, symbol: str, timeframe: Timeframe, source: str, df: pd.DataFrame, note: str = "") -> int:
        """`df` must be normalized (UTC index, ohlcv + session)."""
        if df.empty:
            return 0
        secs = df.index.tz_convert("UTC").as_unit("s").asi8
        rows = [
            (symbol.upper(), str(timeframe), source, int(t), float(o), float(h), float(l), float(c), float(v), s)
            for t, o, h, l, c, v, s in zip(secs, df["open"], df["high"], df["low"], df["close"], df["volume"], df["session"])
        ]
        with self._conn() as c:
            c.executemany("INSERT OR REPLACE INTO bars VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
            c.execute("INSERT INTO fetch_log VALUES (?,?,?,datetime('now'),?,?,?,?)",
                      (symbol.upper(), str(timeframe), source, int(secs.min()), int(secs.max()), len(rows), note))
        return len(rows)

    def load(self, symbol: str, timeframe: Timeframe, source: str | None = None,
             start: pd.Timestamp | None = None, end: pd.Timestamp | None = None) -> pd.DataFrame:
        """Bars in [start, end). When `source` is None, each SESSION comes from
        exactly one provider (SESSION_SOURCE) -- never cross-filled, because
        the providers' volumes differ (~2x) and prices differ slightly, so
        mixing them inside one calculation (e.g. RVOL) would be inconsistent."""
        q = "SELECT ts, open, high, low, close, volume, session, source FROM bars WHERE symbol=? AND timeframe=?"
        args: list = [symbol.upper(), str(timeframe)]
        if source:
            q += " AND source=?"
            args.append(source)
        if start is not None:
            q += " AND ts>=?"
            args.append(int(pd.Timestamp(start).tz_convert("UTC").timestamp()))
        if end is not None:
            q += " AND ts<?"
            args.append(int(pd.Timestamp(end).tz_convert("UTC").timestamp()))
        with self._conn() as c:
            df = pd.read_sql_query(q, c, params=args)
        if df.empty:
            return _empty()
        if source is None:
            wanted = df["session"].map(lambda s: SESSION_SOURCE.get(s, DAILY_SOURCE))
            df = df[df["source"] == wanted]
        df.index = pd.to_datetime(df.pop("ts"), unit="s", utc=True).rename("timestamp")
        return df.sort_index()

    def coverage(self, symbol: str, timeframe: Timeframe) -> dict:
        with self._conn() as c:
            rows = c.execute("SELECT source, COUNT(*), MIN(ts), MAX(ts) FROM bars WHERE symbol=? AND timeframe=? GROUP BY source",
                             (symbol.upper(), str(timeframe))).fetchall()
        return {s: {"rows": n, "first": pd.Timestamp(a, unit="s", tz="UTC"), "last": pd.Timestamp(b, unit="s", tz="UTC")}
                for s, n, a, b in rows}


# Which provider serves each session. Twelve Data (Basic) has no extended
# hours; Tastytrade has them. Regular hours come from Twelve Data only.
SESSION_SOURCE = {"RTH": "twelvedata", "PREMARKET": "tastytrade", "AFTER_HOURS": "tastytrade"}
DAILY_SOURCE = "twelvedata"


def _empty() -> pd.DataFrame:
    return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "session", "source"],
                        index=pd.DatetimeIndex([], tz="UTC", name="timestamp"))


def data_version(*frames: pd.DataFrame) -> str:
    """Content hash of exactly the bars an answer was computed from."""
    h = hashlib.sha1()
    for df in frames:
        if df is None or df.empty:
            h.update(b"empty")
            continue
        h.update(df.index.tz_convert("UTC").as_unit("s").asi8.tobytes())
        h.update(df[["open", "high", "low", "close", "volume"]].to_numpy(dtype="float64").tobytes())
    return h.hexdigest()[:12]
