"""
Point-in-time context for each (date, ticker).

Phase 1 uses the regime labels the strategy engine already persists, joined on
the rule that decides everything here: a row may only carry values whose
`known_at` is at or before the prediction time (09:25 ET by default). The
market and ticker regimes are stamped after the previous close, the premarket
regime at 09:25, so all three are legitimately available before the open.

Phase 2 adds the numeric feature set (gaps, RVOL, ATR, ADX, breadth, relative
strength) from the bar store; the same known_at discipline applies there.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.strategy_engine.data.calendar import NY
from app.strategy_engine.historical import EngineDB

PREDICTION_TIME = "09:25"


def _as_of(dates: np.ndarray, time_str: str) -> np.ndarray:
    return np.array([int(pd.Timestamp(f"{d} {time_str}", tz=NY).timestamp()) for d in dates])


def attach_regimes(d: pd.DataFrame, prediction_time: str = PREDICTION_TIME,
                   db: EngineDB | None = None) -> pd.DataFrame:
    """Add market_regime / ticker_regime / premarket_regime as known at
    `prediction_time` on each row's date. Rows with no regime yet get
    "UNKNOWN" rather than a guess."""
    db = db or EngineDB()
    out = d.copy()
    dates = np.array(sorted(out["date"].unique()))
    ts = _as_of(dates, prediction_time)

    market = db.load_market_history()
    idx = np.searchsorted(market["known_at"].to_numpy(), ts, side="right") - 1
    market_by_date = {date: (market["market_regime"].to_numpy()[i] if i >= 0 else "UNKNOWN")
                      for date, i in zip(dates, idx)}
    out["market_regime"] = out["date"].map(market_by_date).fillna("UNKNOWN")

    ticker_regime, premarket = {}, {}
    for ticker in sorted(out["ticker"].unique()):
        hist = db.load_ticker_history(ticker)
        if len(hist):
            i = np.searchsorted(hist["known_at"].to_numpy(), ts, side="right") - 1
            for date, pos in zip(dates, i):
                ticker_regime[(ticker, date)] = hist["ticker_regime"].to_numpy()[pos] if pos >= 0 else "UNKNOWN"
        pm = db.load_premarket_history(ticker)
        if len(pm):
            known = {r.date: r for r in pm.itertuples()}
            for date, t in zip(dates, ts):
                row = known.get(date)
                premarket[(ticker, date)] = row.premarket_regime if row is not None and row.known_at <= t \
                    else "PREMARKET_DATA_UNAVAILABLE"
    pairs = list(zip(out["ticker"], out["date"]))
    out["ticker_regime"] = [ticker_regime.get(p, "UNKNOWN") for p in pairs]
    out["premarket_regime"] = [premarket.get(p, "PREMARKET_DATA_UNAVAILABLE") for p in pairs]
    return out
