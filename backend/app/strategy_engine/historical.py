"""
Historical regime + strategy-performance database (spec sections 45-47).

Tables (SQLite, backend/data/strategy_engine/engine.sqlite):
  market_regime_history      one row per trading day, as known after its close
  ticker_regime_history      one row per ticker per trading day
  premarket_regime_history   one row per ticker per day, at a fixed decision time
  strategy_trades            every backtest trade, tagged with the regimes that
                             were KNOWN BEFORE its entry (no look-ahead)
  strategy_regime_performance  aggregated results: all-time and per regime
  evaluation_runs            provenance of every evaluation (data/config/catalog versions)
  selection_log              every selection decision (spec 49)

Point-in-time tagging: a trade entering at time t is tagged with the market
and ticker regime of the last session whose CLOSE is <= t, and with the
premarket regime of its own day only if that premarket had ended by t.
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY, previous_trading_day, session_bounds

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "strategy_engine" / "engine.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS market_regime_history (
    date TEXT PRIMARY KEY, known_at INTEGER NOT NULL,
    spy_direction TEXT, qqq_direction TEXT, iwm_direction TEXT,
    market_direction TEXT, market_volatility TEXT, breadth TEXT, market_regime TEXT,
    config_version TEXT
);
CREATE TABLE IF NOT EXISTS ticker_regime_history (
    ticker TEXT NOT NULL, date TEXT NOT NULL, known_at INTEGER NOT NULL,
    trend TEXT, momentum TEXT, relative_strength TEXT, volatility TEXT, volume TEXT, gap TEXT,
    ticker_regime TEXT, config_version TEXT,
    PRIMARY KEY (ticker, date)
);
CREATE TABLE IF NOT EXISTS premarket_regime_history (
    ticker TEXT NOT NULL, date TEXT NOT NULL, decision_time TEXT NOT NULL, known_at INTEGER NOT NULL,
    premarket_data_through TEXT, premarket_status TEXT, premarket_change_pct REAL, premarket_range_pct REAL,
    premarket_structure TEXT, premarket_volume REAL, premarket_rvol REAL, premarket_liquidity TEXT,
    premarket_reliability TEXT, premarket_catalyst TEXT, premarket_regime TEXT, config_version TEXT,
    PRIMARY KEY (ticker, date, decision_time)
);
CREATE TABLE IF NOT EXISTS strategy_trades (
    run_id TEXT NOT NULL, ticker TEXT NOT NULL, strategy_id INTEGER NOT NULL, timeframe TEXT NOT NULL,
    variant TEXT NOT NULL,                 -- "base" or a parameter-neighbour id
    entry_time INTEGER NOT NULL, exit_time INTEGER, direction TEXT,
    entry_price REAL, exit_price REAL, gross_return REAL,
    market_regime TEXT, ticker_regime TEXT, premarket_regime TEXT,
    sample TEXT                            -- IN_SAMPLE | OUT_OF_SAMPLE
);
CREATE INDEX IF NOT EXISTS ix_trades ON strategy_trades (ticker, strategy_id, timeframe, variant);
CREATE TABLE IF NOT EXISTS strategy_regime_performance (
    ticker TEXT NOT NULL, strategy_id INTEGER NOT NULL, family TEXT, timeframe TEXT NOT NULL,
    scope TEXT NOT NULL,                   -- ALL_TIME | MARKET | TICKER | PREMARKET | MARKET_TICKER
    market_regime TEXT NOT NULL, ticker_regime TEXT NOT NULL, premarket_regime TEXT NOT NULL,
    trade_count INTEGER, win_rate REAL, profit_factor REAL, expectancy REAL, sharpe REAL, max_drawdown REAL,
    oos_profit_factor REAL, walk_forward_pass_rate REAL, parameter_stability REAL, slippage_robustness TEXT,
    qualification_status TEXT, details TEXT, run_id TEXT, last_updated TEXT,
    PRIMARY KEY (ticker, strategy_id, timeframe, scope, market_regime, ticker_regime, premarket_regime)
);
CREATE TABLE IF NOT EXISTS evaluation_runs (
    run_id TEXT PRIMARY KEY, ticker TEXT, strategy_id INTEGER, timeframe TEXT,
    started TEXT, finished TEXT, bars_from TEXT, bars_to TEXT,
    data_version TEXT, config_version TEXT, catalog_version TEXT, status TEXT, error TEXT, summary TEXT
);
CREATE TABLE IF NOT EXISTS selection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, logged_at TEXT, decision_ts TEXT, ticker TEXT, timeframe TEXT,
    market_regime TEXT, ticker_regime TEXT, premarket_regime TEXT, premarket_data_through TEXT,
    candidate_families TEXT, candidate_strategies TEXT, qualification_results TEXT,
    final_qualified_strategies TEXT, status TEXT,
    data_version TEXT, configuration_version TEXT, catalog_version TEXT
);
"""

ANY = "*"   # wildcard in strategy_regime_performance rows


class EngineDB:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as c:
            c.executescript(SCHEMA)

    def conn(self):
        return sqlite3.connect(self.path)

    # -- regime histories -------------------------------------------------------
    def write_market_history(self, hist: pd.DataFrame, config_version: str) -> int:
        rows = []
        for idx, r in hist.iterrows():
            d = idx.tz_convert(NY).date()
            b = session_bounds(d)
            if b is None or r["market_regime"] is None:
                continue
            rows.append((str(d), int(b.close.timestamp()), r.get("spy_direction"), r.get("qqq_direction"),
                         r.get("iwm_direction"), r["market_direction"], r["market_volatility"], r["breadth"],
                         r["market_regime"], config_version))
        with self.conn() as c:
            c.executemany("INSERT OR REPLACE INTO market_regime_history VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
        return len(rows)

    def write_ticker_history(self, hist: pd.DataFrame, config_version: str) -> int:
        rows = []
        for idx, r in hist.iterrows():
            d = idx.tz_convert(NY).date()
            b = session_bounds(d)
            if b is None or r["ticker_regime"] is None:
                continue
            rows.append((r["ticker"], str(d), int(b.close.timestamp()), r["trend"], r["momentum"],
                         r["relative_strength"], r["volatility"], r["volume"], r["gap"], r["ticker_regime"], config_version))
        with self.conn() as c:
            c.executemany("INSERT OR REPLACE INTO ticker_regime_history VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
        return len(rows)

    def write_premarket_rows(self, rows: list[dict], config_version: str) -> int:
        vals = [(r["ticker"], r["date"], r["decision_time"], r["known_at"], r.get("premarket_data_through"),
                 r["premarket_status"], r.get("premarket_change_pct"), r.get("premarket_range_pct"),
                 r.get("premarket_structure"), r.get("premarket_volume"), r.get("premarket_rvol"),
                 r.get("premarket_liquidity"), r.get("premarket_reliability"), r.get("premarket_catalyst"),
                 r["premarket_regime"], config_version) for r in rows]
        with self.conn() as c:
            c.executemany("INSERT OR REPLACE INTO premarket_regime_history VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", vals)
        return len(vals)

    def load_market_history(self) -> pd.DataFrame:
        with self.conn() as c:
            return pd.read_sql_query("SELECT * FROM market_regime_history ORDER BY known_at", c)

    def load_ticker_history(self, ticker: str) -> pd.DataFrame:
        with self.conn() as c:
            return pd.read_sql_query("SELECT * FROM ticker_regime_history WHERE ticker=? ORDER BY known_at", c,
                                     params=[ticker.upper()])

    def load_premarket_history(self, ticker: str) -> pd.DataFrame:
        with self.conn() as c:
            return pd.read_sql_query("SELECT * FROM premarket_regime_history WHERE ticker=? ORDER BY known_at", c,
                                     params=[ticker.upper()])

    # -- trades / performance ------------------------------------------------------
    def replace_trades(self, run_id: str, ticker: str, strategy_id: int, timeframe: str, trades: pd.DataFrame) -> None:
        with self.conn() as c:
            c.execute("DELETE FROM strategy_trades WHERE ticker=? AND strategy_id=? AND timeframe=?",
                      (ticker.upper(), strategy_id, timeframe))
            c.executemany("INSERT INTO strategy_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
                (run_id, ticker.upper(), strategy_id, timeframe, r.variant, int(r.entry_time), _int_or_none(r.exit_time),
                 r.direction, r.entry_price, r.exit_price, r.gross_return, r.market_regime, r.ticker_regime,
                 r.premarket_regime, r.sample) for r in trades.itertuples()])

    def load_trades(self, ticker: str, strategy_id: int, timeframe: str, variant: str | None = "base") -> pd.DataFrame:
        q = "SELECT * FROM strategy_trades WHERE ticker=? AND strategy_id=? AND timeframe=?"
        args: list = [ticker.upper(), strategy_id, timeframe]
        if variant is not None:
            q += " AND variant=?"
            args.append(variant)
        with self.conn() as c:
            return pd.read_sql_query(q + " ORDER BY entry_time", c, params=args)

    def replace_performance(self, ticker: str, strategy_id: int, timeframe: str, rows: list[dict]) -> None:
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        with self.conn() as c:
            c.execute("DELETE FROM strategy_regime_performance WHERE ticker=? AND strategy_id=? AND timeframe=?",
                      (ticker.upper(), strategy_id, timeframe))
            c.executemany("INSERT INTO strategy_regime_performance VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
                (ticker.upper(), strategy_id, r["family"], timeframe, r["scope"], r["market_regime"], r["ticker_regime"],
                 r["premarket_regime"], r["trade_count"], r["win_rate"], r["profit_factor"], r["expectancy"], r["sharpe"],
                 r["max_drawdown"], r.get("oos_profit_factor"), r.get("walk_forward_pass_rate"), r.get("parameter_stability"),
                 r.get("slippage_robustness"), r.get("qualification_status"), json.dumps(r.get("details", {}), default=str),
                 r.get("run_id"), now) for r in rows])

    def load_performance(self, ticker: str, strategy_id: int, timeframe: str) -> pd.DataFrame:
        with self.conn() as c:
            return pd.read_sql_query("SELECT * FROM strategy_regime_performance WHERE ticker=? AND strategy_id=? AND timeframe=?",
                                     c, params=[ticker.upper(), strategy_id, timeframe])

    def record_run(self, **kw) -> None:
        cols = ["run_id", "ticker", "strategy_id", "timeframe", "started", "finished", "bars_from", "bars_to",
                "data_version", "config_version", "catalog_version", "status", "error", "summary"]
        with self.conn() as c:
            c.execute(f"INSERT OR REPLACE INTO evaluation_runs ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                      [kw.get(k) if not isinstance(kw.get(k), (dict, list)) else json.dumps(kw.get(k), default=str) for k in cols])

    def latest_run(self, ticker: str, strategy_id: int, timeframe: str) -> dict | None:
        with self.conn() as c:
            c.row_factory = sqlite3.Row
            r = c.execute("SELECT * FROM evaluation_runs WHERE ticker=? AND strategy_id=? AND timeframe=? ORDER BY finished DESC LIMIT 1",
                          (ticker.upper(), strategy_id, timeframe)).fetchone()
        return dict(r) if r else None

    def log_selection(self, record: dict) -> int:
        cols = ["logged_at", "decision_ts", "ticker", "timeframe", "market_regime", "ticker_regime", "premarket_regime",
                "premarket_data_through", "candidate_families", "candidate_strategies", "qualification_results",
                "final_qualified_strategies", "status", "data_version", "configuration_version", "catalog_version"]
        vals = [record.get(k) if not isinstance(record.get(k), (dict, list)) else json.dumps(record.get(k), default=str)
                for k in cols]
        with self.conn() as c:
            cur = c.execute(f"INSERT INTO selection_log ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", vals)
            return int(cur.lastrowid)


# ----------------------------------------------------------------------------
# point-in-time tagging
# ----------------------------------------------------------------------------


def tag_trades(entries_utc_s: np.ndarray, market_hist: pd.DataFrame, ticker_hist: pd.DataFrame,
               premarket_hist: pd.DataFrame | None, uses_premarket: bool) -> pd.DataFrame:
    """Regime labels known BEFORE each entry time (unix seconds UTC)."""
    def last_known(hist: pd.DataFrame, col: str) -> list:
        if hist is None or hist.empty:
            return [None] * len(entries_utc_s)
        known = hist["known_at"].to_numpy()
        pos = np.searchsorted(known, entries_utc_s, side="right") - 1
        vals = hist[col].to_numpy()
        return [vals[p] if p >= 0 else None for p in pos]

    out = pd.DataFrame({"market_regime": last_known(market_hist, "market_regime"),
                        "ticker_regime": last_known(ticker_hist, "ticker_regime")})
    if uses_premarket and premarket_hist is not None and not premarket_hist.empty:
        by_day = {row.date: (row.known_at, row.premarket_regime) for row in premarket_hist.itertuples()}
        labels = []
        for t in entries_utc_s:
            day = str(pd.Timestamp(int(t), unit="s", tz="UTC").tz_convert(NY).date())
            known_at, label = by_day.get(day, (None, None))
            labels.append(label if known_at is not None and known_at <= t else "NOT_AVAILABLE")
        out["premarket_regime"] = labels
    else:
        out["premarket_regime"] = "NOT_APPLICABLE" if not uses_premarket else "NOT_AVAILABLE"
    return out


def _int_or_none(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None
