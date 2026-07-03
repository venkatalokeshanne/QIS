"""Numerical/behavioral correctness tests for each indicator."""

import numpy as np
import pandas as pd

from app.indicators.atr import ATR
from app.indicators.ema import EMA
from app.indicators.macd import MACD
from app.indicators.opening_range import OpeningRange
from app.indicators.rsi import RSI
from app.indicators.sma import SMA
from app.indicators.vwap import VWAP


def test_sma_matches_pandas_rolling_mean(ohlcv_df):
    result = SMA().calculate(ohlcv_df, {"period": 5})
    expected = ohlcv_df["close"].rolling(5).mean()
    pd.testing.assert_series_equal(result["sma_5"], expected, check_names=False)


def test_sma_does_not_mutate_input(ohlcv_df):
    original_cols = list(ohlcv_df.columns)
    SMA().calculate(ohlcv_df, {"period": 5})
    assert list(ohlcv_df.columns) == original_cols


def test_ema_uses_default_params_when_none_given(ohlcv_df):
    result = EMA().calculate(ohlcv_df, {})
    assert "ema_20" in result.columns  # default period = 20


def test_vwap_resets_each_session(ohlcv_df):
    result = VWAP().calculate(ohlcv_df, {})
    # First bar of each session: VWAP should equal that bar's typical price
    for day, group in result.groupby(result.index.date):
        first_bar = group.iloc[0]
        typical = (first_bar["high"] + first_bar["low"] + first_bar["close"]) / 3
        assert np.isclose(first_bar["vwap"], typical, atol=1e-6)


def test_atr_is_non_negative(ohlcv_df):
    result = ATR().calculate(ohlcv_df, {"period": 5})
    valid = result["atr_5"].dropna()
    assert (valid >= 0).all()


def test_rsi_is_bounded_0_to_100(ohlcv_df):
    result = RSI().calculate(ohlcv_df, {"period": 5})
    valid = result["rsi_5"].dropna()
    assert valid.between(0, 100).all()


def test_opening_range_high_gte_low_and_constant_per_session(ohlcv_df):
    result = OpeningRange().calculate(ohlcv_df, {"minutes": 10})
    assert (result["or_high_10"] >= result["or_low_10"]).all()
    for _, group in result.groupby(result.index.date):
        assert group["or_high_10"].nunique() == 1
        assert group["or_low_10"].nunique() == 1


def test_macd_uses_default_params_when_none_given(ohlcv_df):
    result = MACD().calculate(ohlcv_df, {})
    assert "macd_line_12_26_9" in result.columns
    assert "macd_signal_12_26_9" in result.columns
    assert "macd_hist_12_26_9" in result.columns


def test_macd_histogram_equals_line_minus_signal(ohlcv_df):
    result = MACD().calculate(ohlcv_df, {"fast_period": 3, "slow_period": 6, "signal_period": 4})
    line = result["macd_line_3_6_4"]
    signal = result["macd_signal_3_6_4"]
    hist = result["macd_hist_3_6_4"]
    pd.testing.assert_series_equal(hist, line - signal, check_names=False)


def test_macd_line_matches_fast_minus_slow_ema(ohlcv_df):
    result = MACD().calculate(ohlcv_df, {"fast_period": 3, "slow_period": 6, "signal_period": 4})
    fast_ema = ohlcv_df["close"].ewm(span=3, adjust=False).mean()
    slow_ema = ohlcv_df["close"].ewm(span=6, adjust=False).mean()
    expected = fast_ema - slow_ema
    pd.testing.assert_series_equal(result["macd_line_3_6_4"], expected, check_names=False)


def test_macd_does_not_mutate_input(ohlcv_df):
    original_cols = list(ohlcv_df.columns)
    MACD().calculate(ohlcv_df, {})
    assert list(ohlcv_df.columns) == original_cols
