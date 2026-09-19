"""Step 4A: premarket regime (spec 19A-19J, 48)."""

import datetime as dt

import numpy as np
import pandas as pd

from app.strategy_engine.data.normalize import normalize_bars
from app.strategy_engine.models import Timeframe
from app.strategy_engine.premarket_regime import PremarketRegimeDetector

DAYS = [d.date() for d in pd.bdate_range("2026-02-02", "2026-03-10")
        if d.date() not in (dt.date(2026, 2, 16),)]          # Presidents' Day
TODAY = DAYS[-1]


def day_bars(day, pm_close=100.0, pm_volume=2000.0, pm_every=1, rth_close=100.0, pm_path=None):
    """One session: premarket 04:00-09:30 (optionally sparse), RTH 09:30-16:00."""
    pm_idx = pd.date_range(f"{day} 04:00", f"{day} 09:30", freq="5min", inclusive="left")[::pm_every]
    n = len(pm_idx)
    path = pm_path if pm_path is not None else np.full(n, pm_close)
    pm = pd.DataFrame({"date": pm_idx, "open": path, "high": path * 1.001, "low": path * 0.999, "close": path, "volume": pm_volume})
    rth_idx = pd.date_range(f"{day} 09:30", f"{day} 16:00", freq="5min", inclusive="left")
    rth = pd.DataFrame({"date": rth_idx, "open": rth_close, "high": rth_close + 0.2, "low": rth_close - 0.2,
                        "close": rth_close, "volume": 50000.0})
    return pd.concat([pm, rth])


def history(today_df=None, pm_volume=2000.0, pm_move=0.002):
    frames = [day_bars(d, pm_close=100 * (1 + (pm_move if k % 2 else -pm_move)), pm_volume=pm_volume)
              for k, d in enumerate(DAYS[:-1])]
    if today_df is not None:
        frames.append(today_df)
    return normalize_bars(pd.concat(frames), Timeframe.M5)[0]


def detect(bars, hhmm, **kw):
    ts = pd.Timestamp(f"{TODAY} {hhmm}", tz="America/New_York")
    return PremarketRegimeDetector().detect("T", bars, Timeframe.M5, ts, previous_close=100.0, **kw)


def rising(n, start, end):
    return np.linspace(start, end, n)


def test_strong_gap_up_on_heavy_volume():
    n = 66
    today = day_bars(TODAY, pm_volume=20000.0, pm_path=rising(n, 104, 108))
    r = detect(history(today), "09:25")
    assert r.status == "AVAILABLE", r.reasons
    assert r.direction == "STRONG_GAP_UP" and r.structure == "HOLDING_HIGHS"
    assert r.volume == "EXTREME_PREMARKET_VOLUME"
    assert r.premarket_regime == "STRONG_GAP_UP_HIGH_PARTICIPATION"


def test_gap_up_that_fades():
    n = 66
    today = day_bars(TODAY, pm_volume=2000.0, pm_path=rising(n, 106, 102))
    r = detect(history(today), "09:25")
    assert r.direction.endswith("GAP_UP") and r.structure == "FADING"
    assert r.premarket_regime.endswith("LOW_PARTICIPATION")


def test_thin_premarket_is_unreliable():
    today = day_bars(TODAY, pm_volume=50.0, pm_every=12, pm_close=106)
    r = detect(history(today, pm_volume=50.0), "09:25")
    assert r.status == "PREMARKET_UNRELIABLE" and r.reliability == "LOW"
    assert r.premarket_regime == "PREMARKET_UNRELIABLE"


def test_no_extended_hours_data_is_unavailable_not_faked():
    rth_only = history(day_bars(TODAY, pm_path=rising(66, 104, 108)))
    rth_only = rth_only[rth_only["session"] == "RTH"]
    r = detect(rth_only, "09:25")
    assert r.status == "PREMARKET_DATA_UNAVAILABLE" and r.premarket_regime == "PREMARKET_DATA_UNAVAILABLE"


def test_premarket_volume_is_compared_at_the_same_time_of_day():
    # Every day trades 2000/bar. At 07:00 today's cumulative volume equals the
    # usual 07:00 cumulative volume -> RVOL 1, even though it is only a third
    # of a full premarket's volume.
    r = detect(history(day_bars(TODAY, pm_close=100.3)), "07:00")
    assert abs(r.premarket_rvol - 1.0) < 1e-6


def test_only_premarket_bars_before_the_decision_are_used():
    path = np.concatenate([np.full(30, 100.2), np.full(36, 110.0)])   # jump at 06:30
    bars = history(day_bars(TODAY, pm_path=path, pm_volume=20000.0))
    early = detect(bars, "06:30")
    late = detect(bars, "09:25")
    assert early.features["premarket_high"] < 101 and early.direction == "FLAT"
    assert late.features["premarket_high"] > 109
    assert pd.Timestamp(early.premarket_data_through).strftime("%H:%M") == "06:30"


def test_after_the_open_premarket_is_frozen_at_0930():
    bars = history(day_bars(TODAY, pm_path=rising(66, 104, 108), rth_close=120.0))
    at_925 = detect(bars, "09:30")
    at_noon = detect(bars, "12:00")
    assert at_noon.to_dict()["features"] == at_925.to_dict()["features"]
    assert at_noon.direction == at_925.direction


def test_catalyst_unknown_is_not_no_catalyst():
    r = detect(history(day_bars(TODAY, pm_path=rising(66, 104, 108))), "09:25")
    assert r.catalyst == "UNKNOWN"
    r2 = detect(history(day_bars(TODAY, pm_path=rising(66, 104, 108))), "09:25",
                earnings={"expected_report_date": TODAY, "time_of_day": "BMO"})
    assert r2.catalyst == "EARNINGS_BEFORE_OPEN"


def test_market_premarket_needs_both_spy_and_qqq():
    t = history(day_bars(TODAY, pm_path=rising(66, 104, 108)))
    spy = history(day_bars(TODAY, pm_close=101.0))
    qqq = history(day_bars(TODAY, pm_close=101.2))
    r = detect(t, "09:25", market={"SPY": spy, "QQQ": qqq}, market_previous_close={"SPY": 100.0, "QQQ": 100.0})
    assert r.market_premarket == "GAP_UP_CONFIRMED"
    r2 = detect(t, "09:25", market={"SPY": spy}, market_previous_close={"SPY": 100.0})
    assert r2.market_premarket == "UNAVAILABLE"


def test_extended_hours_coverage_starting_later_does_not_leak_back():
    # premarket bars exist only from TODAY on; a decision on an earlier day must
    # see "no extended-hours data", exactly as it would have at the time
    rth_only = [day_bars(d)[lambda f: f["date"].dt.strftime("%H:%M") >= "09:30"] for d in DAYS[:-1]]
    bars = normalize_bars(pd.concat(rth_only + [day_bars(TODAY)]), Timeframe.M5)[0]
    earlier = pd.Timestamp(f"{DAYS[-3]} 09:25", tz="America/New_York")
    r = PremarketRegimeDetector().detect("T", bars, Timeframe.M5, earlier, previous_close=100.0)
    assert r.status == "PREMARKET_DATA_UNAVAILABLE", r.reasons
