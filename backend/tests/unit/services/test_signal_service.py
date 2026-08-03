"""
Tests for app.services.signal_service -- re-running a strategy's
entry/exit logic against the freshest bar and detecting whether a
NEW event landed exactly on that bar.

Uses sma_cross (fast=3/slow=8, both registered defaults) with a
hand-built price series: decline (warm-up) -> sharp rise (crosses up
at 2024-01-02 11:20) -> decline again (crosses back down, signal_exit,
at 2024-01-02 12:10). Truncating the fetched bars at different points
reproduces exactly what a live poll would see at each moment in time.
"""

import pandas as pd
import pytest

from app.services import signal_service
from app.strategies.registry import discover_strategies


@pytest.fixture(autouse=True)
def _ensure_strategies_registered():
    discover_strategies()


def _full_bars() -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:30", periods=40, freq="5min")
    prices = (
        [100 - 0.3 * i for i in range(20)]
        + [100 - 0.3 * 19 + 0.8 * i for i in range(1, 11)]
        + [100 - 0.3 * 19 + 0.8 * 10 - 0.9 * i for i in range(1, 10)]
    )
    return pd.DataFrame(
        {
            "date": idx[: len(prices)],
            "open": prices,
            "high": [p + 0.2 for p in prices],
            "low": [p - 0.2 for p in prices],
            "close": prices,
            "volume": [500] * len(prices),
        }
    )


def _fetch_bars_up_to(timestamp: str):
    """Fake `fetch_bars` standing in for tastytrade_client -- returns the
    same raw shape (a "date" column + lowercase OHLCV) the real client
    returns, truncated as if `timestamp` were the freshest available bar."""

    def _fetch(symbol, interval, outputsize):
        full = _full_bars()
        cutoff = full["date"] <= pd.Timestamp(timestamp)
        return full[cutoff].reset_index(drop=True)

    return _fetch


def test_check_signal_detects_new_entry_on_latest_bar():
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    result = signal_service.check_signal("AAPL", "5min", "sma_cross", {}, fetch_bars=fetch_bars)

    assert result.event == "entry"
    assert result.direction == "long"
    assert result.as_of == pd.Timestamp("2024-01-02 11:20:00")


def test_check_signal_detects_new_exit_on_latest_bar():
    fetch_bars = _fetch_bars_up_to("2024-01-02 12:10:00")
    result = signal_service.check_signal("AAPL", "5min", "sma_cross", {}, fetch_bars=fetch_bars)

    assert result.event == "exit"
    assert result.exit_reason == "signal_exit"
    assert result.as_of == pd.Timestamp("2024-01-02 12:10:00")


def test_check_signal_reports_no_event_mid_position():
    """The freshest bar always looks like 'end of the fetch window,' not
    a real strategy exit or entry -- must not be misreported as a
    signal just because the live snapshot happens to end there."""
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:35:00")
    result = signal_service.check_signal("AAPL", "5min", "sma_cross", {}, fetch_bars=fetch_bars)

    assert result.event is None
    assert result.direction is None
    assert result.exit_reason is None


def test_check_signal_symbol_is_uppercased():
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    result = signal_service.check_signal("aapl", "5min", "sma_cross", {}, fetch_bars=fetch_bars)
    assert result.symbol == "AAPL"


def test_check_signal_unknown_strategy_raises():
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    with pytest.raises(KeyError):
        signal_service.check_signal("AAPL", "5min", "not_a_real_strategy", {}, fetch_bars=fetch_bars)
