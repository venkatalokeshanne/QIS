"""
Tests for app.services.backtest_data.fetch_backtest_bars, mocking
fetch_bars so these run without a real network call.
"""

import pandas as pd
import pytest

from app.core.exceptions import DataValidationError
from app.services.backtest_data import fetch_backtest_bars


def _valid_bars_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02 09:30", "2024-01-02 09:35", "2024-01-02 09:40"]),
            "open": [100.0, 100.5, 101.5],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [500, 600, 700],
        }
    )


def test_fetch_backtest_bars_returns_normalized_frame():
    df = fetch_backtest_bars("AAPL", "5min", fetch_bars=lambda *a, **kw: _valid_bars_df())
    assert len(df) == 3
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]


def test_fetch_backtest_bars_passes_symbol_interval_and_dates_through():
    captured = {}

    def fake_fetch(symbol, interval, outputsize, start_date, end_date, **kwargs):
        captured["symbol"] = symbol
        captured["interval"] = interval
        captured["outputsize"] = outputsize
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return _valid_bars_df()

    fetch_backtest_bars("TSLA", "15min", start_date="2024-01-01", end_date="2024-02-01", fetch_bars=fake_fetch)

    assert captured["symbol"] == "TSLA"
    assert captured["interval"] == "15min"
    assert captured["start_date"] == "2024-01-01"
    assert captured["end_date"] == "2024-02-01"


def test_fetch_backtest_bars_omits_dates_by_default():
    captured = {}

    def fake_fetch(symbol, interval, outputsize, start_date, end_date, **kwargs):
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return _valid_bars_df()

    fetch_backtest_bars("TSLA", "15min", fetch_bars=fake_fetch)

    assert captured["start_date"] is None
    assert captured["end_date"] is None


def test_fetch_backtest_bars_rejects_invalid_bars():
    bad_bars = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02 09:30"]),
            "open": [-1],
            "high": [101],
            "low": [99],
            "close": [100],
            "volume": [500],
        }
    )
    with pytest.raises(DataValidationError):
        fetch_backtest_bars("BAD", "5min", fetch_bars=lambda *a, **kw: bad_bars)
