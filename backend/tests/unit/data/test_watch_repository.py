"""Tests for app.repositories.watch_repository (local SQLite mode)."""

import sqlite3

import pytest

from app.config.settings import settings
from app.core.exceptions import NotFoundError
from app.repositories.watch_repository import WatchRepository


@pytest.fixture
def repository(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    return WatchRepository()


def test_create_and_get_round_trips_all_fields(repository):
    record = repository.create(
        symbol="aapl",
        strategy_name="sma_cross",
        strategy_params={"fast_period": 3, "slow_period": 8},
        interval="5min",
        execution_settings={"capital": 5000.0, "direction_filter": "long_only", "stop_loss_atr_multiple": 2.0},
    )
    assert record.symbol == "AAPL"  # normalized upper-case, same as datasets/levels
    assert record.execution_settings == {
        "capital": 5000.0,
        "direction_filter": "long_only",
        "stop_loss_atr_multiple": 2.0,
    }
    assert record.last_notified_bar_time is None
    assert record.last_checked_at is None

    fetched = repository.get(record.id)
    assert fetched == record


def test_create_without_execution_settings_defaults_to_empty_dict(repository):
    record = repository.create("AAPL", "sma_cross", {}, "5min")
    assert record.execution_settings == {}


def test_get_missing_watch_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get("does-not-exist")


def test_list_all_returns_every_watch(repository):
    repository.create("AAPL", "sma_cross", {}, "5min")
    repository.create("MSFT", "sma_cross", {}, "15min")
    repository.create("TSLA", "sma_cross", {}, "1min")

    results = repository.list_all()
    assert {r.symbol for r in results} == {"AAPL", "MSFT", "TSLA"}


def test_mark_checked_without_notified_bar_time_only_updates_last_checked(repository):
    record = repository.create("AAPL", "sma_cross", {}, "5min")
    repository.mark_checked(record.id, "2024-01-02T10:00:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"
    assert fetched.last_notified_bar_time is None


def test_mark_checked_with_notified_bar_time_updates_both(repository):
    record = repository.create("AAPL", "sma_cross", {}, "5min")
    repository.mark_checked(record.id, "2024-01-02T10:00:00+00:00", notified_bar_time="2024-01-02T09:55:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"
    assert fetched.last_notified_bar_time == "2024-01-02T09:55:00+00:00"


def test_delete_removes_watch(repository):
    record = repository.create("AAPL", "sma_cross", {}, "5min")
    repository.delete(record.id)
    with pytest.raises(NotFoundError):
        repository.get(record.id)


def test_stale_expo_push_token_schema_is_migrated_away(tmp_path, monkeypatch):
    """Pre-Telegram installs have a `watches` table with an
    expo_push_token NOT NULL column -- opening the repository against
    that table must drop and recreate it rather than fail on the first
    insert (which has no value for that column)."""
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    db_path = tmp_path / "data" / "app.db"
    monkeypatch.setattr(settings, "db_path", db_path)
    settings.ensure_dirs()

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE watches (
            id TEXT PRIMARY KEY,
            expo_push_token TEXT NOT NULL,
            symbol TEXT NOT NULL,
            strategy_name TEXT NOT NULL,
            strategy_params TEXT NOT NULL,
            interval TEXT NOT NULL,
            last_notified_bar_time TEXT,
            last_checked_at TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    repository = WatchRepository()
    record = repository.create("AAPL", "sma_cross", {}, "5min")
    assert repository.get(record.id) == record
