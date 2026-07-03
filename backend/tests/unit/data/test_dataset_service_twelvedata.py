"""
Tests for DatasetService.import_from_twelvedata, mocking the Twelve
Data client call entirely so these run without a real network call.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from app.config.settings import settings
from app.core.exceptions import DataValidationError
from app.repositories.dataset_repository import DatasetRepository
from app.services.dataset_service import DatasetService


def _fake_bars_df() -> pd.DataFrame:
    # Mirrors the shape twelvedata_client.fetch_historical_bars returns:
    # a "date" column plus lowercase open/high/low/close/volume -- already
    # compatible with column_detector's aliases, no special-casing needed.
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02 09:30", "2024-01-02 09:31", "2024-01-02 09:32"]),
            "open": [100.0, 100.5, 101.5],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [500, 600, 700],
        }
    )


@pytest.fixture
def service(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    monkeypatch.setattr(settings, "db_path", tmp_path / "data" / "app.db")
    monkeypatch.setattr(settings, "dataset_storage_dir", tmp_path / "data" / "datasets")
    return DatasetService(repository=DatasetRepository())


def test_import_from_twelvedata_persists_dataset(service):
    result = service.import_from_twelvedata("AAPL", fetch_bars=lambda *a, **kw: _fake_bars_df())
    assert result.record.row_count == 3
    assert result.record.original_filename == "TwelveData:AAPL"
    assert result.validation.is_valid


def test_import_from_twelvedata_defaults_name_to_symbol(service):
    result = service.import_from_twelvedata("MSFT", fetch_bars=lambda *a, **kw: _fake_bars_df())
    assert result.record.name == "MSFT"


def test_import_from_twelvedata_uses_given_name(service):
    result = service.import_from_twelvedata(
        "MSFT", name="My Microsoft Set", fetch_bars=lambda *a, **kw: _fake_bars_df()
    )
    assert result.record.name == "My Microsoft Set"


def test_import_from_twelvedata_passes_through_fetch_params(service):
    captured = {}

    def fake_fetch(symbol, **kwargs):
        captured["symbol"] = symbol
        captured.update(kwargs)
        return _fake_bars_df()

    service.import_from_twelvedata(
        "TSLA", interval="5min", outputsize=100, start_date="2024-01-01", fetch_bars=fake_fetch
    )
    assert captured["symbol"] == "TSLA"
    assert captured["interval"] == "5min"
    assert captured["outputsize"] == 100
    assert captured["start_date"] == "2024-01-01"


def test_import_from_twelvedata_translates_duration_to_start_date(service):
    captured = {}

    def fake_fetch(symbol, **kwargs):
        captured.update(kwargs)
        return _fake_bars_df()

    service.import_from_twelvedata("TSLA", duration="5D", fetch_bars=fake_fetch)

    expected = datetime.now(timezone.utc) - timedelta(days=5)
    got = datetime.strptime(captured["start_date"], "%Y-%m-%d")
    assert abs((got - expected.replace(tzinfo=None)).total_seconds()) < 86400  # within a day


def test_import_from_twelvedata_explicit_start_date_overrides_duration(service):
    captured = {}

    def fake_fetch(symbol, **kwargs):
        captured.update(kwargs)
        return _fake_bars_df()

    service.import_from_twelvedata("TSLA", duration="1Y", start_date="2024-01-01", fetch_bars=fake_fetch)

    assert captured["start_date"] == "2024-01-01"


def test_import_from_twelvedata_rejects_invalid_bars(service):
    bad_bars = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-02 09:30"]), "open": [-1], "high": [101], "low": [99], "close": [100], "volume": [500]}
    )
    with pytest.raises(DataValidationError):
        service.import_from_twelvedata("BAD", fetch_bars=lambda *a, **kw: bad_bars)
