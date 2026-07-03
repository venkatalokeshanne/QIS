"""Price > VWAP."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("price_above_vwap")
class PriceAboveVWAP(Filter):
    """Requires a 'vwap' column already computed (app.indicators.vwap)."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="price_above_vwap",
            display_name="Price > VWAP",
            description="True where close price is above VWAP.",
            category="trend",
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        if "vwap" not in df.columns:
            raise KeyError("price_above_vwap filter requires a 'vwap' column (run the VWAP indicator first).")
        return df["close"] > df["vwap"]
