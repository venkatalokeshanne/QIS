"""
Normalization.

Given a raw DataFrame and a column mapping (from column_detector), this
produces the canonical shape every Indicator/Filter/Strategy expects:
lowercase open/high/low/close/volume columns, a sorted, deduplicated
DatetimeIndex named 'timestamp'.
"""

import pandas as pd

from app.core.exceptions import DataValidationError
from app.data.column_detector import ColumnDetectionResult


def normalize_ohlcv(df: pd.DataFrame, detection: ColumnDetectionResult) -> pd.DataFrame:
    if not detection.is_complete:
        raise DataValidationError(
            "Missing required columns.",
            issues=[f"Could not find a column for '{col}'." for col in detection.unmatched_required],
        )

    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df[detection.mapping["timestamp"]], errors="coerce"),
            "open": pd.to_numeric(df[detection.mapping["open"]], errors="coerce"),
            "high": pd.to_numeric(df[detection.mapping["high"]], errors="coerce"),
            "low": pd.to_numeric(df[detection.mapping["low"]], errors="coerce"),
            "close": pd.to_numeric(df[detection.mapping["close"]], errors="coerce"),
            "volume": pd.to_numeric(df[detection.mapping["volume"]], errors="coerce"),
        }
    )

    out = out.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()
    out = out[~out.index.duplicated(keep="first")]
    return out
