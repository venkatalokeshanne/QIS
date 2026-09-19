"""
Tests for app.services.signal_service -- the shared "freshest bars for
a symbol+interval" fetch used by Scanner and Day Prep.
"""

import pandas as pd
import pytest

from app.core.exceptions import DataValidationError
from app.domain.interfaces.strategy import Trade, TradeDirection
from app.services import signal_service


def _fake_fetch_bars(symbol, interval, outputsize, **kwargs):
    idx = pd.date_range("2024-01-02 09:30", periods=5, freq="5min")
    prices = [100.0, 100.5, 101.0, 100.8, 101.2]
    return pd.DataFrame(
        {
            "date": idx,
            "open": prices,
            "high": [p + 0.2 for p in prices],
            "low": [p - 0.2 for p in prices],
            "close": prices,
            "volume": [500] * len(prices),
        }
    )


def _fake_fetch_bars_invalid(symbol, interval, outputsize, **kwargs):
    return pd.DataFrame({"date": [], "open": [], "high": [], "low": [], "close": [], "volume": []})


def test_fetch_symbol_bars_normalizes_raw_frame():
    result = signal_service.fetch_symbol_bars("AAPL", "5min", fetch_bars=_fake_fetch_bars)

    assert list(result.columns) == ["open", "high", "low", "close", "volume"]
    assert result.index.name == "timestamp"
    assert len(result) == 5


def test_fetch_symbol_bars_passes_session_flags_through(monkeypatch):
    captured = {}

    def _fetch(symbol, interval, outputsize, **kwargs):
        captured.update(kwargs)
        return _fake_fetch_bars(symbol, interval, outputsize)

    signal_service.fetch_symbol_bars(
        "AAPL", "5min", fetch_bars=_fetch, include_extended_hours=True, include_overnight=True
    )

    assert captured == {"include_extended_hours": True, "include_overnight": True}


def test_fetch_symbol_bars_raises_on_unusable_data():
    with pytest.raises(DataValidationError):
        signal_service.fetch_symbol_bars("AAPL", "5min", fetch_bars=_fake_fetch_bars_invalid)


def test_trade_direction_returns_string_value():
    trade = Trade(
        entry_time=pd.Timestamp("2024-01-02 10:00"),
        exit_time=None,
        direction=TradeDirection.SHORT,
        entry_price=100.0,
        exit_price=None,
        quantity=1,
        exit_reason=None,
    )

    assert signal_service._trade_direction(trade) == "short"
