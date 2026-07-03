"""
Column detection.

Real-world OHLCV CSVs use all kinds of header spellings ("Date",
"datetime", "Timestamp", "Vol", "Adj Close"...). This module maps
whatever's in the file to our standard column set
(timestamp, open, high, low, close, volume) so every downstream module
can assume those exact names.
"""

from dataclasses import dataclass, field

import pandas as pd

# Each standard column maps to a list of acceptable (lowercased) header aliases.
COLUMN_ALIASES: dict[str, list[str]] = {
    "timestamp": ["timestamp", "datetime", "date", "time", "date time"],
    "open": ["open", "o"],
    "high": ["high", "h"],
    "low": ["low", "l"],
    "close": ["close", "c", "adj close", "adjusted close"],
    "volume": ["volume", "vol", "v"],
}

REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


@dataclass(frozen=True)
class ColumnDetectionResult:
    mapping: dict[str, str]  # standard_name -> original_column_name
    unmatched_required: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.unmatched_required


def detect_columns(df: pd.DataFrame) -> ColumnDetectionResult:
    """Detect which raw columns correspond to each required OHLCV field."""
    normalized_lookup = {col.strip().lower(): col for col in df.columns}

    mapping: dict[str, str] = {}
    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized_lookup:
                mapping[standard_name] = normalized_lookup[alias]
                break

    unmatched = [col for col in REQUIRED_COLUMNS if col not in mapping]
    return ColumnDetectionResult(mapping=mapping, unmatched_required=unmatched)
