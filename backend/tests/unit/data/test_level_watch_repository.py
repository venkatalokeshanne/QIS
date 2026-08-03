"""Tests for app.repositories.level_watch_repository (local SQLite mode)."""

import pytest

from app.config.settings import settings
from app.core.exceptions import DataValidationError, NotFoundError
from app.repositories.level_watch_repository import LevelWatchRepository


@pytest.fixture
def repository(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    return LevelWatchRepository()


def test_create_and_get_round_trips_all_fields(repository):
    record = repository.create("aapl")
    assert record.symbol == "AAPL"
    assert record.last_levels is None
    assert record.last_checked_at is None

    fetched = repository.get(record.id)
    assert fetched == record


def test_create_duplicate_symbol_raises_validation_error(repository):
    repository.create("AAPL")
    with pytest.raises(DataValidationError):
        repository.create("aapl")


def test_get_missing_level_watch_raises_not_found(repository):
    with pytest.raises(NotFoundError):
        repository.get("does-not-exist")


def test_list_all_returns_every_level_watch(repository):
    repository.create("AAPL")
    repository.create("MSFT")

    results = repository.list_all()
    assert {r.symbol for r in results} == {"AAPL", "MSFT"}


def test_update_levels_sets_levels_and_checked_at(repository):
    record = repository.create("AAPL")
    repository.update_levels(record.id, [100.0, 105.5], "2024-01-02T10:00:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_levels == [100.0, 105.5]
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"


def test_mark_checked_leaves_last_levels_unchanged(repository):
    record = repository.create("AAPL")
    repository.update_levels(record.id, [100.0], "2024-01-01T00:00:00+00:00")
    repository.mark_checked(record.id, "2024-01-02T10:00:00+00:00")

    fetched = repository.get(record.id)
    assert fetched.last_levels == [100.0]
    assert fetched.last_checked_at == "2024-01-02T10:00:00+00:00"


def test_delete_removes_level_watch(repository):
    record = repository.create("AAPL")
    repository.delete(record.id)
    with pytest.raises(NotFoundError):
        repository.get(record.id)
