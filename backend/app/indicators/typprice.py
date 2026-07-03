"""Typical Price — mean of high, low, and close for a single bar."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("typprice")
class TypicalPrice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="typprice",
            display_name="Typical Price",
            description="(High + Low + Close) / 3.",
            category="price_transform",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["typprice"] = (out["high"] + out["low"] + out["close"]) / 3
        return out
