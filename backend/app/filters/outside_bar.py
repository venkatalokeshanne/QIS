"""Outside Bar — current bar's range fully engulfs the prior bar's range."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("outside_bar")
class OutsideBar(Filter):
    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="outside_bar",
            display_name="Outside Bar",
            description="True where the current bar's high/low range engulfs the previous bar's range.",
            category="price_action",
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        condition = (df["high"] >= df["high"].shift(1)) & (df["low"] <= df["low"].shift(1))
        return condition.fillna(False)
