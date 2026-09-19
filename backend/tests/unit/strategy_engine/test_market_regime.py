"""Step 3: market regime detector (spec 5-12, 48)."""

import numpy as np
import pandas as pd
import pytest

from app.strategy_engine.data.normalize import normalize_bars
from app.strategy_engine.indicators import persist
from app.strategy_engine.market_regime import MarketRegimeDetector
from app.strategy_engine.models import Timeframe

DAYS = pd.bdate_range("2024-01-02", periods=420)


def make_daily(drift: float, wave: float = 3.0, noise: float = 0.4, seed: int = 1, vol_boost_from: int | None = None):
    rng = np.random.default_rng(seed)
    t = np.arange(len(DAYS))
    close = 100 + drift * t + wave * np.sin(t / 6.0) + rng.normal(0, noise, len(t)).cumsum() * 0.1
    rng_hl = np.full(len(t), 1.0)
    if vol_boost_from is not None:
        rng_hl[vol_boost_from:] = 6.0
        close[vol_boost_from:] += rng.normal(0, 4.0, len(t) - vol_boost_from)
    close = np.maximum(close, 5)
    raw = pd.DataFrame({"date": DAYS, "open": close, "high": close + rng_hl, "low": close - rng_hl, "close": close,
                        "volume": 1e6})
    return normalize_bars(raw, Timeframe.D1)[0]


def market(drift_spy, drift_qqq=None, drift_iwm=None, **kw):
    return {"SPY": make_daily(drift_spy, seed=1, **kw), "QQQ": make_daily(drift_qqq if drift_qqq is not None else drift_spy, seed=2, **kw),
            "IWM": make_daily(drift_iwm if drift_iwm is not None else drift_spy, seed=3, **kw)}


def decide(daily, day=-1, **kw):
    ts = daily["SPY"].index[day].tz_convert("America/New_York").normalize() + pd.Timedelta(hours=17)
    return MarketRegimeDetector(**kw).detect(daily, ts)


def test_bullish_input_is_bullish():
    r = decide(market(0.25))
    assert r.status == "OK" and r.direction == "BULLISH", r.reasons
    assert r.market_regime.startswith("BULLISH_")
    assert 0 <= r.confidence <= 100


def test_bearish_input_is_bearish():
    r = decide(market(-0.25))
    assert r.direction == "BEARISH", r.reasons


def test_mixed_input_is_neutral():
    r = decide(market(0.25, -0.25))        # SPY up, QQQ down
    assert r.direction == "NEUTRAL"


def test_range_bound_market_is_neutral():
    # oscillates around 100 with equal swing highs/lows: no higher highs, no lower lows
    r = decide(market(0.0, wave=4.0, noise=0.0))
    assert r.direction == "NEUTRAL", r.reasons


def test_volatility_is_relative_to_own_history():
    calm = decide(market(0.25))
    stormy = decide(market(0.25, vol_boost_from=400))
    order = ["LOW", "NORMAL", "HIGH", "EXTREME"]
    assert order.index(stormy.volatility) > order.index(calm.volatility)
    assert stormy.volatility in ("HIGH", "EXTREME")


def test_persistence_requires_consecutive_confirmation():
    raw = pd.Series(["BULLISH"] * 5 + ["BEARISH"] + ["BULLISH"] * 2 + ["BEARISH"] * 3)
    out = persist(raw, 3)
    assert list(out) == ["BULLISH"] * 10 + ["BEARISH"]


def test_breadth_unavailable_is_reported_not_faked():
    r = decide(market(0.25))
    assert r.breadth == "UNAVAILABLE"


def test_insufficient_history_is_not_classified():
    short = {k: v.iloc[:100] for k, v in market(0.25).items()}
    assert decide(short).status == "DATA_INSUFFICIENT"


def test_future_bars_cannot_change_a_past_decision():
    full = market(0.25)
    decision = full["SPY"].index[300].tz_convert("America/New_York").normalize() + pd.Timedelta(hours=10)
    det = MarketRegimeDetector()
    with_future = det.detect(full, decision)
    past_only = det.detect({k: v[v.index <= full["SPY"].index[299]] for k, v in full.items()}, decision)
    assert with_future.to_dict() == past_only.to_dict()
    # 10:00 on day 300 must use day 299's close, not day 300's
    assert with_future.as_of == str(full["SPY"].index[299].tz_convert("America/New_York").date())


def test_history_matches_point_in_time_decisions():
    daily = market(0.25)
    hist = MarketRegimeDetector().classify_history(daily)
    for i in (280, 350, 419):
        r = decide(daily, i)
        assert hist.iloc[i]["market_direction"] == r.direction
        assert hist.iloc[i]["market_volatility"] == r.volatility
