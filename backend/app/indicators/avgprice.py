"""Average Price — mean of open, high, low, and close for a single bar."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("avgprice")
class AveragePrice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="avgprice",
            display_name="Average Price",
            description="(Open + High + Low + Close) / 4.",
            category="price_transform",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["avgprice"] = (out["open"] + out["high"] + out["low"] + out["close"]) / 4
        return out
