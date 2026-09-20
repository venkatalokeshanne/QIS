"""
The historical backtest database the selection engine learns from.

Every strategy in the catalog is run once per ticker over the full stored
history, with the SAME execution settings the Run Backtests page uses (long
only, 0.05% slippage per fill, 2 ATR stop, 4 ATR target, 1% risk per trade,
closed at the session end). Its trades are then grouped by entry day, giving
exactly what a per-day backtest of that day would have produced:

    (date, ticker, strategy) -> return, pnl, trades, wins, win rate,
                                profit factor, expectancy, worst trade

Running once per strategy instead of once per day is not a shortcut: a
strategy's signals depend only on the bars up to each moment, so the trades
it enters on day D are the same either way -- and this way the warm-up
history is always complete, which a one-day run cannot guarantee.

Nothing here looks at the future: the grouping is by entry day, and each
day's numbers come only from that day's own trades.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
from dataclasses import asdict, replace
from pathlib import Path

import pandas as pd

from app.strategies.execution import ExecutionConfig
from app.strategies.registry import discover_strategies, get_strategy, strategy_registry
from app.strategy_engine.data.store import BarStore
from app.strategy_engine.evaluation import load_bars, to_qis_frame
from app.strategy_engine.models import Timeframe

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "strategy_engine" / "forecast.sqlite"

# The Run Backtests page's own defaults (frontend useResearchStore), so the
# learned ranking is the ranking the user actually sees.
RUN_EXECUTION = ExecutionConfig(
    capital=10_000.0,
    quantity=1.0,
    commission_per_trade=0.0,
    slippage_pct=0.0005,
    force_close_at_session_end=True,
)
RUN_EXECUTION_EXTRAS = {
    "direction_filter": "long_only",
    "atr_period": 14,
    "stop_loss_atr_multiple": 2,
    "take_profit_atr_multiple": 4,
    "risk_per_trade_pct": 0.01,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS backtest_trades (
    date TEXT NOT NULL, ticker TEXT NOT NULL, timeframe TEXT NOT NULL, strategy TEXT NOT NULL,
    entry_time INTEGER NOT NULL, exit_time INTEGER, direction TEXT,
    entry_price REAL, exit_price REAL, quantity REAL, pnl REAL, return_pct REAL, exit_reason TEXT
);
CREATE INDEX IF NOT EXISTS ix_bt_trades ON backtest_trades (ticker, timeframe, date);
CREATE TABLE IF NOT EXISTS daily_results (
    date TEXT NOT NULL, ticker TEXT NOT NULL, timeframe TEXT NOT NULL, strategy TEXT NOT NULL,
    trade_count INTEGER, wins INTEGER, losses INTEGER, win_rate REAL,
    pnl REAL, return_pct REAL, profit_factor REAL, expectancy REAL, worst_trade REAL,
    hold_hours REAL, run_id TEXT,
    PRIMARY KEY (date, ticker, timeframe, strategy)
);
CREATE TABLE IF NOT EXISTS backtest_runs (
    run_id TEXT PRIMARY KEY, created TEXT, timeframe TEXT, tickers TEXT, strategies INTEGER,
    bars_from TEXT, bars_to TEXT, execution TEXT, failures TEXT
);
"""


def _connect(path: Path | str = DEFAULT_DB) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path)
    c.executescript(SCHEMA)
    return c


def _execution() -> ExecutionConfig:
    cfg = RUN_EXECUTION
    for field, value in RUN_EXECUTION_EXTRAS.items():          # only those this build supports
        if hasattr(cfg, field):
            cfg = replace(cfg, **{field: value})
    return cfg


def run_catalog(ticker: str, timeframe: Timeframe, store: BarStore | None = None,
                strategies: list[str] | None = None, progress=None) -> tuple[pd.DataFrame, dict]:
    """Every strategy over one ticker's full history -> one row per trade."""
    discover_strategies()
    names = strategies or sorted(strategy_registry.names())
    bars = load_bars(store or BarStore(), ticker, timeframe)
    if bars.empty:
        raise ValueError(f"no stored {timeframe} bars for {ticker}")
    df = to_qis_frame(bars, ticker)
    cfg = _execution()
    rows, failures = [], {}
    for i, name in enumerate(names):
        strategy = get_strategy(name)
        try:
            trades = strategy.run(df, strategy.validate_params({}), cfg)
        except Exception as exc:                                # recorded, never silently dropped
            failures[name] = f"{type(exc).__name__}: {exc}"[:200]
            continue
        for t in trades:
            if t.exit_price is None or not t.entry_price:
                continue
            long = str(getattr(t.direction, "value", t.direction)).upper() == "LONG"
            ret = (t.exit_price / t.entry_price - 1) if long else (t.entry_price / t.exit_price - 1)
            rows.append({
                "date": pd.Timestamp(t.entry_time).date().isoformat(), "ticker": ticker.upper(),
                "timeframe": str(timeframe), "strategy": name,
                "entry_time": int(pd.Timestamp(t.entry_time).timestamp()),
                "exit_time": int(pd.Timestamp(t.exit_time).timestamp()) if t.exit_time is not None else None,
                "direction": str(getattr(t.direction, "value", t.direction)).upper(),
                "entry_price": float(t.entry_price), "exit_price": float(t.exit_price),
                "quantity": float(getattr(t, "quantity", 1) or 1), "pnl": float(getattr(t, "pnl", 0.0) or 0.0),
                "return_pct": float(ret), "exit_reason": str(getattr(t, "exit_reason", "") or ""),
            })
        if progress:
            progress(f"{ticker} {timeframe}: {i + 1}/{len(names)} strategies")
    return pd.DataFrame(rows), {"failures": failures, "names": names,
                                "bars_from": str(bars.index[0]), "bars_to": str(bars.index[-1])}


def daily_from_trades(trades: pd.DataFrame, names: list[str], tickers: list[str],
                      timeframe: str, dates: list[str]) -> pd.DataFrame:
    """Per (date, ticker, strategy) day metrics -- including the rows where a
    strategy did not trade, which a ranking has to contain to be honest."""
    if len(trades):
        g = trades.groupby(["date", "ticker", "timeframe", "strategy"])
        agg = g.agg(trade_count=("return_pct", "size"), wins=("return_pct", lambda s: int((s > 0).sum())),
                    pnl=("pnl", "sum"), return_pct=("return_pct", "sum"),
                    worst_trade=("return_pct", "min"),
                    gross_win=("return_pct", lambda s: float(s[s > 0].sum())),
                    gross_loss=("return_pct", lambda s: float(-s[s < 0].sum())),
                    hold_hours=("entry_time", "size")).reset_index()
        hold = g.apply(lambda z: float(((z["exit_time"] - z["entry_time"]) / 3600).sum())).rename("hold_h").reset_index()
        agg = agg.drop(columns=["hold_hours"]).merge(hold, on=["date", "ticker", "timeframe", "strategy"])
    else:
        agg = pd.DataFrame(columns=["date", "ticker", "timeframe", "strategy", "trade_count", "wins", "pnl",
                                    "return_pct", "worst_trade", "gross_win", "gross_loss", "hold_h"])
    full = pd.MultiIndex.from_product([dates, tickers, [timeframe], names],
                                      names=["date", "ticker", "timeframe", "strategy"]).to_frame(index=False)
    d = full.merge(agg, on=["date", "ticker", "timeframe", "strategy"], how="left")
    for col, default in (("trade_count", 0), ("wins", 0), ("pnl", 0.0), ("return_pct", 0.0),
                         ("gross_win", 0.0), ("gross_loss", 0.0), ("hold_h", 0.0)):
        d[col] = d[col].fillna(default)
    d["losses"] = d["trade_count"] - d["wins"]
    d["win_rate"] = (d["wins"] / d["trade_count"]).where(d["trade_count"] > 0)
    d["profit_factor"] = (d["gross_win"] / d["gross_loss"]).where(d["gross_loss"] > 0)
    d["expectancy"] = (d["return_pct"] / d["trade_count"]).where(d["trade_count"] > 0)
    return d.drop(columns=["gross_win", "gross_loss"]).rename(columns={"hold_h": "hold_hours"})


def build(tickers: list[str], timeframe: Timeframe, db_path: Path | str = DEFAULT_DB,
          strategies: list[str] | None = None, progress=None) -> dict:
    import uuid

    from app.strategy_engine.data.calendar import NY

    run_id = uuid.uuid4().hex[:12]
    store = BarStore()
    all_trades, info, failures = [], {}, {}
    for ticker in tickers:
        trades, meta = run_catalog(ticker, timeframe, store, strategies, progress)
        all_trades.append(trades)
        failures[ticker] = meta["failures"]
        info = meta
    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    # every session that has bars, so "no strategy traded" days are present too
    dates = sorted({str(d) for t in tickers
                    for d in load_bars(store, t, timeframe).index.tz_convert(NY).date})
    daily = daily_from_trades(trades, info["names"], [t.upper() for t in tickers], str(timeframe), dates)
    daily["run_id"] = run_id
    with _connect(db_path) as c:
        c.execute("DELETE FROM backtest_trades WHERE timeframe=?", (str(timeframe),))
        c.execute("DELETE FROM daily_results WHERE timeframe=?", (str(timeframe),))
        if len(trades):
            trades.to_sql("backtest_trades", c, if_exists="append", index=False)
        daily.to_sql("daily_results", c, if_exists="append", index=False)
        c.execute("INSERT OR REPLACE INTO backtest_runs VALUES (?,?,?,?,?,?,?,?,?)",
                  (run_id, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), str(timeframe),
                   ",".join(t.upper() for t in tickers), len(info["names"]), info["bars_from"], info["bars_to"],
                   str({**asdict(_execution()), **RUN_EXECUTION_EXTRAS}), str(failures)))
    return {"run_id": run_id, "trades": len(trades), "daily_rows": len(daily), "dates": len(dates),
            "strategies": len(info["names"]), "failures": {k: v for k, v in failures.items() if v}}


def load_daily(timeframe: str, db_path: Path | str = DEFAULT_DB) -> pd.DataFrame:
    with _connect(db_path) as c:
        return pd.read_sql_query("SELECT * FROM daily_results WHERE timeframe=?", c, params=[timeframe])
