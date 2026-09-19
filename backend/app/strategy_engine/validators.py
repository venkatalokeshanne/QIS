"""
Data-quality gate (spec section 42). No regime is classified from bad data:
if a check fails, the layer reports STATUS = DATA_INSUFFICIENT instead.

Checks: missing candles, duplicates, misaligned/future timestamps, timezone,
bars on market holidays, zero volume, possible unadjusted corporate actions,
insufficient history. Missing PREMARKET minutes are expected (thin trading)
and are never treated as errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.strategy_engine.data.calendar import NY, session_bounds
from app.strategy_engine.models import Session, Timeframe
from app.strategy_engine.thresholds import DATA_QUALITY_CONFIG

OK = "OK"
DATA_INSUFFICIENT = "DATA_INSUFFICIENT"


@dataclass
class DataQualityReport:
    symbol: str
    timeframe: str
    status: str = OK
    issues: list[str] = field(default_factory=list)      # each one makes the data insufficient
    warnings: list[str] = field(default_factory=list)    # reported, not blocking
    stats: dict = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.issues.append(message)
        self.status = DATA_INSUFFICIENT

    def to_dict(self) -> dict:
        return {"symbol": self.symbol, "timeframe": self.timeframe, "status": self.status,
                "issues": self.issues, "warnings": self.warnings, "stats": self.stats}


def check_bars(df: pd.DataFrame, symbol: str, timeframe: Timeframe, *, decision_ts: pd.Timestamp | None = None,
               min_bars: int | None = None, config: dict | None = None) -> DataQualityReport:
    cfg = {**DATA_QUALITY_CONFIG, **(config or {})}
    rep = DataQualityReport(symbol=symbol, timeframe=str(timeframe))
    if df is None or df.empty:
        rep.fail("no bars")
        return rep
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex) or idx.tz is None or str(idx.tz) != "UTC":
        rep.fail("timestamps must be a tz-aware UTC index (normalize the bars first)")
        return rep
    if not idx.is_monotonic_increasing:
        rep.fail("timestamps are not sorted")
    dups = int(idx.duplicated().sum())
    if dups:
        rep.fail(f"{dups} duplicate candles")
    if decision_ts is not None:
        ts = pd.Timestamp(decision_ts)
        ts = (ts.tz_localize(NY) if ts.tzinfo is None else ts).tz_convert("UTC")
        future = int((idx >= ts).sum())
        if future:
            rep.fail(f"{future} candles at/after the decision timestamp were passed in (look-ahead)")

    local = idx.tz_convert(NY)
    closed = [d for d in sorted(set(local.date)) if session_bounds(d) is None]
    if timeframe.is_intraday and closed:
        rep.fail(f"bars on {len(closed)} closed market days (e.g. {closed[0]})")

    if timeframe.is_intraday:
        _check_intraday(df, timeframe, rep, cfg)
    else:
        _check_daily(df, rep, cfg)

    need = min_bars if min_bars is not None else (cfg["min_daily_bars"] if not timeframe.is_intraday else None)
    if need is not None and len(df) < need:
        rep.fail(f"insufficient history: {len(df)} bars, need {need}")
    if timeframe.is_intraday:
        days = len(set(local[df["session"].values == Session.RTH.value].date)) if "session" in df else 0
        rep.stats["rth_days"] = days
        if days < cfg["min_intraday_days"]:
            rep.fail(f"insufficient history: {days} regular sessions, need {cfg['min_intraday_days']}")
    rep.stats["bars"] = len(df)
    rep.stats["first"] = str(idx.min())
    rep.stats["last"] = str(idx.max())
    return rep


def _check_intraday(df: pd.DataFrame, tf: Timeframe, rep: DataQualityReport, cfg: dict) -> None:
    if "session" not in df:
        rep.fail("bars carry no session tags")
        return
    rth = df[df["session"] == Session.RTH.value]
    if rth.empty:
        rep.fail("no regular-session bars")
        return
    local = rth.index.tz_convert(NY)
    minutes = tf.minutes
    # Alignment: RTH bar starts must sit on the session grid (open + k*tf).
    offsets = ((local.hour * 60 + local.minute) - (9 * 60 + 30)) % minutes
    misaligned = int((offsets != 0).sum()) if minutes < 390 else 0
    if misaligned:
        rep.fail(f"{misaligned} regular-session candles are not aligned to the {tf} grid")
    # Missing candles per day.
    counts = pd.Series(1, index=local).groupby(local.date).sum()
    incomplete = []
    for d, n in counts.items():
        b = session_bounds(d)
        expected = -(-int((b.close - b.open).total_seconds() // 60) // minutes)
        if n < cfg["min_rth_completeness"] * expected:
            incomplete.append((d, int(n), expected))
    rep.stats["incomplete_days"] = len(incomplete)
    if incomplete:
        frac = len(incomplete) / len(counts)
        msg = f"{len(incomplete)}/{len(counts)} sessions have missing regular-session candles (e.g. {incomplete[0][0]}: {incomplete[0][1]}/{incomplete[0][2]})"
        if frac > cfg["max_incomplete_day_fraction"]:
            rep.fail(msg)
        else:
            rep.warnings.append(msg)
    zero = float((rth["volume"] <= 0).mean())
    rep.stats["zero_volume_fraction"] = round(zero, 4)
    if zero > cfg["max_zero_volume_fraction"]:
        rep.fail(f"{zero:.1%} of regular-session candles have zero volume")
    pm = df[df["session"] == Session.PREMARKET.value]
    rep.stats["premarket_bars"] = len(pm)


def _check_daily(df: pd.DataFrame, rep: DataQualityReport, cfg: dict) -> None:
    local_dates = df.index.tz_convert(NY).date
    closed = [d for d in local_dates if session_bounds(d) is None]
    if closed:
        rep.warnings.append(f"{len(closed)} daily bars dated on non-trading days (e.g. {closed[0]})")
    zero = float((df["volume"] <= 0).mean())
    if zero > cfg["max_zero_volume_fraction"]:
        rep.fail(f"{zero:.1%} of daily bars have zero volume")
    # Possible unadjusted split: a huge close-to-open-to-close jump that the
    # next bars don't reverse is typical of an unadjusted corporate action.
    ret = df["close"].pct_change().abs()
    jumps = ret[ret > cfg["corporate_action_jump"]]
    if len(jumps):
        rep.warnings.append(f"{len(jumps)} daily moves > {cfg['corporate_action_jump']:.0%} "
                            f"(check for unadjusted splits), e.g. {jumps.index[0].date()}")
