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

from app.domain.interfaces.strategy import Trade, TradeDirection
from app.services import signal_service
from app.strategies.execution import ExecutionConfig
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
    assert result.position == "long"


def test_check_signal_symbol_is_uppercased():
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    result = signal_service.check_signal("aapl", "5min", "sma_cross", {}, fetch_bars=fetch_bars)
    assert result.symbol == "AAPL"


def test_check_signal_unknown_strategy_raises():
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    with pytest.raises(KeyError):
        signal_service.check_signal("AAPL", "5min", "not_a_real_strategy", {}, fetch_bars=fetch_bars)


# --- execution_config wiring --------------------------------------------


def test_check_signal_passes_execution_config_through_to_strategy(monkeypatch):
    """The Live Signal tab / a watch's snapshotted settings (stop loss,
    direction filter, etc.) should reach the strategy's execution
    engine unchanged -- except force_close_at_session_end, which is
    always forced off for a live check (see check_signal's docstring)
    regardless of what the caller passed."""
    captured = {}

    class _FakeStrategy:
        def validate_params(self, params):
            return params

        def run(self, df, params, config):
            captured["config"] = config
            return []

    monkeypatch.setattr(signal_service, "get_strategy", lambda name: _FakeStrategy())
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")
    config = ExecutionConfig(
        capital=2500.0, direction_filter="short_only", stop_loss_atr_multiple=1.5, force_close_at_session_end=True
    )

    signal_service.check_signal("AAPL", "5min", "sma_cross", {}, fetch_bars=fetch_bars, execution_config=config)

    result_config = captured["config"]
    assert result_config.capital == 2500.0
    assert result_config.direction_filter == "short_only"
    assert result_config.stop_loss_atr_multiple == 1.5
    assert result_config.force_close_at_session_end is False  # always overridden


def test_check_signal_defaults_execution_config_when_none_given(monkeypatch):
    captured = {}

    class _FakeStrategy:
        def validate_params(self, params):
            return params

        def run(self, df, params, config):
            captured["config"] = config
            return []

    monkeypatch.setattr(signal_service, "get_strategy", lambda name: _FakeStrategy())
    fetch_bars = _fetch_bars_up_to("2024-01-02 11:20:00")

    signal_service.check_signal("AAPL", "5min", "sma_cross", {}, fetch_bars=fetch_bars)

    assert captured["config"] == ExecutionConfig(force_close_at_session_end=False)


# --- event_for_bar -- shared by check_signal and live_signal_engine ----


def _trade(entry_time, exit_time=None, direction=TradeDirection.LONG, exit_reason=None):
    return Trade(
        entry_time=entry_time,
        exit_time=exit_time,
        direction=direction,
        entry_price=100.0,
        exit_price=101.0 if exit_time else None,
        quantity=1,
        exit_reason=exit_reason,
    )


def test_event_for_bar_no_trades_returns_no_event():
    assert signal_service.event_for_bar([], pd.Timestamp("2024-01-02 11:20")) == (None, None, None)


def test_event_for_bar_entry_on_last_bar():
    bar_time = pd.Timestamp("2024-01-02 11:20")
    trades = [_trade(entry_time=bar_time, direction=TradeDirection.SHORT)]

    event, direction, exit_reason = signal_service.event_for_bar(trades, bar_time)

    assert event == "entry"
    assert direction == "short"
    assert exit_reason is None


def test_event_for_bar_exit_on_last_bar():
    entry = pd.Timestamp("2024-01-02 10:00")
    exit_time = pd.Timestamp("2024-01-02 12:10")
    trades = [_trade(entry_time=entry, exit_time=exit_time, exit_reason="signal_exit")]

    event, direction, exit_reason = signal_service.event_for_bar(trades, exit_time)

    assert event == "exit"
    assert direction is None
    assert exit_reason == "signal_exit"


def test_event_for_bar_ignores_artificial_end_of_data_exit():
    entry = pd.Timestamp("2024-01-02 10:00")
    exit_time = pd.Timestamp("2024-01-02 12:10")
    trades = [_trade(entry_time=entry, exit_time=exit_time, exit_reason="end_of_data")]

    assert signal_service.event_for_bar(trades, exit_time) == (None, None, None)


def test_event_for_bar_neither_entry_nor_exit_on_bar_returns_no_event():
    trades = [_trade(entry_time=pd.Timestamp("2024-01-02 10:00"), exit_time=pd.Timestamp("2024-01-02 10:30"))]

    assert signal_service.event_for_bar(trades, pd.Timestamp("2024-01-02 11:00")) == (None, None, None)


# --- todays_events -- full-day signal timeline for the Live Signal tab --


def test_todays_events_includes_entries_and_exits_on_the_session_date():
    trades = [
        _trade(
            entry_time=pd.Timestamp("2024-01-02 10:00"),
            exit_time=pd.Timestamp("2024-01-02 10:30"),
            direction=TradeDirection.LONG,
            exit_reason="signal_exit",
        ),
        _trade(entry_time=pd.Timestamp("2024-01-02 11:20"), direction=TradeDirection.SHORT),
    ]

    events = signal_service.todays_events(trades, pd.Timestamp("2024-01-02").date())

    assert events == [
        {"time": pd.Timestamp("2024-01-02 10:00"), "event": "entry", "direction": "long", "exit_reason": None},
        {"time": pd.Timestamp("2024-01-02 10:30"), "event": "exit", "direction": None, "exit_reason": "signal_exit"},
        {"time": pd.Timestamp("2024-01-02 11:20"), "event": "entry", "direction": "short", "exit_reason": None},
    ]


def test_todays_events_excludes_other_days_and_artificial_exit():
    trades = [
        _trade(
            entry_time=pd.Timestamp("2024-01-01 10:00"),
            exit_time=pd.Timestamp("2024-01-01 10:30"),
            exit_reason="signal_exit",
        ),
        _trade(entry_time=pd.Timestamp("2024-01-02 10:00"), exit_time=pd.Timestamp("2024-01-02 10:30"), exit_reason="end_of_data"),
    ]

    events = signal_service.todays_events(trades, pd.Timestamp("2024-01-02").date())

    assert events == [
        {"time": pd.Timestamp("2024-01-02 10:00"), "event": "entry", "direction": "long", "exit_reason": None},
    ]


def test_todays_events_empty_when_no_trades():
    assert signal_service.todays_events([], pd.Timestamp("2024-01-02").date()) == []
