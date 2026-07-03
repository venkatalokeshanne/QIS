"""Tests for OHLCV normalization."""

import pandas as pd
import pytest

from app.core.exceptions import DataValidationError
from app.data.column_detector import detect_columns
from app.data.normalizer import normalize_ohlcv


def test_normalize_produces_standard_columns_and_sorted_index():
    raw = pd.DataFrame(
        {
            "Date": ["2024-01-02 09:31", "2024-01-02 09:30"],
            "Open": [101, 100],
            "High": [102, 101],
            "Low": [100, 99],
            "Close": [101.5, 100.5],
            "Vol": [500, 600],
        }
    )
    detection = detect_columns(raw)
    out = normalize_ohlcv(raw, detection)

    assert list(out.columns) == ["open", "high", "low", "close", "volume"]
    assert out.index.is_monotonic_increasing
    assert out.index.name == "timestamp"


def test_normalize_drops_unparseable_timestamp_rows():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-02 09:30", "not-a-date"],
            "open": [100, 100],
            "high": [101, 101],
            "low": [99, 99],
            "close": [100.5, 100.5],
            "volume": [500, 500],
        }
    )
    detection = detect_columns(raw)
    out = normalize_ohlcv(raw, detection)
    assert len(out) == 1


def test_normalize_deduplicates_timestamps_keeping_first():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-02 09:30", "2024-01-02 09:30"],
            "open": [100, 999],
            "high": [101, 999],
            "low": [99, 999],
            "close": [100.5, 999],
            "volume": [500, 999],
        }
    )
    detection = detect_columns(raw)
    out = normalize_ohlcv(raw, detection)
    assert len(out) == 1
    assert out.iloc[0]["open"] == 100


def test_normalize_raises_on_missing_columns():
    raw = pd.DataFrame({"timestamp": ["2024-01-02 09:30"], "open": [100]})
    detection = detect_columns(raw)
    with pytest.raises(DataValidationError):
        normalize_ohlcv(raw, detection)
