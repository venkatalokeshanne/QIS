"""
Market light: is today a green, yellow or red environment?

Two moving averages on the indices, nothing else:

    green  -- close above a RISING 21 EMA and 9 EMA above the 21
    red    -- close below a DECLINING 21 EMA and 9 EMA below the 21
    yellow -- anything else: flat 21 EMA, 9/21 disagreeing, price on the
              wrong side of a still-rising (or still-falling) average

It answers how much aggression the environment deserves, not what to buy.
Every light at bar t uses only bars up to t; forward returns appear only
in the descriptive stats, never in the light itself.

"Rising" and "declining" are measured in ATRs so the same threshold means
the same thing on SPY and on IWM, and on a daily chart and an hourly one:
the 21 EMA's change over the last SLOPE_BARS bars, divided by ATR(14).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv
from app.data.validator import validate_ohlcv
from app.integrations import twelvedata_client

INDICES = ("SPY", "QQQ", "IWM")
FAST, SLOW = 9, 21
ATR_PERIOD = 14
SLOPE_BARS = 5
FLAT_ATR = 0.2          # |21 EMA change over SLOPE_BARS| under 0.2 ATR counts as flat
STRUCTURE_BARS = 10     # HH/HL compares the last 10 bars against the 10 before them
HISTORY_BARS = 60
CACHE_SECONDS = 60

# timeframe -> (Twelve Data interval, bars to fetch)
TIMEFRAMES = {"1D": ("1day", 500), "1h": ("1h", 700), "15m": ("15min", 700)}

GREEN, YELLOW, RED = "green", "yellow", "red"


def _ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def _atr(df: pd.DataFrame, period: int) -> pd.Series:
    prev_close = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev_close).abs(),
                    (df["low"] - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()          # Wilder


def classify(df: pd.DataFrame) -> pd.DataFrame:
    """Per-bar light for an OHLC frame. Point-in-time: row t depends on rows <= t only."""
    out = pd.DataFrame(index=df.index)
    out["close"] = df["close"]
    out["ema9"] = _ema(df["close"], FAST)
    out["ema21"] = _ema(df["close"], SLOW)
    atr = _atr(df, ATR_PERIOD)
    out["slope_atr"] = (out["ema21"] - out["ema21"].shift(SLOPE_BARS)) / atr

    above = out["close"] > out["ema21"]
    below = out["close"] < out["ema21"]
    rising = out["slope_atr"] > FLAT_ATR
    falling = out["slope_atr"] < -FLAT_ATR
    stack_up = out["ema9"] > out["ema21"]
    stack_down = out["ema9"] < out["ema21"]

    light = np.where(above & rising & stack_up, GREEN,
                     np.where(below & falling & stack_down, RED, YELLOW))
    out["light"] = pd.Series(light, index=df.index).where(out["slope_atr"].notna(), None)

    # Structure is supporting evidence only -- it never changes the light.
    recent_high = df["high"].rolling(STRUCTURE_BARS).max()
    recent_low = df["low"].rolling(STRUCTURE_BARS).min()
    prior_high, prior_low = recent_high.shift(STRUCTURE_BARS), recent_low.shift(STRUCTURE_BARS)
    out["structure"] = np.where((recent_high > prior_high) & (recent_low > prior_low), "HH/HL",
                                np.where((recent_high < prior_high) & (recent_low < prior_low), "LH/LL", "mixed"))
    return out


def _reasons(row: pd.Series) -> list[str]:
    slope = row["slope_atr"]
    trend = "rising" if slope > FLAT_ATR else "declining" if slope < -FLAT_ATR else "flat"
    side = "above" if row["close"] > row["ema21"] else "below"
    stack = "9 EMA above 21" if row["ema9"] > row["ema21"] else "9 EMA below 21"
    return [f"Price {side} the 21 EMA", f"21 EMA {trend} ({slope:+.2f} ATR over {SLOPE_BARS} bars)", stack]


def composite(lights: list[str]) -> tuple[str, str]:
    """Indices agree -> that light. Any green-vs-red disagreement -> yellow."""
    g, r = lights.count(GREEN), lights.count(RED)
    if g >= 2 and r == 0:
        return GREEN, f"{g} of {len(lights)} indices green, none red"
    if r >= 2 and g == 0:
        return RED, f"{r} of {len(lights)} indices red, none green"
    if g and r:
        return YELLOW, "Indices disagree — some green, some red"
    return YELLOW, "No clear majority — conflicting or flat"


def _streak(lights: pd.Series) -> int:
    last = lights.iloc[-1]
    n = 0
    for v in reversed(lights.tolist()):
        if v != last:
            break
        n += 1
    return n


def light_stats(frame: pd.DataFrame) -> dict:
    """How the index itself behaved after each light. In-sample and descriptive:
    it shows what each environment has looked like, not a forecast."""
    fwd1 = frame["close"].shift(-1) / frame["close"] - 1
    fwd5 = frame["close"].shift(-5) / frame["close"] - 1
    stats = {}
    for light in (GREEN, YELLOW, RED):
        mask = frame["light"] == light
        f1, f5 = fwd1[mask].dropna(), fwd5[mask].dropna()
        stats[light] = {
            "bars": int(mask.sum()),
            "share_pct": round(float(mask.mean()) * 100, 1),
            "next_bar_avg_pct": round(float(f1.mean()) * 100, 3) if len(f1) else None,
            "next_5_avg_pct": round(float(f5.mean()) * 100, 3) if len(f5) else None,
            "next_bar_up_pct": round(float((f1 > 0).mean()) * 100, 1) if len(f1) else None,
        }
    return stats


@dataclass
class _Cached:
    at: float
    frame: pd.DataFrame


_cache: dict[tuple[str, str], _Cached] = {}


def _fetch(symbol: str, timeframe: str, fetch_bars) -> pd.DataFrame:
    interval, size = TIMEFRAMES[timeframe]
    key = (symbol, interval)
    hit = _cache.get(key)
    if hit and time.monotonic() - hit.at < CACHE_SECONDS and fetch_bars is twelvedata_client.fetch_historical_bars:
        return hit.frame
    raw = fetch_bars(symbol, interval=interval, outputsize=size)
    normalized = normalize_ohlcv(raw, detect_columns(raw))
    report = validate_ohlcv(normalized)
    if not report.is_valid:
        raise DataValidationError(f"Received unusable bars for '{symbol}' from the live data source.", issues=report.errors)
    _cache[key] = _Cached(time.monotonic(), normalized)
    return normalized


def index_light(symbol: str, bars: pd.DataFrame) -> dict:
    frame = classify(bars).dropna(subset=["light"])
    if frame.empty:
        raise DataValidationError(f"Not enough bars for '{symbol}' to compute the 21 EMA slope.")
    last = frame.iloc[-1]
    history = frame.tail(HISTORY_BARS)
    return {
        "symbol": symbol,
        "light": last["light"],
        "as_of": frame.index[-1].isoformat(),
        "close": round(float(last["close"]), 2),
        "ema9": round(float(last["ema9"]), 2),
        "ema21": round(float(last["ema21"]), 2),
        "slope_atr": round(float(last["slope_atr"]), 2),
        "distance_from_21_pct": round(float(last["close"] / last["ema21"] - 1) * 100, 2),
        "structure": last["structure"],
        "reasons": _reasons(last),
        "streak": _streak(frame["light"]),
        "history": [{"t": t.isoformat(), "light": v} for t, v in history["light"].items()],
        "stats": light_stats(frame),
    }


def get_market_light(timeframe: str = "1D", fetch_bars=twelvedata_client.fetch_historical_bars) -> dict:
    if timeframe not in TIMEFRAMES:
        raise DataValidationError(f"Unsupported timeframe '{timeframe}'. Use one of {', '.join(TIMEFRAMES)}.")
    indices = [index_light(sym, _fetch(sym, timeframe, fetch_bars)) for sym in INDICES]
    overall, why = composite([i["light"] for i in indices])

    # Composite history, aligned on the timestamps every index shares.
    per = {i["symbol"]: {h["t"]: h["light"] for h in i["history"]} for i in indices}
    shared = sorted(set.intersection(*(set(v) for v in per.values())))
    comp_history = [{"t": t, "light": composite([per[s][t] for s in per])[0]} for t in shared]

    return {
        "timeframe": timeframe,
        "light": overall,
        "reason": why,
        "indices": indices,
        "history": comp_history,
        "rules": {"fast": FAST, "slow": SLOW, "slope_bars": SLOPE_BARS, "flat_atr": FLAT_ATR},
    }
