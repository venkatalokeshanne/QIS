"""Weighted Close Price — close weighted double against high and low."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("wclprice")
class WeightedClosePrice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="wclprice",
            display_name="Weighted Close Price",
            description="(High + Low + 2*Close) / 4.",
            category="price_transform",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["wclprice"] = (out["high"] + out["low"] + 2 * out["close"]) / 4
        return out
