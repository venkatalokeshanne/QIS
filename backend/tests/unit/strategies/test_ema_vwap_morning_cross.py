"""Tests for the Morning EMA/VWAP Cross strategy."""

import pandas as pd
import pytest

from app.domain.interfaces.strategy import TradeDirection
from app.strategies.ema_vwap_morning_cross.strategy import EMAVWAPMorningCross


def _prepared_df(times, fast, slow, close, vwap):
    """Hand-built 'already prepared' frame so entry logic is tested exactly."""
    idx = pd.DatetimeIndex(pd.to_datetime(times))
    return pd.DataFrame(
        {"ema_9": fast, "ema_21": slow, "close": close, "vwap": vwap}, index=idx
    )


def test_long_entry_on_cross_up_above_vwap_before_noon():
    df = _prepared_df(
        ["2024-01-02 09:35", "2024-01-02 09:40", "2024-01-02 09:45"],
        fast=[99.0, 101.0, 102.0],
        slow=[100.0, 100.0, 100.0],
        close=[100.0, 101.0, 102.0],
        vwap=[100.5, 100.5, 100.5],
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {})
    assert entries.iloc[0] is None  # no prior bar to cross from
    assert entries.iloc[1] == TradeDirection.LONG  # cross happens here
    assert entries.iloc[2] is None  # already above — a state, not a cross


def test_equal_emas_on_prior_bar_counts_as_cross():
    df = _prepared_df(
        ["2024-01-02 09:35", "2024-01-02 09:40"],
        fast=[100.0, 101.0],
        slow=[100.0, 100.0],
        close=[100.0, 102.0],
        vwap=[99.0, 99.0],
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {})
    assert entries.iloc[1] == TradeDirection.LONG


def test_no_long_entry_when_close_below_vwap():
    df = _prepared_df(
        ["2024-01-02 09:35", "2024-01-02 09:40"],
        fast=[99.0, 101.0],
        slow=[100.0, 100.0],
        close=[100.0, 101.0],
        vwap=[100.5, 102.0],  # cross fires but close is below VWAP
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {})
    assert entries.iloc[1] is None


def test_no_entries_at_or_after_entry_cutoff():
    df = _prepared_df(
        ["2024-01-02 11:55", "2024-01-02 12:00"],
        fast=[99.0, 101.0],
        slow=[100.0, 100.0],
        close=[100.0, 101.0],
        vwap=[99.0, 99.0],
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {})
    assert entries.iloc[1] is None  # the 12:00 bar is already afternoon

    # Same cross one bar earlier (11:55) is still morning.
    df2 = _prepared_df(
        ["2024-01-02 11:50", "2024-01-02 11:55"],
        fast=[99.0, 101.0],
        slow=[100.0, 100.0],
        close=[100.0, 101.0],
        vwap=[99.0, 99.0],
    )
    entries2 = EMAVWAPMorningCross().generate_entries(df2, {})
    assert entries2.iloc[1] == TradeDirection.LONG


def test_short_entry_on_cross_down_below_vwap():
    df = _prepared_df(
        ["2024-01-02 09:35", "2024-01-02 09:40"],
        fast=[101.0, 99.0],
        slow=[100.0, 100.0],
        close=[100.0, 98.0],
        vwap=[99.5, 99.5],
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {})
    assert entries.iloc[1] == TradeDirection.SHORT


def test_direction_param_filters_sides():
    df = _prepared_df(
        ["2024-01-02 09:35", "2024-01-02 09:40"],
        fast=[101.0, 99.0],
        slow=[100.0, 100.0],
        close=[100.0, 98.0],
        vwap=[99.5, 99.5],
    )
    entries = EMAVWAPMorningCross().generate_entries(df, {"direction": "long_only"})
    assert entries.iloc[1] is None


def test_exits_fire_at_and_after_flat_time_only():
    df = _prepared_df(
        ["2024-01-02 15:40", "2024-01-02 15:45", "2024-01-02 15:50"],
        fast=[100.0] * 3,
        slow=[100.0] * 3,
        close=[100.0] * 3,
        vwap=[100.0] * 3,
    )
    exits = EMAVWAPMorningCross().generate_exits(df, {})
    assert list(exits) == [False, True, True]


def test_invalid_params_raise():
    strategy = EMAVWAPMorningCross()
    with pytest.raises(ValueError):
        strategy.validate_params({"fast_period": 21, "slow_period": 9})
    with pytest.raises(ValueError):
        strategy.validate_params({"flat_time": "3:50 PM"})


def test_prepare_attaches_ema_and_vwap_columns():
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="5min")
    df = pd.DataFrame(
        {
            "open": 100.0,
            "high": 100.5,
            "low": 99.5,
            "close": 100.0,
            "volume": 1000,
        },
        index=idx,
    )
    out = EMAVWAPMorningCross().prepare(df, {})
    for col in ("ema_9", "ema_21", "vwap"):
        assert col in out.columns


def test_end_to_end_flat_then_rally_produces_morning_long():
    # 25 flat bars (EMA warm-up), then a rally at 11:35 — EMA(9) crosses
    # above EMA(21) with price above VWAP, well before the noon cutoff.
    idx = pd.date_range("2024-01-02 09:30", periods=40, freq="5min")
    closes = [100.0] * 25 + [110.0] * 15
    df = pd.DataFrame(
        {
            "open": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "close": closes,
            "volume": 1000,
        },
        index=idx,
    )
    strategy = EMAVWAPMorningCross()
    prepared = strategy.prepare(df, {})
    entries = strategy.generate_entries(prepared, {})

    signal_bars = entries[entries.notna()]
    assert len(signal_bars) == 1
    assert signal_bars.iloc[0] == TradeDirection.LONG
    assert signal_bars.index[0].time() < pd.Timestamp("2024-01-02 12:00").time()
