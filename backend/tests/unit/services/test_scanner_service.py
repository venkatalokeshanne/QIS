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

    # Historical-trust enrichment (see test_scan_attaches_historical_trust_to_matches
    # below) always does its own separate fetch -- a full trailing year,
    # unrelated to the live scan's cached bars -- so it's disabled here
    # to isolate what this test actually checks: the live scan loop
    # itself doesn't re-fetch when cached bars are already available.
    results, _ = scanner_service.scan_for_signals(
        ["AAPL"],
        "5min",
        strategy_names=["sma_cross"],
        fetch_bars=_fetch,
        lookback_bars=10,
        get_cached_bars=lambda symbol, interval: df,
        include_historical_trust=False,
    )

    assert calls == []
    assert len(results) == 1


def test_scan_attaches_historical_trust_to_matches():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end()})

    results, _ = scanner_service.scan_for_signals(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, lookback_bars=10
    )

    assert len(results) == 1
    match = results[0]
    # sma_cross trades on this fixture (that's the entry the live scan
    # itself matched on), so the trailing-year re-run should find at
    # least that one trade and score it, not leave the fields None.
    assert match.historical_trade_count is not None
    assert match.historical_trade_count >= 1


def test_scan_leaves_historical_trust_none_when_historical_fetch_fails():
    def _fetch(symbol, interval, outputsize, start_date=None, end_date=None, **kwargs):
        # The live scan's own fetch (no start_date/end_date) should
        # still succeed; only the historical-trust fetch (which always
        # passes start_date/end_date, see scanner_service) fails.
        if start_date is not None:
            raise RuntimeError("historical fetch unavailable")
        return _bars_with_entry_near_the_end()

    results, _ = scanner_service.scan_for_signals(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=_fetch, lookback_bars=10
    )

    assert len(results) == 1
    assert results[0].historical_trade_count is None
    assert results[0].historical_win_rate is None


def test_scan_can_skip_historical_trust_enrichment():
    calls = []

    def _fetch(symbol, interval, outputsize, start_date=None, **kwargs):
        calls.append(start_date)
        return _bars_with_entry_near_the_end()

    results, _ = scanner_service.scan_for_signals(
        ["AAPL"],
        "5min",
        strategy_names=["sma_cross"],
        fetch_bars=_fetch,
        lookback_bars=10,
        include_historical_trust=False,
    )

    assert len(results) == 1
    assert results[0].historical_trade_count is None
    # Only the live scan's own fetch happened (start_date=None) -- no
    # separate historical-window fetch (which would pass a start_date).
    assert all(s is None for s in calls)
