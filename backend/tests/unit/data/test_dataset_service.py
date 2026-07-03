"""
Integration tests for DatasetService, exercising the full
load -> detect -> normalize -> validate -> persist pipeline against
real SQLite + CSV storage in a temp directory.
"""

import pytest

from app.config.settings import settings
from app.core.exceptions import DataValidationError, NotFoundError
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService

VALID_CSV = (
    b"Date,Open,High,Low,Close,Volume\n"
    b"2024-01-02 09:30,100,101,99,100.5,500\n"
    b"2024-01-02 09:31,100.5,102,100,101.5,600\n"
    b"2024-01-02 09:32,101.5,103,101,102.5,700\n"
)


@pytest.fixture
def service(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    monkeypatch.setattr(settings, "dataset_storage_dir", tmp_path / "data" / "datasets")
    return DatasetService(repository=DatasetRepository())


def test_upload_valid_csv_succeeds(service):
    result = service.upload_dataset(VALID_CSV, name="Test Set", original_filename="test.csv")
    assert result.record.row_count == 3
    assert result.validation.is_valid


def test_upload_persists_dataset_retrievable_by_id(service):
    result = service.upload_dataset(VALID_CSV, name="Test Set", original_filename="test.csv")
    df = service.get_dataframe(result.record.id)
    assert len(df) == 3
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]


def test_upload_rejects_dataset_with_negative_prices(service):
    bad_csv = b"Date,Open,High,Low,Close,Volume\n2024-01-02 09:30,-1,101,99,100.5,500\n"
    with pytest.raises(DataValidationError):
        service.upload_dataset(bad_csv, name="Bad Set", original_filename="bad.csv")


def test_upload_rejects_csv_missing_required_columns(service):
    bad_csv = b"Date,Open\n2024-01-02 09:30,100\n"
    with pytest.raises(DataValidationError):
        service.upload_dataset(bad_csv, name="Bad Set", original_filename="bad.csv")


def test_list_datasets_returns_uploaded_sets(service):
    service.upload_dataset(VALID_CSV, name="Set A", original_filename="a.csv")
    service.upload_dataset(VALID_CSV, name="Set B", original_filename="b.csv")
    names = {d.name for d in service.list_datasets()}
    assert names == {"Set A", "Set B"}


def test_delete_dataset_removes_it(service):
    result = service.upload_dataset(VALID_CSV, name="Set A", original_filename="a.csv")
    service.delete_dataset(result.record.id)
    with pytest.raises(NotFoundError):
        service.get_metadata(result.record.id)


def test_get_unknown_dataset_raises_not_found(service):
    with pytest.raises(NotFoundError):
        service.get_dataframe("does-not-exist")


def test_preview_returns_limited_rows_as_dicts(service):
    result = service.upload_dataset(VALID_CSV, name="Set A", original_filename="a.csv")
    preview = service.preview(result.record.id, rows=2)
    assert len(preview) == 2
    assert "timestamp" in preview[0]
    assert "close" in preview[0]
