"""Step 4: ticker regime detector (spec 13-22, 48)."""

import datetime as dt

import numpy as np
import pandas as pd

from app.strategy_engine.data.normalize import normalize_bars
from app.strategy_engine.models import Timeframe
from app.strategy_engine.ticker_regime import TickerRegimeDetector

DAYS = pd.bdate_range("2024-01-02", periods=420)
DAYS = DAYS[~DAYS.isin(pd.to_datetime(["2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19", "2024-07-04",
                                        "2024-09-02", "2024-11-28", "2024-12-25", "2025-01-01", "2025-01-09",
                                        "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26", "2025-06-19"]))]


def daily(drift, noise=0.3, seed=0, spread=1.0, vol_from=None, base=100.0):
    rng = np.random.default_rng(seed)
    t = np.arange(len(DAYS))
    close = base * np.exp(drift * t + rng.normal(0, noise / 100, len(t)).cumsum())
    spread = np.asarray(spread, dtype=float) if np.ndim(spread) else np.full(len(t), float(spread))
    rng_hl = spread * close / 100
    if vol_from is not None:
        rng_hl[vol_from:] *= 5
    raw = pd.DataFrame({"date": DAYS, "open": close * (1 - 0.001), "high": close + rng_hl, "low": close - rng_hl,
                        "close": close, "volume": 2e6})
    return normalize_bars(raw, Timeframe.D1)[0]


BENCH = {"SPY": daily(0.0003, seed=11), "QQQ": daily(0.0003, seed=12)}


def at(day_index, hhmm="17:00"):
    d = DAYS[day_index].date()
    return pd.Timestamp(f"{d} {hhmm}", tz="America/New_York")


def test_strong_uptrend_with_relative_strength():
    r = TickerRegimeDetector().detect("UPCO", daily(0.004, seed=1), BENCH, at(-1))
    assert r.status == "OK", r.reasons
    assert r.trend == "STRONG_UPTREND"
    assert r.momentum in ("STRONG", "POSITIVE")
    assert r.relative_strength == "STRONG_RELATIVE_STRENGTH"
    assert r.ticker_regime.startswith("HIGH_MOMENTUM_")


def test_downtrend_with_weak_relative_strength():
    r = TickerRegimeDetector().detect("DNCO", daily(-0.004, seed=2), BENCH, at(-1))
    assert r.trend in ("STRONG_DOWNTREND", "DOWNTREND")
    assert r.relative_strength == "WEAK_RELATIVE_STRENGTH"


def test_ticker_is_independent_of_the_market():
    # benchmarks rising, ticker falling
    r = TickerRegimeDetector().detect("X", daily(-0.004, seed=3), BENCH, at(-1))
    assert r.trend.endswith("DOWNTREND")


def test_volatility_is_judged_against_the_tickers_own_history():
    # Similar ABSOLUTE ATR% today, very different meaning: for a stock that is
    # always this wild it is ordinary; for a calm stock that just turned wild
    # it is extreme.
    t_ = np.arange(len(DAYS))
    cycling = 5.0 + 2.0 * np.sin(2 * np.pi * (t_ - t_[-1]) / 60)   # 3%..7% ranges, ending mid-cycle at 5%
    always_wild = TickerRegimeDetector().detect("WILD", daily(0.001, spread=cycling, seed=4), BENCH, at(-1))
    turned_wild = TickerRegimeDetector().detect("TURN", daily(0.001, spread=1.0, vol_from=len(DAYS) - 40, seed=4), BENCH, at(-1))
    a, t = always_wild.features["volatility"], turned_wild.features["volatility"]
    assert abs(a["atr_pct"] - t["atr_pct"]) / t["atr_pct"] < 0.25          # similar absolute volatility
    assert t["atr_pct_pctile"] > 0.8 and a["atr_pct_pctile"] < t["atr_pct_pctile"] - 0.2
    assert turned_wild.volatility in ("HIGH", "EXTREME")


def intraday_frame(n_days=25, today_boost=1.0):
    """U-shaped intraday volume; today's morning volume multiplied by today_boost."""
    frames = []
    days = [d for d in DAYS[-n_days:]]
    for k, d in enumerate(days):
        idx = pd.date_range(f"{d.date()} 09:30", f"{d.date()} 16:00", freq="5min", inclusive="left")
        minutes = np.arange(len(idx))
        vol = 20000 + 30000 * ((minutes - 39) / 39) ** 2   # heavy at open/close
        if k == len(days) - 1:
            vol = vol * today_boost
        frames.append(pd.DataFrame({"date": idx, "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": vol}))
    return normalize_bars(pd.concat(frames), Timeframe.M5)[0]


def test_rvol_uses_time_of_day_normalisation():
    d = daily(0.001, seed=5)
    today_idx = len(DAYS) - 1
    ts = at(today_idx, "10:30")
    normal = TickerRegimeDetector().detect("T", d, BENCH, ts, intraday_frame(today_boost=1.0), Timeframe.M5)
    assert normal.features["volume"]["method"] == "TIME_OF_DAY"
    # same volume profile as usual at 10:30 -> RVOL ~1, even though the morning is the heaviest part of the day
    assert abs(normal.features["volume"]["rvol"] - 1.0) < 0.01 and normal.volume == "NORMAL_VOLUME"
    busy = TickerRegimeDetector().detect("T", d, BENCH, ts, intraday_frame(today_boost=4.0), Timeframe.M5)
    assert busy.volume == "EXTREME_VOLUME"


def test_gap_is_unknown_before_the_open_and_measured_after():
    d = daily(0.001, seed=6)
    before = TickerRegimeDetector().detect("T", d, BENCH, at(len(DAYS) - 1, "08:00"), intraday_frame(), Timeframe.M5)
    assert before.gap is None
    after = TickerRegimeDetector().detect("T", d, BENCH, at(len(DAYS) - 1, "10:00"), intraday_frame(), Timeframe.M5)
    assert after.gap is not None and after.features["gap"]["gap_pct"] is not None


def test_event_status_is_never_assumed():
    d = daily(0.001, seed=7)
    ts = at(len(DAYS) - 1, "09:00")
    today = ts.date()
    det = TickerRegimeDetector()
    assert det.detect("T", d, BENCH, ts).event_status == "UNKNOWN"
    assert det.detect("T", d, BENCH, ts, earnings={"expected_report_date": today}).event_status == "EARNINGS_TODAY"
    soon = today + dt.timedelta(days=2)
    assert det.detect("T", d, BENCH, ts, earnings={"expected_report_date": soon}).event_status == "EARNINGS_SOON"
    past = today - dt.timedelta(days=30)
    assert det.detect("T", d, BENCH, ts, earnings={"expected_report_date": past}).event_status == "UNKNOWN"


def test_future_bars_cannot_change_a_past_decision():
    d = daily(0.002, seed=8)
    ts = at(300, "10:00")
    det = TickerRegimeDetector()
    full = det.detect("T", d, BENCH, ts)
    trimmed = det.detect("T", d[d.index < d.index[300]], {k: v[v.index < v.index[300]] for k, v in BENCH.items()}, ts)
    assert full.to_dict() == trimmed.to_dict()
    assert full.as_of == str(d.index[299].tz_convert("America/New_York").date())


def test_insufficient_history():
    assert TickerRegimeDetector().detect("T", daily(0.001).iloc[:100], BENCH, at(99)).status == "DATA_INSUFFICIENT"
