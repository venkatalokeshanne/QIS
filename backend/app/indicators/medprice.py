"""Median Price — midpoint of a single bar's high and low."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("medprice")
class MedianPrice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="medprice",
            display_name="Median Price",
            description="(High + Low) / 2.",
            category="price_transform",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["medprice"] = (out["high"] + out["low"]) / 2
        return out
