"""Tests for OHLCV validation rules."""

import pandas as pd

from app.data.validator import validate_ohlcv


def _df(rows: list[dict]) -> pd.DataFrame:
    idx = pd.date_range("2024-01-02 09:30", periods=len(rows), freq="1min")
    return pd.DataFrame(rows, index=idx)


def test_valid_dataset_passes():
    rows = [{"open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 500}] * 40
    report = validate_ohlcv(_df(rows))
    assert report.is_valid


def test_empty_dataset_is_invalid():
    report = validate_ohlcv(pd.DataFrame(columns=["open", "high", "low", "close", "volume"]))
    assert not report.is_valid


def test_negative_price_is_error():
    rows = [{"open": -1, "high": 101, "low": 99, "close": 100.5, "volume": 500}] * 30
    report = validate_ohlcv(_df(rows))
    assert not report.is_valid
    assert any("negative" in e for e in report.errors)


def test_high_less_than_low_is_error():
    rows = [{"open": 100, "high": 90, "low": 99, "close": 95, "volume": 500}] * 30
    report = validate_ohlcv(_df(rows))
    assert not report.is_valid


def test_negative_volume_is_error():
    rows = [{"open": 100, "high": 101, "low": 99, "close": 100.5, "volume": -5}] * 30
    report = validate_ohlcv(_df(rows))
    assert not report.is_valid


def test_short_dataset_produces_warning_not_error():
    rows = [{"open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 500}] * 5
    report = validate_ohlcv(_df(rows))
    assert report.is_valid
    assert any("fewer than 30" in w for w in report.warnings)
