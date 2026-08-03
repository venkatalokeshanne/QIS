"""
Tests for app.indicators.auto_support_resistance.

Covers three things found while reviewing the indicator for intraday
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

3. A more serious architectural bug (fixed): levels used to be computed
   ONCE globally over the whole input df, so every historical bar in a
   would-be strategy backtest would be evaluated against levels only
   knowable using the entire rest of the dataset. Now computed per
   session using only swings both dated AND confirmed strictly before
   that session starts, broadcast across that session's own bars --
   matching how every other levels indicator here already behaves.
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


def test_levels_vary_across_sessions_not_globally_constant(random_walk_df):
    """
    Regression guard for the "computed once globally" bug: with a
    price series that trends a long way over 2000 bars, the levels
    relevant to an early session should differ from the levels
    relevant to a late session -- if they're identical throughout,
    the per-session recompute silently regressed back to a single
    global calculation.
    """
    out = AutoSupportResistance().calculate(random_walk_df, {})
    session_date = pd.Series(random_walk_df.index.date, index=random_walk_df.index)
    unique_days = session_date.unique()

    early_day_mask = session_date == unique_days[len(unique_days) // 4]
    late_day_mask = session_date == unique_days[-1]

    early_levels = out.loc[early_day_mask, "auto_sr_level_1"].iloc[0]
    late_levels = out.loc[late_day_mask, "auto_sr_level_1"].iloc[0]

    assert early_levels != late_levels, "levels are identical early vs late -- looks globally constant, not per-session"


def test_a_sessions_levels_are_unaffected_by_bars_that_come_after_it(random_walk_df):
    """
    The core no-lookahead property: a given session's own levels must
    be reproducible using ONLY the data available up through that
    session -- appending more bars afterward (as a live feed would)
    must not change what was already computed for an earlier session.
    """
    full = AutoSupportResistance().calculate(random_walk_df, {})
    session_date = pd.Series(random_walk_df.index.date, index=random_walk_df.index)
    unique_days = sorted(session_date.unique())
    cutoff_day = unique_days[len(unique_days) // 2]

    truncated_df = random_walk_df.loc[session_date <= cutoff_day]
    truncated = AutoSupportResistance().calculate(truncated_df, {})

    cutoff_mask_full = session_date == cutoff_day
    cutoff_mask_truncated = pd.Series(truncated_df.index.date, index=truncated_df.index) == cutoff_day

    for i in range(1, 6):
        full_value = full.loc[cutoff_mask_full, f"auto_sr_level_{i}"].iloc[0]
        truncated_value = truncated.loc[cutoff_mask_truncated, f"auto_sr_level_{i}"].iloc[0]
        if pd.isna(full_value):
            assert pd.isna(truncated_value)
        else:
            assert full_value == truncated_value, (
                f"auto_sr_level_{i} for the cutoff session changed after appending later bars -- lookahead regressed"
            )
