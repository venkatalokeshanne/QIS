"""Tests for filter discovery and correctness of each filter."""

import pandas as pd
import pytest

from app.filters.registry import discover_filters, get_filter, list_filters
from app.indicators.atr import ATR
from app.indicators.ema import EMA
from app.indicators.rsi import RSI
from app.indicators.volume_average import VolumeAverage
from app.indicators.vwap import VWAP

EXPECTED_FILTERS = {
    "price_above_vwap",
    "ema_above",
    "volume_above_average",
    "rsi_below",
    "atr_above_threshold",
    "gap_up",
    "gap_down",
    "higher_high",
    "inside_bar",
    "outside_bar",
}


def test_discovery_finds_all_built_in_filters():
    discover_filters()
    names = {f["name"] for f in list_filters()}
    assert EXPECTED_FILTERS.issubset(names)


def test_get_unknown_filter_raises():
    discover_filters()
    with pytest.raises(KeyError):
        get_filter("does_not_exist")


def test_price_above_vwap(ohlcv_df):
    enriched = VWAP().calculate(ohlcv_df, {})
    result = get_filter("price_above_vwap").apply(enriched, {})
    expected = enriched["close"] > enriched["vwap"]
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_price_above_vwap_raises_without_vwap_column(ohlcv_df):
    with pytest.raises(KeyError):
        get_filter("price_above_vwap").apply(ohlcv_df, {})


def test_ema_above(ohlcv_df):
    enriched = EMA().calculate(ohlcv_df, {"period": 5})
    enriched = EMA().calculate(enriched, {"period": 10})
    result = get_filter("ema_above").apply(enriched, {"fast_period": 5, "slow_period": 10})
    expected = enriched["ema_5"] > enriched["ema_10"]
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_volume_above_average(ohlcv_df):
    enriched = VolumeAverage().calculate(ohlcv_df, {"period": 5})
    result = get_filter("volume_above_average").apply(enriched, {"period": 5})
    expected = enriched["volume"] > enriched["volume_avg_5"]
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_rsi_below(ohlcv_df):
    enriched = RSI().calculate(ohlcv_df, {"period": 5})
    result = get_filter("rsi_below").apply(enriched, {"period": 5, "threshold": 40})
    expected = enriched["rsi_5"] < 40
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_atr_above_threshold(ohlcv_df):
    enriched = ATR().calculate(ohlcv_df, {"period": 5})
    result = get_filter("atr_above_threshold").apply(enriched, {"period": 5, "threshold": 0.1})
    expected = enriched["atr_5"] > 0.1
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_higher_high():
    idx = pd.date_range("2024-01-02 09:30", periods=4, freq="1min")
    df = pd.DataFrame({"high": [10, 12, 11, 13]}, index=idx)
    result = get_filter("higher_high").apply(df, {})
    assert list(result) == [False, True, False, True]


def test_inside_bar():
    idx = pd.date_range("2024-01-02 09:30", periods=3, freq="1min")
    df = pd.DataFrame({"high": [10, 9, 11], "low": [5, 6, 4]}, index=idx)
    result = get_filter("inside_bar").apply(df, {})
    assert list(result) == [False, True, False]


def test_outside_bar():
    idx = pd.date_range("2024-01-02 09:30", periods=3, freq="1min")
    df = pd.DataFrame({"high": [10, 12, 11], "low": [5, 3, 6]}, index=idx)
    result = get_filter("outside_bar").apply(df, {})
    assert list(result) == [False, True, False]


def test_gap_up_flags_only_first_bar_of_session_when_gapped():
    idx = pd.to_datetime(
        ["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-03 09:30", "2024-01-03 09:31"]
    )
    df = pd.DataFrame(
        {"open": [100, 100.5, 110, 110], "close": [100.5, 101, 110.5, 111]}, index=idx
    )
    result = get_filter("gap_up").apply(df, {"threshold_pct": 0.01})
    # Session 2 opens at 110 vs prior session close of 101 -> gap up on its first bar only
    assert list(result) == [False, False, True, False]


def test_gap_down_flags_only_first_bar_of_session_when_gapped():
    idx = pd.to_datetime(
        ["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-03 09:30", "2024-01-03 09:31"]
    )
    df = pd.DataFrame(
        {"open": [100, 100.5, 90, 90], "close": [100.5, 101, 90.5, 91]}, index=idx
    )
    result = get_filter("gap_down").apply(df, {"threshold_pct": 0.01})
    assert list(result) == [False, False, True, False]
