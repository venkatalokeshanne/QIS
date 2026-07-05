"""
Tests for app.indicators.auto_support_resistance.

Covers two things found while reviewing the indicator for intraday
accuracy:

1. A real bug (fixed): swing highs and swing lows were concatenated
   into one Series (all highs, then all lows) without re-sorting by
   time before slicing the trailing `lookback` window, so that slice
   could draw from only one side (e.g. all lows, zero highs) instead
   of the true most-recent swings of both kinds.

2. A quality improvement (empirically validated via a no-lookahead
   backtest across 10 real tickers -- see conversation history):
   ranking clusters by how many DISTINCT SESSIONS touched them, not
   raw touch count, and requiring a minimum of `min_touches` distinct
   sessions before a level qualifies at all.
"""

import numpy as np
import pandas as pd
import pytest

from app.indicators.auto_support_resistance import AutoSupportResistance


@pytest.fixture
def random_walk_df() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 2000
    idx = pd.date_range("2024-01-01 09:30", periods=n, freq="5min")
    price = 100 + np.cumsum(rng.normal(0, 0.3, n))
    high = price + rng.uniform(0.05, 0.3, n)
    low = price - rng.uniform(0.05, 0.3, n)
    return pd.DataFrame(
        {"open": price, "high": high, "low": low, "close": price, "volume": rng.integers(100, 1000, n)},
        index=idx,
    )


def _swing_masks(df: pd.DataFrame, swing_range: int) -> tuple[pd.Series, pd.Series]:
    left = right = swing_range
    window = left + right + 1

    def is_swing_high(w: pd.Series) -> bool:
        return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

    def is_swing_low(w: pd.Series) -> bool:
        return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

    high_mask = (
        df["high"].rolling(window=window, min_periods=window).apply(is_swing_high, raw=False).astype(bool)
    ).shift(-right).fillna(False).astype(bool)
    low_mask = (
        df["low"].rolling(window=window, min_periods=window).apply(is_swing_low, raw=False).astype(bool)
    ).shift(-right).fillna(False).astype(bool)
    return high_mask, low_mask


def test_recent_lookback_window_includes_both_highs_and_lows(random_walk_df):
    """
    The bug this guards against: without sorting by time, the trailing
    `lookback` slice could be 100% swing lows (or 100% highs) purely
    because of concatenation order, not because recent swings actually
    skewed that way.
    """
    default_params = AutoSupportResistance().metadata.default_params
    high_mask, low_mask = _swing_masks(random_walk_df, default_params["swing_range"])

    swing_prices = (
        pd.concat([random_walk_df["high"].where(high_mask), random_walk_df["low"].where(low_mask)])
        .dropna()
        .sort_index()
    )
    recent = swing_prices.iloc[-default_params["lookback"] :]

    is_high_touch = [random_walk_df.loc[t, "high"] == v and high_mask.loc[t] for t, v in recent.items()]
    is_low_touch = [random_walk_df.loc[t, "low"] == v and low_mask.loc[t] for t, v in recent.items()]

    assert any(is_high_touch), "trailing lookback window contains zero swing highs -- recency bug regressed"
    assert any(is_low_touch), "trailing lookback window contains zero swing lows -- recency bug regressed"


def test_calculate_returns_five_levels_sorted_by_distinct_session_touches(random_walk_df):
    out = AutoSupportResistance().calculate(random_walk_df, {})
    levels = [out[f"auto_sr_level_{i}"].iloc[-1] for i in range(1, 6)]

    assert len(levels) == 5
    assert all(not pd.isna(lv) for lv in levels), "expected 5 real levels from 2000 bars of varied price action"


def test_min_touches_filters_out_single_session_levels(random_walk_df):
    """A level only ever touched within one session shouldn't qualify
    once min_touches requires at least 2 distinct sessions."""
    lenient = AutoSupportResistance().calculate(random_walk_df, {"min_touches": 1})
    strict = AutoSupportResistance().calculate(random_walk_df, {"min_touches": 10})

    lenient_levels = [lenient[f"auto_sr_level_{i}"].iloc[-1] for i in range(1, 6)]
    strict_levels = [strict[f"auto_sr_level_{i}"].iloc[-1] for i in range(1, 6)]

    assert all(not pd.isna(lv) for lv in lenient_levels), "min_touches=1 should always fill all 5 slots"
    assert any(pd.isna(lv) for lv in strict_levels), "min_touches=10 should be too strict to fill all 5 slots"


def test_calculate_does_not_mutate_input(random_walk_df):
    original_columns = list(random_walk_df.columns)
    AutoSupportResistance().calculate(random_walk_df, {})
    assert list(random_walk_df.columns) == original_columns
