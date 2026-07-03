"""
Validation.

Runs on an already-normalized OHLCV DataFrame and produces a structured
report (errors block the upload, warnings don't). Kept separate from
normalization so the rules here can grow (e.g. session-gap checks)
without touching parsing logic.
"""

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_ohlcv(df: pd.DataFrame) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    if df.empty:
        errors.append("Dataset has no valid rows after parsing.")
        return ValidationReport(errors=errors, warnings=warnings)

    null_counts = df[["open", "high", "low", "close", "volume"]].isna().sum()
    for col, count in null_counts.items():
        if count > 0:
            warnings.append(f"{count} row(s) have a missing/unparseable '{col}' value.")

    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        errors.append("One or more price values are zero or negative.")

    if (df["volume"] < 0).any():
        errors.append("One or more volume values are negative.")

    if (df["high"] < df["low"]).any():
        errors.append("One or more rows have high < low.")

    bad_high = ((df["high"] < df["open"]) | (df["high"] < df["close"])).sum()
    if bad_high > 0:
        warnings.append(f"{bad_high} row(s) have a high lower than their open or close.")

    bad_low = ((df["low"] > df["open"]) | (df["low"] > df["close"])).sum()
    if bad_low > 0:
        warnings.append(f"{bad_low} row(s) have a low higher than their open or close.")

    if not df.index.is_monotonic_increasing:
        errors.append("Timestamps are not sorted in increasing order.")

    if len(df) < 30:
        warnings.append("Dataset has fewer than 30 rows — most indicators won't have enough history.")

    return ValidationReport(errors=errors, warnings=warnings)
