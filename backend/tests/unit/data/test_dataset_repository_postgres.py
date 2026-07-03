"""
Tests for DatasetRepository's Postgres-backed path (see its module
docstring). Skipped unless a real DATABASE_URL is set in the test
environment -- these need a live Postgres to talk to, so they are NOT
part of the normal hermetic test suite.

Run against a real (throwaway/test, not production) database once you
have one, e.g.:
    DATABASE_URL=postgresql://... pytest tests/unit/data/test_dataset_repository_postgres.py

Each test's fixture wipes the `datasets` table clean afterward, so
don't point this at a database holding real data you care about.
"""

import os

import pandas as pd
import pytest

from app.config.settings import settings
from app.core.exceptions import NotFoundError
from app.repositories.dataset_repository import DatasetRepository

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"), reason="requires a live DATABASE_URL to test the Postgres path"
)


def _sample_df():
    idx = pd.to_datetime(["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-02 09:32"])
    idx.name = "timestamp"
    return pd.DataFrame(
        {
            "open": [100.0, 100.5, 101.5],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [500, 600, 700],
        },
        index=idx,
    )


@pytest.fixture
def repo(monkeypatch):
    monkeypatch.setattr(settings, "database_url", os.environ["DATABASE_URL"])
    r = DatasetRepository()
    yield r
    for record in r.list_all():
        r.delete(record.id)


def test_save_and_get_dataframe_roundtrip(repo):
    record = repo.save(_sample_df(), name="PG Test", original_filename="pg.csv")
    df = repo.get_dataframe(record.id)
    assert len(df) == 3
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]


def test_get_metadata_returns_saved_record(repo):
    record = repo.save(_sample_df(), name="PG Test", original_filename="pg.csv")
    fetched = repo.get_metadata(record.id)
    assert fetched.name == "PG Test"
    assert fetched.row_count == 3


def test_list_all_includes_saved_datasets(repo):
    repo.save(_sample_df(), name="PG A", original_filename="a.csv")
    repo.save(_sample_df(), name="PG B", original_filename="b.csv")
    names = {r.name for r in repo.list_all()}
    assert {"PG A", "PG B"}.issubset(names)


def test_delete_removes_dataset(repo):
    record = repo.save(_sample_df(), name="PG Test", original_filename="pg.csv")
    repo.delete(record.id)
    with pytest.raises(NotFoundError):
        repo.get_metadata(record.id)


def test_get_unknown_dataset_raises_not_found(repo):
    with pytest.raises(NotFoundError):
        repo.get_dataframe("does-not-exist")
