"""ATR > threshold (volatility filter)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("atr_above_threshold")
class ATRAboveThreshold(Filter):
    """Requires an atr_{period} column already computed (app.indicators.atr)."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="atr_above_threshold",
            display_name="ATR > Threshold",
            description="True where ATR exceeds a fixed volatility threshold.",
            category="volatility",
            default_params={"period": 14, "threshold": 0.5},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        p = self.validate_params(params)
        col = f"atr_{p['period']}"
        if col not in df.columns:
            raise KeyError(f"atr_above_threshold filter requires a '{col}' column.")
        return df[col] > p["threshold"]
