"""
Correctness/behavioral tests for the Twelve-Data-catalog indicator
expansion (overlap studies, momentum, volume, volatility, price
transform, cycle, and statistics families).

Uses a longer single-session fixture than conftest's `ohlcv_df` since
several of these (bbands, ultosc, ichimoku, coppock, kst, the Hilbert
Transform family) need more warmup bars than a 31-minute session
provides.
"""

import numpy as np
import pandas as pd
import pytest

from app.indicators.registry import discover_indicators, get_indicator, list_indicators


@pytest.fixture
def long_ohlcv_df() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.date_range("2024-01-02 09:30", periods=300, freq="1min")
    close = 100 + np.cumsum(rng.normal(0, 0.1, 300))
    high = close + rng.uniform(0, 0.2, 300)
    low = close - rng.uniform(0, 0.2, 300)
    open_ = close + rng.normal(0, 0.05, 300)
    volume = rng.integers(100, 1000, 300)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=idx)


def test_every_registered_indicator_runs_without_mutating_input(long_ohlcv_df):
    discover_indicators()
    for meta in list_indicators():
        original_cols = list(long_ohlcv_df.columns)
        result = get_indicator(meta["name"]).calculate(long_ohlcv_df, {})
        assert list(long_ohlcv_df.columns) == original_cols, f"{meta['name']} mutated its input"
        new_cols = [c for c in result.columns if c not in original_cols]
        assert new_cols, f"{meta['name']} added no columns"


# --- Bounded oscillators (0-100 or -100-0 or -100-100) ---


@pytest.mark.parametrize(
    "name,col,lo,hi",
    [
        ("adx", "adx_14", 0, 100),
        ("cci", None, None, None),  # unbounded, checked separately below
        ("cmo", "cmo_14", -100, 100),
        ("mfi", "mfi_14", 0, 100),
        ("willr", "willr_14", -100, 0),
        ("aroon", "aroon_up_14", 0, 100),
        ("stoch", "stoch_k_14_3_3", 0, 100),
        ("stochrsi", "stochrsi_k_14_14", 0, 100),
        ("ultosc", "ultosc_7_14_28", 0, 100),
        ("percent_b", None, None, None),  # can exceed 0-1 during breakouts, no hard bound
    ],
)
def test_bounded_indicators_stay_within_range(long_ohlcv_df, name, col, lo, hi):
    if col is None:
        pytest.skip(f"{name} has no hard bound")
    result = get_indicator(name).calculate(long_ohlcv_df, {})
    valid = result[col].dropna()
    assert valid.between(lo, hi).all()


def test_rsi_is_bounded_0_to_100(long_ohlcv_df):
    result = get_indicator("rsi").calculate(long_ohlcv_df, {"period": 14})
    valid = result["rsi_14"].dropna()
    assert valid.between(0, 100).all()


# --- Non-negativity of volatility/range measures ---


@pytest.mark.parametrize("name,col", [("natr", "natr_14"), ("trange", "trange")])
def test_volatility_measures_are_non_negative(long_ohlcv_df, name, col):
    result = get_indicator(name).calculate(long_ohlcv_df, {})
    valid = result[col].dropna()
    assert (valid >= 0).all()


# --- Cross-checkable formulas ---


def test_dema_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("dema").calculate(long_ohlcv_df, {"period": 10})
    ema1 = long_ohlcv_df["close"].ewm(span=10, adjust=False).mean()
    ema2 = ema1.ewm(span=10, adjust=False).mean()
    expected = 2 * ema1 - ema2
    pd.testing.assert_series_equal(result["dema_10"], expected, check_names=False)


def test_tema_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("tema").calculate(long_ohlcv_df, {"period": 10})
    ema1 = long_ohlcv_df["close"].ewm(span=10, adjust=False).mean()
    ema2 = ema1.ewm(span=10, adjust=False).mean()
    ema3 = ema2.ewm(span=10, adjust=False).mean()
    expected = 3 * ema1 - 3 * ema2 + ema3
    pd.testing.assert_series_equal(result["tema_10"], expected, check_names=False)


def test_bbands_upper_gte_middle_gte_lower(long_ohlcv_df):
    result = get_indicator("bbands").calculate(long_ohlcv_df, {"period": 20, "std_dev": 2.0})
    valid = result.dropna(subset=["bbands_upper_20", "bbands_middle_20", "bbands_lower_20"])
    assert (valid["bbands_upper_20"] >= valid["bbands_middle_20"]).all()
    assert (valid["bbands_middle_20"] >= valid["bbands_lower_20"]).all()


def test_willr_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("willr").calculate(long_ohlcv_df, {"period": 14})
    hh = long_ohlcv_df["high"].rolling(14, min_periods=14).max()
    ll = long_ohlcv_df["low"].rolling(14, min_periods=14).min()
    expected = -100 * (hh - long_ohlcv_df["close"]) / (hh - ll)
    pd.testing.assert_series_equal(result["willr_14"], expected, check_names=False)


def test_obv_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("obv").calculate(long_ohlcv_df, {})
    direction = np.sign(long_ohlcv_df["close"].diff().fillna(0))
    expected = (direction * long_ohlcv_df["volume"]).cumsum()
    pd.testing.assert_series_equal(result["obv"], expected, check_names=False)


def test_roc_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("roc").calculate(long_ohlcv_df, {"period": 10})
    src = long_ohlcv_df["close"]
    expected = 100 * (src - src.shift(10)) / src.shift(10)
    pd.testing.assert_series_equal(result["roc_10"], expected, check_names=False)


def test_stoch_k_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("stoch").calculate(long_ohlcv_df, {"k_period": 14, "k_slowing": 1, "d_period": 3})
    hh = long_ohlcv_df["high"].rolling(14, min_periods=14).max()
    ll = long_ohlcv_df["low"].rolling(14, min_periods=14).min()
    fast_k = 100 * (long_ohlcv_df["close"] - ll) / (hh - ll)
    pd.testing.assert_series_equal(result["stoch_k_14_1_3"], fast_k, check_names=False)


def test_supertrend_direction_is_plus_or_minus_one(long_ohlcv_df):
    result = get_indicator("supertrend").calculate(long_ohlcv_df, {"period": 10, "multiple": 3.0})
    assert set(result["supertrend_direction_10_3.0"].unique()).issubset({1, -1})


def test_supertrend_recovers_from_nan_atr_warmup_without_freezing():
    # Regression test: the band-ratchet comparison against a still-NaN
    # previous band value must not permanently freeze the band at NaN
    # once ATR warms up -- it did, until fixed, because any comparison
    # against NaN is False, so the ratchet always kept the frozen value.
    rng = np.random.default_rng(1)
    idx = pd.date_range("2024-01-02 09:30", periods=500, freq="1min")
    close = 100 + np.cumsum(rng.normal(0, 0.3, 500)) + np.sin(np.arange(500) / 40) * 5
    df = pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.1, 500),
            "high": close + rng.uniform(0, 0.3, 500),
            "low": close - rng.uniform(0, 0.3, 500),
            "close": close,
            "volume": rng.integers(100, 1000, 500),
        },
        index=idx,
    )
    result = get_indicator("supertrend").calculate(df, {"period": 10, "multiple": 3.0})
    line = result["supertrend_10_3.0"]
    direction = result["supertrend_direction_10_3.0"]

    assert line.iloc[20:].isna().sum() == 0, "supertrend line stayed NaN past warmup"
    assert direction.nunique() > 1, "supertrend direction never flipped on trending/reversing data"


def test_pivot_points_hl_high_gte_low_when_both_present(long_ohlcv_df):
    result = get_indicator("pivot_points_hl").calculate(long_ohlcv_df, {"left_range": 5, "right_range": 5})
    both = result.dropna(subset=["pivot_points_hl_high", "pivot_points_hl_low"])
    assert (both["pivot_points_hl_high"] >= both["pivot_points_hl_low"]).all()


def test_sar_stays_within_reasonable_bounds(long_ohlcv_df):
    result = get_indicator("sar").calculate(long_ohlcv_df, {})
    valid = result["sar"].dropna()
    price_min, price_max = long_ohlcv_df["low"].min(), long_ohlcv_df["high"].max()
    margin = (price_max - price_min) * 2
    assert valid.between(price_min - margin, price_max + margin).all()


def test_linearregslope_matches_manual_formula(long_ohlcv_df):
    result = get_indicator("linearregslope").calculate(long_ohlcv_df, {"period": 14})
    x = np.arange(14)

    def slope(window):
        return np.polyfit(x, window, 1)[0]

    expected = long_ohlcv_df["close"].rolling(14, min_periods=14).apply(slope, raw=True)
    pd.testing.assert_series_equal(result["linearregslope_14"], expected, check_names=False)


def test_typprice_and_hlc3_are_identical(long_ohlcv_df):
    typprice = get_indicator("typprice").calculate(long_ohlcv_df, {})["typprice"]
    hlc3 = get_indicator("hlc3").calculate(long_ohlcv_df, {})["hlc3"]
    pd.testing.assert_series_equal(typprice, hlc3, check_names=False)
