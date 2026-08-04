"""
Tests for app.services.live_signal_engine -- the pure candle-parsing/
merging helpers, subscription bookkeeping, and the notify/dedup logic,
all exercised WITHOUT a real WebSocket (no live Tastytrade/Telegram
network calls). Async methods are awaited directly via asyncio.run()
since this project has no pytest-asyncio dependency.
"""

import asyncio
from datetime import datetime, timezone

import pandas as pd
import pytest

from app.config.settings import settings
from app.repositories.watch_repository import WatchRecord, WatchRepository
from app.services import live_signal_engine as lse
from app.services import notification_service, poller
from app.strategies.registry import discover_strategies


@pytest.fixture(autouse=True)
def _ensure_strategies_registered():
    discover_strategies()


@pytest.fixture
def repository(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    return WatchRepository()


@pytest.fixture
def engine(repository):
    return lse.LiveSignalEngine(repository=repository)


@pytest.fixture
def sent_messages(monkeypatch):
    sent = []
    monkeypatch.setattr(notification_service, "send_telegram_message", lambda text: sent.append(text))
    return sent


def _historical_df(periods=30) -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:30", periods=periods, freq="5min")
    return pd.DataFrame(
        {"open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 500.0}, index=idx
    )


def _candle_event(symbol_compound: str, time_ms: int, close: float) -> dict:
    return {
        "eventType": "Candle",
        "eventSymbol": symbol_compound,
        "time": time_ms,
        "open": close,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": 500,
    }


# --- parse_live_candle / merge_live_candle (pure) -----------------------


def test_parse_live_candle_extracts_ny_naive_timestamp_and_ohlcv():
    # 2024-01-02 14:35:00 UTC == 2024-01-02 09:35:00 America/New_York (EST, UTC-5)
    event = _candle_event("AAPL{=5m,tho=true}", int(pd.Timestamp("2024-01-02 14:35:00", tz="UTC").timestamp() * 1000), 101.25)

    bar_time, ohlcv = lse.parse_live_candle(event)

    assert bar_time == pd.Timestamp("2024-01-02 09:35:00")
    assert ohlcv == {"open": 101.25, "high": 101.75, "low": 100.75, "close": 101.25, "volume": 500.0}


def test_merge_live_candle_updates_same_still_forming_bar_in_place():
    df = _historical_df()
    last_bar_time = df.index[-1]

    merged = lse.merge_live_candle(df, last_bar_time, {"open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 999})

    assert len(merged) == len(df)  # no new row -- same bar updated
    assert merged.loc[last_bar_time, "close"] == 1.5
    assert merged.loc[last_bar_time, "volume"] == 999


def test_merge_live_candle_appends_new_row_when_bar_rolls_over():
    df = _historical_df()
    new_bar_time = df.index[-1] + pd.Timedelta(minutes=5)

    merged = lse.merge_live_candle(df, new_bar_time, {"open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 999})

    assert len(merged) == len(df) + 1
    assert merged.index[-1] == new_bar_time
    assert merged.loc[new_bar_time, "close"] == 1.5


def test_merge_live_candle_trims_to_max_cached_bars(monkeypatch):
    monkeypatch.setattr(lse, "_MAX_CACHED_BARS", 10)
    df = _historical_df(periods=10)
    new_bar_time = df.index[-1] + pd.Timedelta(minutes=5)

    merged = lse.merge_live_candle(df, new_bar_time, {"open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 999})

    assert len(merged) == 10
    assert merged.index[-1] == new_bar_time
    assert merged.index[0] == df.index[1]  # oldest row dropped


def test_merge_live_candle_never_mutates_input():
    df = _historical_df()
    original_close = df["close"].iloc[-1]

    lse.merge_live_candle(df, df.index[-1], {"open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 999})

    assert df["close"].iloc[-1] == original_close


# --- subscription bookkeeping --------------------------------------------


def test_ensure_subscribed_populates_pair_and_symbol_map(engine, monkeypatch):
    monkeypatch.setattr(lse.signal_service, "fetch_symbol_bars", lambda symbol, interval, **kwargs: _historical_df())

    asyncio.run(engine._ensure_subscribed("AAPL", "5min"))

    assert ("AAPL", "5min") in engine._pairs
    assert "AAPL{=5m,tho=false}" in engine._symbol_to_pair
    assert engine._symbol_to_pair["AAPL{=5m,tho=false}"] == ("AAPL", "5min")


def test_ensure_subscribed_is_idempotent_for_same_pair(engine, monkeypatch):
    calls = []
    monkeypatch.setattr(
        lse.signal_service,
        "fetch_symbol_bars",
        lambda symbol, interval, **kwargs: (calls.append(1), _historical_df())[1],
    )

    asyncio.run(engine._ensure_subscribed("AAPL", "5min"))
    asyncio.run(engine._ensure_subscribed("AAPL", "5min"))

    assert len(calls) == 1  # second call is a no-op, no redundant fetch


def test_ensure_subscribed_swallows_fetch_failure(engine, monkeypatch):
    def _raise(symbol, interval, **kwargs):
        raise RuntimeError("Tastytrade blew up")

    monkeypatch.setattr(lse.signal_service, "fetch_symbol_bars", _raise)

    asyncio.run(engine._ensure_subscribed("BADSYM", "5min"))  # must not raise

    assert ("BADSYM", "5min") not in engine._pairs


def test_maybe_unsubscribe_removes_pair_when_no_watch_needs_it(engine, monkeypatch):
    monkeypatch.setattr(lse.signal_service, "fetch_symbol_bars", lambda symbol, interval, **kwargs: _historical_df())
    asyncio.run(engine._ensure_subscribed("AAPL", "5min"))

    asyncio.run(engine._maybe_unsubscribe("AAPL", "5min"))

    assert ("AAPL", "5min") not in engine._pairs
    assert "AAPL{=5m,tho=false}" not in engine._symbol_to_pair


def test_maybe_unsubscribe_keeps_pair_when_another_watch_still_needs_it(engine, repository, monkeypatch):
    monkeypatch.setattr(lse.signal_service, "fetch_symbol_bars", lambda symbol, interval, **kwargs: _historical_df())
    asyncio.run(engine._ensure_subscribed("AAPL", "5min"))
    repository.create("AAPL", "sma_cross", {}, "5min")  # still-active watch on this pair

    asyncio.run(engine._maybe_unsubscribe("AAPL", "5min"))

    assert ("AAPL", "5min") in engine._pairs


# --- notify / dedup logic -------------------------------------------------


def test_evaluate_pair_notifies_on_new_event_and_dedupes_same_bar(engine, repository, sent_messages, monkeypatch):
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    watch = repository.create("AAPL", "sma_cross", {}, "5min")
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    monkeypatch.setattr(
        lse.LiveSignalEngine, "_run_strategy", staticmethod(lambda watch, df, bar_time: ("entry", "long", None, []))
    )

    bar_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    event = _candle_event("AAPL{=5m,tho=true}", bar_ms, 101.0)

    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), event))
    assert len(sent_messages) == 1
    assert "AAPL" in sent_messages[0]
    updated = repository.get(watch.id)
    assert updated.last_notified_bar_time is not None

    # Same candle time again (e.g. dxfeed re-sends the still-forming bar) -- no re-notify.
    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), event))
    assert len(sent_messages) == 1


def test_evaluate_pair_notifies_again_on_a_new_bar(engine, repository, sent_messages, monkeypatch):
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    repository.create("AAPL", "sma_cross", {}, "5min")
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    monkeypatch.setattr(
        lse.LiveSignalEngine, "_run_strategy", staticmethod(lambda watch, df, bar_time: ("entry", "long", None, []))
    )

    first_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    second_ms = int(pd.Timestamp("2024-01-02 09:40:00", tz="America/New_York").timestamp() * 1000)

    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), _candle_event("AAPL{=5m,tho=true}", first_ms, 101.0)))
    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), _candle_event("AAPL{=5m,tho=true}", second_ms, 102.0)))

    assert len(sent_messages) == 2


def test_evaluate_pair_no_event_does_not_notify(engine, repository, sent_messages, monkeypatch):
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    repository.create("AAPL", "sma_cross", {}, "5min")
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    monkeypatch.setattr(
        lse.LiveSignalEngine, "_run_strategy", staticmethod(lambda watch, df, bar_time: (None, None, None, []))
    )

    bar_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), _candle_event("AAPL{=5m,tho=true}", bar_ms, 101.0)))

    assert sent_messages == []


def test_evaluate_pair_skips_outside_market_hours(engine, repository, sent_messages, monkeypatch):
    monkeypatch.setattr(poller, "is_market_hours", lambda now: False)
    repository.create("AAPL", "sma_cross", {}, "5min")
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    monkeypatch.setattr(
        lse.LiveSignalEngine, "_run_strategy", staticmethod(lambda watch, df, bar_time: ("entry", "long", None, []))
    )

    bar_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    asyncio.run(engine._evaluate_pair(("AAPL", "5min"), _candle_event("AAPL{=5m,tho=true}", bar_ms, 101.0)))

    assert sent_messages == []


def test_evaluate_watch_continues_when_strategy_raises(engine, repository, sent_messages, monkeypatch):
    repository.create("AAPL", "sma_cross", {}, "5min")

    def _raise(watch, df, bar_time):
        raise RuntimeError("boom")

    monkeypatch.setattr(lse.LiveSignalEngine, "_run_strategy", staticmethod(_raise))

    watch = repository.list_all()[0]
    asyncio.run(engine._evaluate_watch(watch, _historical_df(), _historical_df().index[-1]))  # must not raise
    assert sent_messages == []


# --- execution_settings wiring -------------------------------------------


def _watch(execution_settings):
    return WatchRecord(
        id="w1",
        symbol="AAPL",
        strategy_name="sma_cross",
        strategy_params={},
        interval="5min",
        execution_settings=execution_settings,
        last_notified_bar_time=None,
        last_checked_at=None,
        created_at="2024-01-01T00:00:00+00:00",
    )


def test_run_strategy_builds_execution_config_from_watch_settings(monkeypatch):
    captured = {}

    class _FakeStrategy:
        def validate_params(self, params):
            return params

        def run(self, df, params, config):
            captured["config"] = config
            return []

    monkeypatch.setattr(lse, "get_strategy", lambda name: _FakeStrategy())
    watch = _watch({"direction_filter": "short_only", "capital": 2000.0, "force_close_at_session_end": True})

    lse.LiveSignalEngine._run_strategy(watch, _historical_df(), _historical_df().index[-1])

    config = captured["config"]
    assert config.direction_filter == "short_only"
    assert config.capital == 2000.0
    assert config.force_close_at_session_end is False  # always overridden, regardless of the stored value


def test_run_strategy_falls_back_to_bare_defaults_when_no_execution_settings_stored(monkeypatch):
    """Watches created before execution-settings snapshotting existed
    have an empty execution_settings dict -- must not crash, and should
    behave like the old bare-defaults LIVE_EXECUTION_CONFIG."""
    captured = {}

    class _FakeStrategy:
        def validate_params(self, params):
            return params

        def run(self, df, params, config):
            captured["config"] = config
            return []

    monkeypatch.setattr(lse, "get_strategy", lambda name: _FakeStrategy())
    watch = _watch({})

    lse.LiveSignalEngine._run_strategy(watch, _historical_df(), _historical_df().index[-1])

    from app.strategies.execution import ExecutionConfig

    assert captured["config"] == ExecutionConfig(force_close_at_session_end=False)


# --- throttling ------------------------------------------------------------


async def _run_handle_candle_event_test(engine, events, monkeypatch):
    """Runs _handle_candle_event inside a real event loop (so its own
    asyncio.create_task call works normally) with _evaluate_pair
    stubbed out to a fast no-op that just records how many times it was
    scheduled -- isolates the throttle/routing decision in
    _handle_candle_event from the notify logic already covered above."""
    scheduled = []

    async def _fake_evaluate_pair(pair, event):
        scheduled.append((pair, event))

    monkeypatch.setattr(engine, "_evaluate_pair", _fake_evaluate_pair)
    for event in events:
        engine._handle_candle_event(event)
    await asyncio.sleep(0)  # let scheduled tasks run
    return scheduled


def test_handle_candle_event_throttles_rapid_updates_for_same_pair(engine, monkeypatch):
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    engine._symbol_to_pair["AAPL{=5m,tho=true}"] = ("AAPL", "5min")

    bar_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    event = _candle_event("AAPL{=5m,tho=true}", bar_ms, 101.0)

    scheduled = asyncio.run(_run_handle_candle_event_test(engine, [event, event], monkeypatch))

    assert len(scheduled) == 1  # second, immediate call is throttled


def test_handle_candle_event_ignores_unsubscribed_symbol(engine, monkeypatch):
    bar_ms = int(pd.Timestamp("2024-01-02 09:35:00", tz="America/New_York").timestamp() * 1000)
    event = _candle_event("MSFT{=5m,tho=true}", bar_ms, 101.0)  # never subscribed

    scheduled = asyncio.run(_run_handle_candle_event_test(engine, [event], monkeypatch))

    assert scheduled == []


def test_handle_candle_event_ignores_nan_placeholder_candle(engine, monkeypatch):
    engine._pairs[("AAPL", "5min")] = lse._PairState(_historical_df())
    engine._symbol_to_pair["AAPL{=5m,tho=true}"] = ("AAPL", "5min")

    event = {"eventType": "Candle", "eventSymbol": "AAPL{=5m,tho=true}", "time": 123, "open": "NaN"}

    scheduled = asyncio.run(_run_handle_candle_event_test(engine, [event], monkeypatch))

    assert scheduled == []
