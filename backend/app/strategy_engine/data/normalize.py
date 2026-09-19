"""
Bar normalization: one canonical frame shape for every layer.

Canonical frame:
  * index `timestamp`: tz-aware UTC DatetimeIndex, bar START time, unique, sorted
  * columns: open, high, low, close, volume (float), session (str)
  * session in {PREMARKET, RTH, AFTER_HOURS} for intraday bars, DAILY for
    daily-and-coarser bars

Session tagging uses the NYSE calendar in America/New_York (DST-aware).
Intraday bars outside 04:00-20:00 (overnight) or on closed days are
dropped, and counted, rather than silently mixed into a session.
Premarket bars are never forward-filled: a missing premarket minute means
nothing traded.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.strategy_engine.data.calendar import NY, session_bounds
from app.strategy_engine.models import Session, Timeframe

OHLCV = ["open", "high", "low", "close", "volume"]


@dataclass
class NormalizationReport:
    input_rows: int = 0
    output_rows: int = 0
    duplicates_dropped: int = 0
    invalid_ohlc_dropped: int = 0
    outside_session_dropped: int = 0
    closed_day_dropped: int = 0
    notes: list[str] = field(default_factory=list)


def to_utc_index(values, assume_tz: str = "America/New_York") -> pd.DatetimeIndex:
    """Naive timestamps are interpreted in `assume_tz` (exchange time), aware ones are converted."""
    idx = pd.DatetimeIndex(pd.to_datetime(values))
    if idx.tz is None:
        idx = idx.tz_localize(assume_tz, ambiguous="infer", nonexistent="shift_forward")
    return idx.tz_convert("UTC").as_unit("ns")


def tag_sessions(index_utc: pd.DatetimeIndex) -> pd.Series:
    """Session label per bar start, or None when outside 04:00-20:00 / closed day."""
    local = index_utc.tz_convert(NY)
    labels = []
    cache: dict = {}
    for ts in local:
        d = ts.date()
        if d not in cache:
            cache[d] = session_bounds(d)
        b = cache[d]
        if b is None:
            labels.append(None)
        elif b.premarket_start <= ts < b.open:
            labels.append(Session.PREMARKET.value)
        elif b.open <= ts < b.close:
            labels.append(Session.RTH.value)
        elif b.close <= ts < b.after_hours_end:
            labels.append(Session.AFTER_HOURS.value)
        else:
            labels.append(None)
    return pd.Series(labels, index=index_utc, dtype=object)


def normalize_bars(raw: pd.DataFrame, timeframe: Timeframe, *, time_column: str | None = None,
                   assume_tz: str = "America/New_York") -> tuple[pd.DataFrame, NormalizationReport]:
    rep = NormalizationReport(input_rows=len(raw))
    df = raw.copy()
    if time_column is None:
        time_column = next((c for c in ("timestamp", "datetime", "date", "time") if c in df.columns), None)
    if time_column is not None:
        df.index = to_utc_index(df[time_column], assume_tz)
        df = df.drop(columns=[time_column])
    else:
        df.index = to_utc_index(df.index, assume_tz)
    df.index.name = "timestamp"
    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"bars are missing columns {missing}")
    df = df[OHLCV].astype(float).sort_index()

    dup = df.index.duplicated(keep="first")
    rep.duplicates_dropped = int(dup.sum())
    df = df[~dup]

    bad = (df["high"] < df[["open", "close", "low"]].max(axis=1)) | (df["low"] > df[["open", "close", "high"]].min(axis=1)) \
        | (df[["open", "high", "low", "close"]] <= 0).any(axis=1) | df[OHLCV].isna().any(axis=1) | (df["volume"] < 0)
    rep.invalid_ohlc_dropped = int(bad.sum())
    df = df[~bad]

    if timeframe.is_intraday:
        sessions = tag_sessions(df.index)
        local_days = df.index.tz_convert(NY).date
        closed = pd.Series([session_bounds(d) is None for d in local_days], index=df.index)
        rep.closed_day_dropped = int(closed.sum())
        outside = sessions.isna() & ~closed
        rep.outside_session_dropped = int(outside.sum())
        keep = sessions.notna()
        df = df[keep.values].copy()
        df["session"] = sessions[keep].values
    else:
        df = df.copy()
        df["session"] = Session.DAILY.value
    rep.output_rows = len(df)
    return df, rep


def select_session(df: pd.DataFrame, *sessions: Session | str) -> pd.DataFrame:
    """Explicit session selection -- the only sanctioned way to combine sessions."""
    wanted = {str(s) for s in sessions}
    return df[df["session"].isin(wanted)]


def upto(df: pd.DataFrame, decision_ts: pd.Timestamp, bar_minutes: int | None) -> pd.DataFrame:
    """Bars fully COMPLETED before `decision_ts` (no look-ahead).

    A bar starting at t covering `bar_minutes` is complete at t + bar_minutes.
    For daily bars (bar_minutes None) a bar is complete at that day's close,
    which the caller encodes by passing the daily frame's session-close index
    or by using `daily_upto`.
    """
    ts = pd.Timestamp(decision_ts)
    ts = ts.tz_localize(NY) if ts.tzinfo is None else ts
    ts = ts.tz_convert("UTC")
    if bar_minutes is None:
        return df[df.index < ts]
    return df[df.index + pd.Timedelta(minutes=bar_minutes) <= ts]


def daily_upto(daily: pd.DataFrame, decision_ts: pd.Timestamp) -> pd.DataFrame:
    """Daily bars whose session had CLOSED by `decision_ts`.

    Daily bars are stamped at the trading date; the bar for date D is only
    final after D's close (16:00 ET, or 13:00 on early-close days).
    """
    ts = pd.Timestamp(decision_ts)
    ts = ts.tz_localize(NY) if ts.tzinfo is None else ts
    local_dates = daily.index.tz_convert(NY).date
    keep = []
    for d in local_dates:
        b = session_bounds(d)
        close = b.close if b else pd.Timestamp(d, tz=NY) + pd.Timedelta(hours=16)
        keep.append(close <= ts)
    return daily[keep]
