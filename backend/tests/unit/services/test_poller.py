"""
Tests for app.services.poller -- the per-watch due-check cadence,
market-hours gating, and notify-once-per-bar dedupe logic. Uses a
temp-SQLite WatchRepository (like test_watch_repository.py) plus
monkeypatched signal_service.check_signal / notification_service.send_
so no real Twelve Data / Expo network calls happen.
"""

from datetime import datetime, timezone

import pytest

from app.config.settings import settings
from app.repositories.watch_repository import WatchRepository
from app.services import notification_service, poller, signal_service


@pytest.fixture
def repository(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    return WatchRepository()


@pytest.fixture
def sent_notifications(monkeypatch):
    sent = []
    monkeypatch.setattr(
        notification_service,
        "send_push_notification",
        lambda token, title, body, data=None: sent.append((token, title, body, data)),
    )
    return sent


def _market_hours_tuesday() -> datetime:
    return datetime(2024, 1, 2, 15, 0, tzinfo=timezone.utc)  # 10:00 America/New_York


def _weekend() -> datetime:
    return datetime(2024, 1, 6, 15, 0, tzinfo=timezone.utc)  # a Saturday


def _fake_signal(event=None, direction=None, exit_reason=None, as_of="2024-01-02T10:00:00"):
    import pandas as pd

    return signal_service.SignalCheck(
        symbol="AAPL",
        interval="5min",
        strategy_name="sma_cross",
        as_of=pd.Timestamp(as_of),
        price=100.0,
        event=event,
        direction=direction,
        exit_reason=exit_reason,
    )


def test_tick_skips_all_watches_outside_market_hours(repository, sent_notifications, monkeypatch):
    repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    monkeypatch.setattr(poller, "_is_market_hours", lambda now: False)

    p = poller.Poller(repository=repository)
    p.tick()

    assert sent_notifications == []


def test_tick_sends_notification_on_new_entry_signal(repository, sent_notifications, monkeypatch):
    watch = repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    monkeypatch.setattr(poller, "_is_market_hours", lambda now: True)
    monkeypatch.setattr(
        signal_service, "check_signal", lambda *a, **k: _fake_signal(event="entry", direction="long")
    )

    p = poller.Poller(repository=repository)
    p.tick()

    assert len(sent_notifications) == 1
    token, title, body, data = sent_notifications[0]
    assert token == "token-a"
    assert "AAPL" in title
    assert data["event"] == "entry"

    updated = repository.get(watch.id)
    assert updated.last_notified_bar_time == "2024-01-02T10:00:00"
    assert updated.last_checked_at is not None


def test_tick_does_not_renotify_same_bar_twice(repository, sent_notifications, monkeypatch):
    repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    monkeypatch.setattr(poller, "_is_market_hours", lambda now: True)
    monkeypatch.setattr(
        signal_service, "check_signal", lambda *a, **k: _fake_signal(event="entry", direction="long")
    )

    p = poller.Poller(repository=repository)
    p.tick()
    p.tick()  # simulate a later check where nothing new has happened -- same bar, same signal state

    assert len(sent_notifications) == 1


def test_tick_skips_watch_not_yet_due_for_its_interval(repository, sent_notifications, monkeypatch):
    watch = repository.create("token-a", "AAPL", "sma_cross", {}, "15min")
    now = datetime.now(timezone.utc)
    repository.mark_checked(watch.id, now.isoformat())  # just checked -- 15min watch isn't due again yet

    monkeypatch.setattr(poller, "_is_market_hours", lambda now: True)
    monkeypatch.setattr(
        signal_service, "check_signal", lambda *a, **k: _fake_signal(event="entry", direction="long")
    )

    p = poller.Poller(repository=repository)
    p.tick()

    assert sent_notifications == []


def test_tick_no_event_updates_last_checked_without_notifying(repository, sent_notifications, monkeypatch):
    watch = repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    monkeypatch.setattr(poller, "_is_market_hours", lambda now: True)
    monkeypatch.setattr(signal_service, "check_signal", lambda *a, **k: _fake_signal(event=None))

    p = poller.Poller(repository=repository)
    p.tick()

    assert sent_notifications == []
    updated = repository.get(watch.id)
    assert updated.last_checked_at is not None
    assert updated.last_notified_bar_time is None


def test_tick_continues_past_a_watch_whose_signal_check_raises(repository, sent_notifications, monkeypatch):
    repository.create("token-a", "BADSYM", "sma_cross", {}, "5min")
    good_watch = repository.create("token-b", "AAPL", "sma_cross", {}, "5min")
    monkeypatch.setattr(poller, "_is_market_hours", lambda now: True)

    def _check_signal(symbol, *a, **k):
        if symbol == "BADSYM":
            raise RuntimeError("Twelve Data blew up")
        return _fake_signal(event="entry", direction="long")

    monkeypatch.setattr(signal_service, "check_signal", _check_signal)

    p = poller.Poller(repository=repository)
    p.tick()  # must not raise, and must still process the other watch

    assert len(sent_notifications) == 1
    assert sent_notifications[0][0] == "token-b"


def test_is_market_hours_true_during_session():
    assert poller._is_market_hours(_market_hours_tuesday())


def test_is_market_hours_false_on_weekend():
    assert not poller._is_market_hours(_weekend())
