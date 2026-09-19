"""Tests for app.services.calibration_service."""

from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from app.domain.interfaces.strategy import Trade, TradeDirection
from app.services.calibration_service import (
    MIN_REGIME_TRADES,
    _SL_ATR_GRID,
    _TP_ATR_GRID,
    _TIME_WINDOW_GRID,
    _pick_best_strategy,
    _sweep_parameters,
    calibrate_ticker,
)
from app.strategies.registry import discover_strategies, get_strategy


def _trade(pnl, day_offset=0):
    entry = pd.Timestamp("2024-02-05 10:00") + timedelta(days=day_offset)
    return Trade(
        entry_time=entry,
        exit_time=entry + timedelta(minutes=30),
        direction=TradeDirection.LONG,
        entry_price=100.0,
        exit_price=100.0 + pnl,
        quantity=1.0,
        pnl=pnl,
        exit_reason="signal_exit",
    )


# --- _pick_best_strategy -------------------------------------------------


def test_pick_best_strategy_returns_none_for_empty_input():
    assert _pick_best_strategy({}, capital=10_000.0) is None


def test_pick_best_strategy_returns_none_when_every_candidate_has_zero_trades():
    assert _pick_best_strategy({"a": [], "b": []}, capital=10_000.0) is None


def test_pick_best_strategy_prefers_the_more_profitable_candidate():
    winner_trades = [_trade(200, i) for i in range(10)]
    loser_trades = [_trade(-50, i) for i in range(10)]
    best = _pick_best_strategy({"winner": winner_trades, "loser": loser_trades}, capital=10_000.0)
    assert best == "winner"


# --- _sweep_parameters -------------------------------------------------


def _synthetic_intraday_df(n_days=15, freq="5min"):
    days = pd.bdate_range("2024-02-01", periods=n_days)
    idx = []
    for d in days:
        idx.extend(pd.date_range(d + pd.Timedelta(hours=9, minutes=30), d + pd.Timedelta(hours=16), freq=freq, inclusive="left"))
    idx = pd.DatetimeIndex(idx)
    rng = np.random.RandomState(0)
    closes = 100 + np.linspace(0, 15, len(idx)) + rng.normal(0, 0.2, len(idx))
    return pd.DataFrame(
        {"open": closes, "high": closes + 0.3, "low": closes - 0.3, "close": closes, "volume": 1000.0},
        index=idx,
    )


def test_sweep_parameters_returns_a_point_from_the_grid():
    discover_strategies()
    df = _synthetic_intraday_df()
    report_start = pd.Timestamp("2024-02-01").date()

    sl, tp, (t_start, t_end) = _sweep_parameters(df, "sma_cross", report_start)

    assert sl in _SL_ATR_GRID
    assert tp in _TP_ATR_GRID
    assert (t_start, t_end) in _TIME_WINDOW_GRID


# --- calibrate_ticker (end to end, synthetic fetch_bars) -----------------


def _fake_fetch_bars(symbol, interval="1min", outputsize=5000, start_date=None, end_date=None, **kwargs):
    """Deterministic synthetic bars: a slow uptrend with noise, enough
    for real strategies to generate a handful of trades and for
    ADX/ATR to classify most days once warmed up."""
    start = pd.Timestamp(start_date) if start_date else pd.Timestamp("2024-01-01")
    end = pd.Timestamp(end_date) if end_date else start + pd.Timedelta(days=30)
    days = pd.bdate_range(start, end)

    if interval == "1day":
        idx = pd.DatetimeIndex(days)
    else:
        freq = {"1min": "1min", "5min": "5min", "15min": "15min", "30min": "30min", "1h": "1h"}.get(interval, "5min")
        idx = []
        for d in days:
            idx.extend(
                pd.date_range(d + pd.Timedelta(hours=9, minutes=30), d + pd.Timedelta(hours=16), freq=freq, inclusive="left")
            )
        idx = pd.DatetimeIndex(idx)

    n = len(idx)
    rng = np.random.RandomState(abs(hash(symbol)) % (2**31))
    closes = 100 + np.linspace(0, 25, n) + rng.normal(0, 0.3, n)
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


_CANDIDATE_STRATEGIES = ["sma_cross", "vwap_reversion", "rsi_reversal"]


def test_calibrate_ticker_produces_a_sane_profile():
    discover_strategies()
    profile = calibrate_ticker(
        symbol="test",
        interval="5min",
        market_proxies=["SPY", "QQQ"],
        start_date="2024-02-01",
        cutoff_date="2024-03-15",
        strategy_names=_CANDIDATE_STRATEGIES,
        fetch_bars=_fake_fetch_bars,
    )

    assert profile.symbol == "TEST"  # upper-cased
    assert profile.interval == "5min"
    assert profile.calibrated_through == "2024-03-15"
    assert profile.market_proxies == ["SPY", "QQQ"]
    assert profile.default_strategy in _CANDIDATE_STRATEGIES
    assert profile.stop_loss_atr_multiple in _SL_ATR_GRID
    assert profile.take_profit_atr_multiple in _TP_ATR_GRID
    assert (profile.entry_time_start, profile.entry_time_end) in _TIME_WINDOW_GRID

    for bucket_key, strategy_name in profile.strategy_by_regime.items():
        assert strategy_name in _CANDIDATE_STRATEGIES
        assert profile.regime_trade_counts[bucket_key] >= MIN_REGIME_TRADES


def test_calibrate_ticker_raises_when_no_strategy_produces_trades():
    def empty_fetch_bars(symbol, interval="1min", outputsize=5000, start_date=None, end_date=None, **kwargs):
        # A single bar is nowhere near enough for any strategy's
        # indicator warm-up -- guaranteed zero trades from everything.
        idx = pd.DatetimeIndex([pd.Timestamp(start_date or "2024-02-01")])
        return pd.DataFrame({"date": idx, "open": [100.0], "high": [100.5], "low": [99.5], "close": [100.0], "volume": [1000.0]})

    discover_strategies()
    with pytest.raises(ValueError):
        calibrate_ticker(
            symbol="TEST",
            interval="5min",
            market_proxies=["SPY"],
            start_date="2024-02-01",
            cutoff_date="2024-02-02",
            strategy_names=_CANDIDATE_STRATEGIES,
            fetch_bars=empty_fetch_bars,
        )
