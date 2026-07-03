"""Higher High — current bar's high exceeds the prior bar's high."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("higher_high")
class HigherHigh(Filter):
    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="higher_high",
            display_name="Higher High",
            description="True where the current bar's high is above the previous bar's high.",
            category="price_action",
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        return (df["high"] > df["high"].shift(1)).fillna(False)
