"""Tests for app.services.daily_selector_service."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from app.core.exceptions import NotFoundError
from app.services import calibration_store, daily_selector_service
from app.services.calibration_service import TickerProfile
from app.strategies.registry import discover_strategies


def _fake_fetch_bars(symbol, interval="1min", outputsize=5000, start_date=None, end_date=None, **kwargs):
    """Deterministic synthetic bars: a slow, noise-free uptrend --
    always classifies "trending" once enough bars exist, and gives real
    strategies (sma_cross, rsi_reversal, vwap_reversion) something to
    trade on."""
    start = pd.Timestamp(start_date) if start_date else pd.Timestamp("2023-01-01")
    end = pd.Timestamp(end_date) if end_date else start + pd.Timedelta(days=30)

    if interval == "1day":
        idx = pd.bdate_range(start, end)
    else:
        freq = {"1min": "1min", "5min": "5min", "15min": "15min", "30min": "30min", "1h": "1h"}.get(interval, "5min")
        days = pd.bdate_range(max(start, end - pd.Timedelta(days=5)), end)
        idx = []
        for d in days:
            idx.extend(
                pd.date_range(d + pd.Timedelta(hours=9, minutes=30), d + pd.Timedelta(hours=16), freq=freq, inclusive="left")
            )
        idx = pd.DatetimeIndex(idx)

    n = len(idx)
    closes = 100 + np.linspace(0, n * 0.05, n)
    return pd.DataFrame(
        {
            "date": idx,
            "open": closes,
            "high": closes + 0.3,
            "low": closes - 0.3,
            "close": closes,
            "volume": np.full(n, 1000.0),
        }
    )


def _profile(**overrides):
    base = dict(
        symbol="TEST",
        interval="5min",
        calibrated_through="2024-03-01",
        market_proxies=["SPY"],
        default_strategy="vwap_reversion",
        strategy_by_regime={},
        regime_trade_counts={},
        stop_loss_atr_multiple=1.5,
        take_profit_atr_multiple=3.0,
        entry_time_start=None,
        entry_time_end=None,
        regime_params={},
    )
    base.update(overrides)
    return TickerProfile(**base)


@pytest.fixture(autouse=True)
def _discover():
    discover_strategies()


# --- select_for_today -------------------------------------------------


def test_select_for_today_raises_for_uncalibrated_symbol(monkeypatch):
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: None)
    with pytest.raises(NotFoundError):
        daily_selector_service.select_for_today("NOPE", "5min", fetch_bars=_fake_fetch_bars)


def test_select_for_today_uses_the_calibrated_pick_for_the_observed_regime(monkeypatch):
    base_profile = _profile()
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: base_profile)
    as_of = pd.Timestamp("2024-06-15 15:00")

    # First pass: nothing calibrated for any specific regime yet -> falls
    # back to default_strategy. Discover which bucket the synthetic data
    # actually classifies as, rather than hardcoding a guess.
    first = daily_selector_service.select_for_today("TEST", "5min", as_of=as_of, fetch_bars=_fake_fetch_bars)
    assert first.selected_strategy == "vwap_reversion"
    assert first.used_fallback is True
    assert first.regime_bucket is not None

    # Second pass: calibrate that EXACT observed bucket to a different
    # strategy -- selection should now pick it instead of the fallback.
    tuned_profile = _profile(strategy_by_regime={first.regime_bucket: "rsi_reversal"})
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: tuned_profile)

    second = daily_selector_service.select_for_today("TEST", "5min", as_of=as_of, fetch_bars=_fake_fetch_bars)
    assert second.regime_bucket == first.regime_bucket
    assert second.selected_strategy == "rsi_reversal"
    assert second.used_fallback is False


def test_select_for_today_reports_calibrated_static_params(monkeypatch):
    profile = _profile(stop_loss_atr_multiple=2.5, take_profit_atr_multiple=4.0, entry_time_start="09:30", entry_time_end="11:30")
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: profile)

    result = daily_selector_service.select_for_today("TEST", "5min", fetch_bars=_fake_fetch_bars)

    assert result.stop_loss_atr_multiple == 2.5
    assert result.take_profit_atr_multiple == 4.0
    assert result.entry_time_start == "09:30"
    assert result.entry_time_end == "11:30"


def test_select_for_today_applies_a_regime_params_override_over_ticker_wide_defaults(monkeypatch):
    as_of = pd.Timestamp("2024-06-15 15:00")

    # Discover the bucket the synthetic data classifies as, same trick
    # test_select_for_today_uses_the_calibrated_pick_for_the_observed_regime
    # uses, then calibrate that bucket with its OWN tuned params distinct
    # from the ticker-wide defaults.
    discovery_profile = _profile()
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: discovery_profile)
    discovered = daily_selector_service.select_for_today("TEST", "5min", as_of=as_of, fetch_bars=_fake_fetch_bars)
    bucket = discovered.regime_bucket

    tuned_profile = _profile(
        strategy_by_regime={bucket: "rsi_reversal"},
        stop_loss_atr_multiple=1.5,
        take_profit_atr_multiple=3.0,
        regime_params={bucket: {"stop_loss_atr_multiple": 9.0, "take_profit_atr_multiple": 8.0, "entry_time_start": "10:00", "entry_time_end": "12:00"}},
    )
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: tuned_profile)

    result = daily_selector_service.select_for_today("TEST", "5min", as_of=as_of, fetch_bars=_fake_fetch_bars)

    assert result.regime_bucket == bucket
    assert result.selected_strategy == "rsi_reversal"
    assert result.stop_loss_atr_multiple == 9.0
    assert result.take_profit_atr_multiple == 8.0
    assert result.entry_time_start == "10:00"
    assert result.entry_time_end == "12:00"


# --- _group_into_segments / _test_window_days -----------------------------


_PARAMS_A = {"stop_loss_atr_multiple": 1.5, "take_profit_atr_multiple": 3.0, "entry_time_start": None, "entry_time_end": None}
_PARAMS_B = {"stop_loss_atr_multiple": 2.0, "take_profit_atr_multiple": 4.0, "entry_time_start": "09:30", "entry_time_end": "11:00"}


def test_group_into_segments_merges_consecutive_same_strategy_days():
    days = [
        (date(2024, 1, 1), "b1", "strat_a", _PARAMS_A),
        (date(2024, 1, 2), "b1", "strat_a", _PARAMS_A),
        (date(2024, 1, 3), "b2", "strat_a", _PARAMS_A),  # different bucket, same strategy+params -> merges
        (date(2024, 1, 4), "b2", "strat_b", _PARAMS_A),  # strategy changes -> new segment
    ]
    segments = daily_selector_service._group_into_segments(days)
    assert segments == [
        ("b1", "strat_a", _PARAMS_A, date(2024, 1, 1), date(2024, 1, 3)),
        ("b2", "strat_b", _PARAMS_A, date(2024, 1, 4), date(2024, 1, 4)),
    ]


def test_group_into_segments_does_not_merge_same_strategy_with_different_params():
    days = [
        (date(2024, 1, 1), "b1", "strat_a", _PARAMS_A),
        (date(2024, 1, 2), "b2", "strat_a", _PARAMS_B),  # same strategy, different resolved params -> new segment
    ]
    segments = daily_selector_service._group_into_segments(days)
    assert segments == [
        ("b1", "strat_a", _PARAMS_A, date(2024, 1, 1), date(2024, 1, 1)),
        ("b2", "strat_a", _PARAMS_B, date(2024, 1, 2), date(2024, 1, 2)),
    ]


def test_group_into_segments_empty_input():
    assert daily_selector_service._group_into_segments([]) == []


# --- backtest_selection -------------------------------------------------


def test_backtest_selection_clamps_a_requested_start_before_the_cutoff(monkeypatch):
    # Requested start (2024-01-01) predates the calibration cutoff
    # (2024-03-01) -- the out-of-sample guarantee must win: nothing
    # before the cutoff may ever appear in the result.
    profile = _profile(default_strategy="sma_cross", calibrated_through="2024-03-01", market_proxies=["SPY"])
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: profile)

    result = daily_selector_service.backtest_selection(
        symbol="TEST",
        interval="5min",
        start_date="2024-01-01",
        test_end_date="2024-04-15",
        fetch_bars=_fake_fetch_bars,
    )

    cutoff = pd.Timestamp("2024-03-01").date()
    test_end = pd.Timestamp("2024-04-15").date()
    assert result.test_start == "2024-03-01"  # clamped up to the cutoff, not the requested 2024-01-01
    assert result.test_end == "2024-04-15"
    assert result.baseline_strategy == "sma_cross"

    for segment in result.segments:
        seg_start = pd.Timestamp(segment.start_date).date()
        seg_end = pd.Timestamp(segment.end_date).date()
        assert seg_start >= cutoff
        assert seg_end <= test_end

    # Every switching trade carries which strategy generated it, is
    # chronologically sorted, and falls within the same bounds as the
    # segments (see the honesty property above).
    assert len(result.switching_trades) == result.switching_trade_count
    assert [t.entry_time for t in result.switching_trades] == sorted(t.entry_time for t in result.switching_trades)
    for trade in result.switching_trades:
        assert trade.strategy_name
        assert cutoff <= trade.entry_time.date() <= test_end


def test_backtest_selection_honors_a_requested_start_after_the_cutoff(monkeypatch):
    profile = _profile(default_strategy="sma_cross", calibrated_through="2024-03-01", market_proxies=["SPY"])
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: profile)

    result = daily_selector_service.backtest_selection(
        symbol="TEST",
        interval="5min",
        start_date="2024-03-15",  # after the cutoff -- should NOT be clamped
        test_end_date="2024-04-15",
        fetch_bars=_fake_fetch_bars,
    )

    assert result.test_start == "2024-03-15"


def test_backtest_selection_raises_for_uncalibrated_symbol(monkeypatch):
    monkeypatch.setattr(calibration_store, "load_profile", lambda symbol: None)
    with pytest.raises(NotFoundError):
        daily_selector_service.backtest_selection(
            symbol="NOPE", interval="5min", start_date="2024-01-01", test_end_date="2024-04-15", fetch_bars=_fake_fetch_bars
        )
