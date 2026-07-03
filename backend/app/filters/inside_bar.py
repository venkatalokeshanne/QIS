"""Inside Bar — current bar's range is fully contained within the prior bar's range."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("inside_bar")
class InsideBar(Filter):
    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="inside_bar",
            display_name="Inside Bar",
            description="True where the current bar's high/low range sits inside the previous bar's range.",
            category="price_action",
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        condition = (df["high"] <= df["high"].shift(1)) & (df["low"] >= df["low"].shift(1))
        return condition.fillna(False)
