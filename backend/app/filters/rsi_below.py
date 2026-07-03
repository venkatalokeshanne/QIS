"""RSI < threshold (e.g. RSI < 30, oversold)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("rsi_below")
class RSIBelow(Filter):
    """Requires an rsi_{period} column already computed (app.indicators.rsi)."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="rsi_below",
            display_name="RSI Below Threshold",
            description="True where RSI is below the given threshold (e.g. oversold < 30).",
            category="momentum",
            default_params={"period": 14, "threshold": 30},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        p = self.validate_params(params)
        col = f"rsi_{p['period']}"
        if col not in df.columns:
            raise KeyError(f"rsi_below filter requires a '{col}' column.")
        return df[col] < p["threshold"]
