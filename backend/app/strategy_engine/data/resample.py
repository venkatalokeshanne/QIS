"""
Session-anchored resampling of regular-session bars.

Builds coarser intraday bars (65m, 2h, 4h, ...) from finer ones with the
grid anchored at each session's OPEN (09:30 ET), the way TrendSpider and
most charting platforms build them: 65m -> 09:30, 10:35, ... 14:55 (6 bars);
2h -> 09:30, 11:30, 13:30, 15:30 (last one partial). Premarket and
after-hours bars are never folded into regular-session bars.
"""

from __future__ import annotations

import pandas as pd

from app.strategy_engine.data.calendar import NY, session_bounds
from app.strategy_engine.models import Session, Timeframe


def resample_rth(df: pd.DataFrame, target: Timeframe) -> pd.DataFrame:
    """`df`: normalized intraday bars (any finer timeframe). Returns normalized
    RTH-only bars of `target` minutes, anchored at each day's open."""
    rth = df[df["session"] == Session.RTH.value]
    if rth.empty:
        return rth.copy()
    local = rth.index.tz_convert(NY)
    minutes = target.minutes
    keys = []
    for ts in local:
        b = session_bounds(ts.date())
        k = int((ts - b.open).total_seconds() // 60 // minutes)
        keys.append(b.open + pd.Timedelta(minutes=k * minutes))
    grouped = rth.groupby(pd.DatetimeIndex(keys).tz_convert("UTC"))
    out = pd.DataFrame({
        "open": grouped["open"].first(), "high": grouped["high"].max(), "low": grouped["low"].min(),
        "close": grouped["close"].last(), "volume": grouped["volume"].sum(),
    })
    out.index.name = "timestamp"
    out["session"] = Session.RTH.value
    return out
