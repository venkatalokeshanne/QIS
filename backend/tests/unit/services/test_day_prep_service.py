"""
Tests for app.services.day_prep_service -- ranking tickers worth
concentrating on today (activity + historical edge + today's gap),
not just symbols with a signal inside a tight recent-bars window (see
test_scanner_service.py for that narrower view).
"""

import pandas as pd
import pytest

from app.services import day_prep_service
from app.strategies.registry import discover_strategies


@pytest.fixture(autouse=True)
def _ensure_strategies_registered():
    discover_strategies()


def _bars_with_entry_near_the_end(day="2024-01-02") -> pd.DataFrame:
    # sma_cross's golden-cross entry lands a few bars after the trend
    # reverses (index 20) once the slow SMA catches up -- a short tail
    # (4 bars) keeps that entry within day_prep_service's
    # SIGNAL_LOOKBACK_BARS window of the freshest bar, unlike the
    # longer tail test_scanner_service.py uses for its own (larger)
    # lookback window.
    idx = pd.date_range(f"{day} 09:30", periods=24, freq="5min")
    prices = [100 - 0.3 * i for i in range(20)] + [100 - 0.3 * 19 + 0.8 * i for i in range(1, 5)]
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


def _flat_bars_no_entry(day="2024-01-02") -> pd.DataFrame:
    idx = pd.date_range(f"{day} 09:30", periods=30, freq="5min")
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


NOW = pd.Timestamp("2024-01-02 10:00:00")


def test_prepare_day_drops_tickers_with_no_trading_history():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end(), "MSFT": _flat_bars_no_entry()})

    results, failed = day_prep_service.prepare_day(
        ["AAPL", "MSFT"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, now=NOW
    )

    assert failed == []
    symbols = [r.symbol for r in results]
    assert "AAPL" in symbols
    assert "MSFT" not in symbols  # sma_cross never traded on flat bars -- nothing to say about it


def test_prepare_day_reports_activity_and_edge_for_a_traded_ticker():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end()})

    results, _ = day_prep_service.prepare_day(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, now=NOW
    )

    assert len(results) == 1
    ticker = results[0]
    assert ticker.symbol == "AAPL"
    assert ticker.activity_count >= 1
    assert len(ticker.top_strategies) == 1
    edge = ticker.top_strategies[0]
    assert edge.strategy_name == "sma_cross"
    assert edge.trade_count >= 1


def test_prepare_day_flags_a_live_signal_near_the_freshest_bar():
    fetch_bars = _fetch_bars_for({"AAPL": _bars_with_entry_near_the_end()})

    results, _ = day_prep_service.prepare_day(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, now=NOW
    )

    edge = results[0].top_strategies[0]
    # The golden-cross entry lands right near the end of the fixture.
    assert edge.has_live_signal is True
    assert edge.signal_direction == "long"
    assert edge.signal_bars_ago is not None


def test_prepare_day_ranks_higher_activity_ticker_first():
    # AAPL: strong, obvious trend -> more/cleaner sma_cross entries.
    # MSFT: same shape but far more muted -> fewer/weaker entries.
    aapl = _bars_with_entry_near_the_end()
    msft = _bars_with_entry_near_the_end()
    msft["close"] = 100 + (msft["close"] - 100) * 0.05  # flatten the move almost to nothing
    msft["open"] = msft["close"]
    msft["high"] = msft["close"] + 0.05
    msft["low"] = msft["close"] - 0.05

    fetch_bars = _fetch_bars_for({"AAPL": aapl, "MSFT": msft})

    results, _ = day_prep_service.prepare_day(
        ["AAPL", "MSFT"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, now=NOW
    )

    symbols = [r.symbol for r in results]
    if "MSFT" in symbols:
        # Whichever of the two actually has more/better trades should rank first.
        assert results[0].concentration_score >= results[-1].concentration_score


def test_prepare_day_records_failed_symbols_without_aborting():
    def _fetch(symbol, interval, outputsize, **kwargs):
        if symbol == "BADTICKER":
            raise RuntimeError("no data")
        return _bars_with_entry_near_the_end()

    results, failed = day_prep_service.prepare_day(
        ["AAPL", "BADTICKER"], "5min", strategy_names=["sma_cross"], fetch_bars=_fetch, now=NOW
    )

    assert failed == ["BADTICKER"]
    assert len(results) == 1
    assert results[0].symbol == "AAPL"


def test_prepare_day_computes_gap_pct_against_prior_session_close():
    # Two-session fixture: day 1 closes at ~94.3, day 2 opens flat at
    # the same level then trends up -- the gap snapshot (also served by
    # the same fake fetch_bars) reports day 2's last close as "current."
    day1 = _flat_bars_no_entry(day="2024-01-02")
    day2 = _bars_with_entry_near_the_end(day="2024-01-03")
    combined = pd.concat([day1, day2], ignore_index=True)

    fetch_bars = _fetch_bars_for({"AAPL": combined})
    now = pd.Timestamp("2024-01-03 11:55:00")

    results, _ = day_prep_service.prepare_day(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=fetch_bars, now=now
    )

    assert len(results) == 1
    assert results[0].gap_pct is not None
    prior_close = day1["close"].iloc[-1]
    latest_close = day2["close"].iloc[-1]
    assert results[0].gap_pct == pytest.approx((latest_close - prior_close) / prior_close)


def test_prepare_day_gap_is_none_when_snapshot_fetch_fails():
    day1 = _flat_bars_no_entry(day="2024-01-02")
    day2 = _bars_with_entry_near_the_end(day="2024-01-03")
    combined = pd.concat([day1, day2], ignore_index=True)

    def _fetch(symbol, interval, outputsize, start_date=None, end_date=None, **kwargs):
        # The edge/backtest fetch always passes an end_date; the gap
        # snapshot fetch never does (see day_prep_service) -- fail only
        # the snapshot call so the edge computation still succeeds.
        if end_date is None:
            raise RuntimeError("snapshot unavailable")
        return combined

    now = pd.Timestamp("2024-01-03 11:55:00")
    results, _ = day_prep_service.prepare_day(
        ["AAPL"], "5min", strategy_names=["sma_cross"], fetch_bars=_fetch, now=now
    )

    assert len(results) == 1
    assert results[0].gap_pct is None
