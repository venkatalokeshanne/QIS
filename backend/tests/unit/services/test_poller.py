"""
Tests for app.services.poller -- market-hours gating and the
change-detection logic for level watches. Signal-watch alerting moved
to app.services.live_signal_engine (see test_live_signal_engine.py);
level watches have no per-timeframe live-bar concept, so they still
poll on a fixed cadence here. Uses a temp-SQLite LevelWatchRepository
(like test_level_watch_repository.py) plus monkeypatched
levels_service.get_daily_levels / notification_service.
send_telegram_message so no real Tastytrade / Telegram network calls
happen.
"""

from datetime import datetime, timezone

import pytest

from app.config.settings import settings
from app.repositories.level_watch_repository import LevelWatchRepository
from app.services import levels_service, notification_service, poller


@pytest.fixture
def level_watch_repository(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    return LevelWatchRepository()


@pytest.fixture
def sent_messages(monkeypatch):
    sent = []
    monkeypatch.setattr(notification_service, "send_telegram_message", lambda text: sent.append(text))
    return sent


def _market_hours_tuesday() -> datetime:
    return datetime(2024, 1, 2, 15, 0, tzinfo=timezone.utc)  # 10:00 America/New_York


def _weekend() -> datetime:
    return datetime(2024, 1, 6, 15, 0, tzinfo=timezone.utc)  # a Saturday


def test_is_market_hours_true_during_session():
    assert poller.is_market_hours(_market_hours_tuesday())


def test_is_market_hours_false_on_weekend():
    assert not poller.is_market_hours(_weekend())


def test_tick_skips_all_level_watches_outside_market_hours(level_watch_repository, sent_messages, monkeypatch):
    level_watch_repository.create("AAPL")
    monkeypatch.setattr(poller, "is_market_hours", lambda now: False)

    p = poller.Poller(level_watch_repository=level_watch_repository)
    p.tick()

    assert sent_messages == []


# --- Level watches ---------------------------------------------------


def _fake_levels(auto_support_resistance):
    class _Levels:
        pass

    levels = _Levels()
    levels.auto_support_resistance = auto_support_resistance
    return levels


def test_level_watch_notifies_on_first_check(level_watch_repository, sent_messages, monkeypatch):
    watch = level_watch_repository.create("AAPL")
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    monkeypatch.setattr(levels_service, "get_daily_levels", lambda symbol: _fake_levels([100.0, 105.5]))

    p = poller.Poller(level_watch_repository=level_watch_repository)
    p.tick()

    assert len(sent_messages) == 1
    assert "AAPL" in sent_messages[0]
    updated = level_watch_repository.get(watch.id)
    assert updated.last_levels == [100.0, 105.5]


def test_level_watch_notifies_when_levels_change(level_watch_repository, sent_messages, monkeypatch):
    watch = level_watch_repository.create("AAPL")
    level_watch_repository.update_levels(watch.id, [100.0, 105.5], "2024-01-01T00:00:00+00:00")
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    monkeypatch.setattr(levels_service, "get_daily_levels", lambda symbol: _fake_levels([101.0, 106.0]))

    p = poller.Poller(level_watch_repository=level_watch_repository)
    p.tick()

    assert len(sent_messages) == 1
    updated = level_watch_repository.get(watch.id)
    assert updated.last_levels == [101.0, 106.0]


def test_level_watch_does_not_notify_when_levels_unchanged(level_watch_repository, sent_messages, monkeypatch):
    watch = level_watch_repository.create("AAPL")
    level_watch_repository.update_levels(watch.id, [100.0, 105.5], "2024-01-01T00:00:00+00:00")
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)
    monkeypatch.setattr(levels_service, "get_daily_levels", lambda symbol: _fake_levels([100.001, 105.499]))

    p = poller.Poller(level_watch_repository=level_watch_repository)
    p.tick()

    assert sent_messages == []
    updated = level_watch_repository.get(watch.id)
    assert updated.last_levels == [100.0, 105.5]  # unchanged -- only last_checked_at bumped


def test_level_watch_continues_past_a_watch_whose_levels_check_raises(level_watch_repository, sent_messages, monkeypatch):
    level_watch_repository.create("BADSYM")
    level_watch_repository.create("AAPL")
    monkeypatch.setattr(poller, "is_market_hours", lambda now: True)

    def _get_daily_levels(symbol):
        if symbol == "BADSYM":
            raise RuntimeError("Tastytrade blew up")
        return _fake_levels([100.0])

    monkeypatch.setattr(levels_service, "get_daily_levels", _get_daily_levels)

    p = poller.Poller(level_watch_repository=level_watch_repository)
    p.tick()  # must not raise, and must still process the other level watch

    assert len(sent_messages) == 1
    assert "AAPL" in sent_messages[0]
