"""
Tests for app.services.scanner_service -- looping over many
symbols/strategies and keeping only the recent entry signals.

Reuses the same handcrafted decline -> sharp rise -> decline price
series test_signal_service.py uses so sma_cross (fast=3/slow=8)
produces a known entry ("golden cross" up, long) partway through.
"""

import pandas as pd
import pytest

from app.services import scanner_service
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import discover_strategies


@pytest.fixture(autouse=True)
def _ensure_strategies_registered():
    discover_strategies()


def _bars_with_entry_near_the_end() -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="5min")
    prices = [100 - 0.3 * i for i in range(20)] + [100 - 0.3 * 19 + 0.8 * i for i in range(1, 11)]
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


def _flat_bars_no_entry() -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:30", periods=30, freq="5min")
    return pd.DataFrame(
        {
            "date": idx,
            "open": [100.0] * 30,
            "high": [100.2] * 30,
            "low": [99.8] * 30,
            "close": [100.0] * 30,
            "volume": [500] * 30,
        }
    )


def _fetch_bars_for(frames_by_symbol):
    def _fetch(symbol, interval, outputsize, **kwargs):
        return frames_by_symbol[symbol]

    return _fetch


def test_scan_reports_a_match_for_a_symbol_with_a_recent_entry():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end(), "MSFT": _flat_bars_no_entry()})

    results, failed = scanner_service.scan_for_signals(
        ["AAPL", "MSFT"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, lookback_bars=10
    )

    assert failed == []
    assert len(results) == 1
    match = results[0]
    assert match.symbol == "AAPL"
    assert match.strategy_name == "sma_cross"
    assert match.signal_direction == "long"
    assert match.bars_ago < 10


def test_scan_ignores_entries_outside_the_lookback_window():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end()})

    results, _ = scanner_service.scan_for_signals(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, lookback_bars=1
    )

    # The entry landed a few bars back, well outside a 1-bar window.
    assert results == []


def test_scan_records_failed_symbols_without_aborting_the_whole_scan():
    def _fetch(symbol, interval, outputsize, **kwargs):
        if symbol == "BADTICKER":
            raise RuntimeError("no data")
        return _bars_with_entry_near_the_end()

    results, failed = scanner_service.scan_for_signals(
        ["AAPL", "BADTICKER"], "5min", strategy_names=["sma_cross"], fetch_bars=_fetch, lookback_bars=10
    )

    assert failed == ["BADTICKER"]
    assert len(results) == 1
    assert results[0].symbol == "AAPL"


def test_scan_defaults_to_every_registered_strategy_when_none_given():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end()})

    results, _ = scanner_service.scan_for_signals(["AAPL"], "5min", fetch_bars=fetch_bars, lookback_bars=10)

    # sma_cross should be among whatever strategies matched -- proves
    # a None strategy_names list ran the full registry, not nothing.
    assert any(r.strategy_name == "sma_cross" for r in results)


def test_scan_uses_cached_bars_when_provided_instead_of_fetching():
    calls = []

    def _fetch(symbol, interval, outputsize, **kwargs):
        calls.append(symbol)
        raise AssertionError("should not fetch when cached bars are available")

    df = _bars_with_entry_near_the_end().set_index("date")
    df.index.name = "timestamp"

    results, _ = scanner_service.scan_for_signals(
        ["AAPL"],
        "5min",
        strategy_names=["sma_cross"],
        fetch_bars=_fetch,
        lookback_bars=10,
        get_cached_bars=lambda symbol, interval: df,
    )

    assert calls == []
    assert len(results) == 1
