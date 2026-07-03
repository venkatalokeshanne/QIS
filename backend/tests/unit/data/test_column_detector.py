"""Tests for column detection against varied real-world header spellings."""

import pandas as pd

from app.data.column_detector import detect_columns


def test_detects_standard_lowercase_headers():
    df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    result = detect_columns(df)
    assert result.is_complete
    assert result.mapping["close"] == "close"


def test_detects_common_aliases():
    df = pd.DataFrame(columns=["Date", "O", "H", "L", "Adj Close", "Vol"])
    result = detect_columns(df)
    assert result.is_complete
    assert result.mapping["timestamp"] == "Date"
    assert result.mapping["close"] == "Adj Close"
    assert result.mapping["volume"] == "Vol"


def test_reports_missing_required_columns():
    df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])  # no volume
    result = detect_columns(df)
    assert not result.is_complete
    assert "volume" in result.unmatched_required


def test_case_and_whitespace_insensitive():
    df = pd.DataFrame(columns=[" DateTime ", "OPEN", "High", "low", "Close", "volume"])
    result = detect_columns(df)
    assert result.is_complete
