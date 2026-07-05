"""Tests for app.repositories.watch_repository (local SQLite mode)."""

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
        expo_push_token="ExponentPushToken[abc123]",
        symbol="aapl",
        strategy_name="sma_cross",
        strategy_params={"fast_period": 3, "slow_period": 8},
        interval="5min",
    )
    assert record.symbol == "AAPL"  # normalized upper-case, same as datasets/levels
    assert record.last_notified_bar_time is None
    assert record.last_checked_at is None

    fetched = repository.get(record.id)
    assert fetched == record


def test_get_missing_watch_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get("does-not-exist")


def test_list_for_token_only_returns_matching_token(repository):
    repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    repository.create("token-a", "MSFT", "sma_cross", {}, "15min")
    repository.create("token-b", "TSLA", "sma_cross", {}, "1min")

    results = repository.list_for_token("token-a")
    assert {r.symbol for r in results} == {"AAPL", "MSFT"}


def test_mark_checked_without_notified_bar_time_only_updates_last_checked(repository):
    record = repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    repository.mark_checked(record.id, "2024-01-02T10:00:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"
    assert fetched.last_notified_bar_time is None


def test_mark_checked_with_notified_bar_time_updates_both(repository):
    record = repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    repository.mark_checked(record.id, "2024-01-02T10:00:00+00:00", notified_bar_time="2024-01-02T09:55:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"
    assert fetched.last_notified_bar_time == "2024-01-02T09:55:00+00:00"


def test_delete_removes_watch(repository):
    record = repository.create("token-a", "AAPL", "sma_cross", {}, "5min")
    repository.delete(record.id)
    with pytest.raises(NotFoundError):
        repository.get(record.id)
