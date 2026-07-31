"""Tests for app.indicators.confluence_order_block.

Focused on the algorithm spec's explicitly flagged highest-risk items:
the causal "break on first bar the score is met" in zone detection, the
volume-pivot / structure-state off-by-ones, and the zone lifecycle's
age -> mitigation -> touch ordering (with activation strictly after
evaluation, so a zone can never be entered on its own confirmation bar).
"""

import numpy as np
import pandas as pd
import pytest

from app.indicators.confluence_order_block import (
    ConfluenceOrderBlock,
    _Zone,
    _compute_os_state,
    _compute_vol_pivot,
    _detect_zones,
    _run_lifecycle,
)


# --- _compute_os_state -------------------------------------------------


def test_os_state_window_and_tested_bar_offsets():
    # os_len=2: the window at bar i is high/low[i-1..i]; the bar TESTED
    # against that window is i-2, one bar older than the window itself.
    high = np.array([1.0, 2.0, 3.0, 10.0, 3.0, 2.0, 1.0, 1.0])
    low = np.array([1.0, 2.0, 3.0, 3.0, 3.0, 2.0, 1.0, -10.0])

    os = _compute_os_state(high, low, os_len=2)

    assert list(os) == [0, 0, 1, 1, 1, 0, 0, 0]


# --- _compute_vol_pivot -------------------------------------------------


def test_vol_pivot_flags_lagged_local_max_not_the_candle_itself():
    # A volume spike at index 4 is only knowable at index 4 + vol_len.
    volume = np.array([5, 5, 5, 5, 100, 5, 5, 5, 5, 5], dtype=float)

    vol_pivot = _compute_vol_pivot(volume, vol_len=2)

    assert not vol_pivot[4], "the spike's own bar must not be flagged -- that would be lookahead"
    assert vol_pivot[6], "spike at index 4 should be flagged at 4 + vol_len = 6"
    assert vol_pivot.sum() == 1


# --- _detect_zones --------------------------------------------------------


def test_zone_confirms_on_first_bar_score_is_met_not_later():
    """
    Regression guard for spec pitfall #1: the confirmation must break on
    the FIRST bar the threshold is genuinely met. Engineered so the score
    is 1 at k=4, hits 3 (the threshold) at k=5, and would go higher still
    at k=6 if the loop kept scanning -- confirm_index must land on 5.
    """
    n = 8
    open_ = np.array([0, 0, 0, 10, 0, 0, 0, 0], dtype=float)
    close = np.array([0, 0, 0, 9, 0, 0, 0, 0], dtype=float)
    high = np.array([0, 0, 0, 10.5, 10.6, 12.0, 0, 0], dtype=float)
    low = np.array([0, 0, 0, 9.0, 0, 0, 0, 0], dtype=float)
    atr = np.array([np.nan, np.nan, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan])
    os = np.array([0, 0, 0, 0, 0, 1, 1, 0])
    vol_pivot = np.zeros(n, dtype=bool)
    vol_pivot[4] = True  # vol_bar for the i=3 candidate (vol_len=1) is 3+1=4

    zones = _detect_zones(
        open_, high, low, close, atr, os, vol_pivot,
        impulse_bars=3, disp_atr=1.0, disp_pct=1000.0, vol_len=1, min_score=3, zone_width="half",
    )

    assert len(zones) == 1
    z = zones[0]
    assert z.direction == 1
    assert z.ob_index == 3
    assert z.confirm_index == 5, "must confirm at the first bar score>=min_score (5), not 4 or 6"
    assert z.atr_at_formation == 1.0
    assert z.bottom == 9.0
    assert z.top == pytest.approx((10.5 + 9.0) / 2)  # zone_width="half" -> midpoint


def test_zone_width_full_uses_candle_high_low_not_midpoint():
    n = 8
    open_ = np.array([0, 0, 0, 10, 0, 0, 0, 0], dtype=float)
    close = np.array([0, 0, 0, 9, 0, 0, 0, 0], dtype=float)
    high = np.array([0, 0, 0, 10.5, 10.6, 12.0, 0, 0], dtype=float)
    low = np.array([0, 0, 0, 9.0, 0, 0, 0, 0], dtype=float)
    atr = np.array([np.nan, np.nan, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan])
    os = np.array([0, 0, 0, 0, 0, 1, 1, 0])
    vol_pivot = np.zeros(n, dtype=bool)
    vol_pivot[4] = True

    zones = _detect_zones(
        open_, high, low, close, atr, os, vol_pivot,
        impulse_bars=3, disp_atr=1.0, disp_pct=1000.0, vol_len=1, min_score=3, zone_width="full",
    )

    assert zones[0].top == 10.5
    assert zones[0].bottom == 9.0


def test_no_zone_when_score_never_reaches_threshold():
    n = 8
    open_ = np.array([0, 0, 0, 10, 0, 0, 0, 0], dtype=float)
    close = np.array([0, 0, 0, 9, 0, 0, 0, 0], dtype=float)
    high = np.array([0, 0, 0, 10.5, 10.6, 10.7, 0, 0], dtype=float)  # too small to displace
    low = np.array([0, 0, 0, 9.0, 0, 0, 0, 0], dtype=float)
    atr = np.array([np.nan, np.nan, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan])
    os = np.array([0, 0, 0, 0, 0, 0, 0, 0])  # never matches direction +1
    vol_pivot = np.zeros(n, dtype=bool)  # no volume pivot either

    zones = _detect_zones(
        open_, high, low, close, atr, os, vol_pivot,
        impulse_bars=3, disp_atr=2.0, disp_pct=1000.0, vol_len=1, min_score=3, zone_width="half",
    )

    assert zones == []


# --- _run_lifecycle ---------------------------------------------------


def test_zone_cannot_be_entered_on_its_own_confirmation_bar():
    zone = _Zone(direction=1, ob_index=0, confirm_index=1, top=10.0, bottom=9.0, atr_at_formation=1.0)
    close = np.array([0.0, 100.0, 9.5, 0.0, 0.0])
    low = np.array([0.0, 5.0, 9.5, 0.0, 0.0])  # bar 1 would touch (low<=top) if it were already active
    high = np.zeros(5)

    signal, top, bottom, atr = _run_lifecycle(5, close, low, high, [zone], mitigation="close", max_age=10)

    assert signal[1] is None, "activation happens AFTER evaluation on the confirm bar -- it must not fire yet"
    assert signal[2] == "long"
    assert top[2] == 10.0
    assert bottom[2] == 9.0
    assert atr[2] == 1.0
    assert signal[0] is None and signal[3] is None and signal[4] is None


def test_zone_expires_before_a_later_touch_can_fire():
    zone = _Zone(direction=1, ob_index=0, confirm_index=0, top=10.0, bottom=9.0, atr_at_formation=1.0)
    close = np.array([0.0, 50.0, 50.0])
    low = np.array([0.0, 50.0, 5.0])  # bar 2's low would touch, but the zone is already expired by then

    signal, *_ = _run_lifecycle(3, close, low, np.zeros(3), [zone], mitigation="close", max_age=1)

    assert list(signal) == [None, None, None]


def test_mitigation_drops_zone_before_touch_is_checked():
    zone = _Zone(direction=1, ob_index=0, confirm_index=0, top=10.0, bottom=9.0, atr_at_formation=1.0)
    close = np.array([0.0, 8.0, 8.0])  # close < bottom -> mitigated on bar 1
    low = np.array([0.0, 9.5, 9.5])  # would also touch, if evaluated

    signal, *_ = _run_lifecycle(3, close, low, np.zeros(3), [zone], mitigation="close", max_age=10)

    assert list(signal) == [None, None, None]


def test_first_touch_wins_when_two_zones_touch_the_same_bar():
    zone_a = _Zone(direction=1, ob_index=0, confirm_index=0, top=10.0, bottom=9.0, atr_at_formation=1.0)
    zone_b = _Zone(direction=1, ob_index=0, confirm_index=0, top=20.0, bottom=19.0, atr_at_formation=2.0)
    close = np.array([0.0, 100.0])
    low = np.array([0.0, 9.5])  # touches both zones' proximal edges

    signal, top, bottom, atr = _run_lifecycle(
        2, close, low, np.zeros(2), [zone_a, zone_b], mitigation="close", max_age=10
    )

    assert signal[1] == "long"
    assert top[1] == 10.0 and bottom[1] == 9.0, "the first (oldest-listed) zone should win the tie"


# --- ConfluenceOrderBlock indicator (end-to-end) -----------------------


@pytest.fixture
def random_walk_df() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 400
    idx = pd.date_range("2024-01-01 09:30", periods=n, freq="30min")
    price = 100 + np.cumsum(rng.normal(0, 0.5, n))
    high = price + rng.uniform(0.1, 0.6, n)
    low = price - rng.uniform(0.1, 0.6, n)
    open_ = price + rng.normal(0, 0.2, n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": price, "volume": rng.integers(100, 5000, n)},
        index=idx,
    )


def test_calculate_attaches_expected_columns(random_walk_df):
    out = ConfluenceOrderBlock().calculate(random_walk_df, {})
    for col in ("cob_signal", "cob_zone_top", "cob_zone_bottom", "cob_atr_at_formation"):
        assert col in out.columns


def test_calculate_does_not_mutate_input(random_walk_df):
    original_columns = list(random_walk_df.columns)
    ConfluenceOrderBlock().calculate(random_walk_df, {})
    assert list(random_walk_df.columns) == original_columns


def test_no_lookahead_regression(random_walk_df):
    """
    Appending more bars to the end of the series must not change signals
    already produced for earlier bars -- excluding a margin near the
    truncation cutoff, where a truncated run legitimately has less future
    data available to confirm/consume zones than the full run does.
    """
    full = ConfluenceOrderBlock().calculate(random_walk_df, {})
    cutoff = 250
    margin = 120  # > max(impulse_bars, vol_len) + max_age default headroom
    truncated_df = random_walk_df.iloc[: cutoff + 1]
    truncated = ConfluenceOrderBlock().calculate(truncated_df, {})

    stable_upto = cutoff - margin
    for col in ("cob_signal", "cob_zone_top", "cob_zone_bottom", "cob_atr_at_formation"):
        full_vals = full[col].iloc[:stable_upto].tolist()
        truncated_vals = truncated[col].iloc[:stable_upto].tolist()
        for a, b in zip(full_vals, truncated_vals):
            if isinstance(a, float) and np.isnan(a):
                assert isinstance(b, float) and np.isnan(b)
            else:
                assert a == b, f"{col} changed after appending later bars -- lookahead regressed"
