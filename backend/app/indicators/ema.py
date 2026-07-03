"""Exponential Moving Average — recursively weighted average that reacts faster than SMA to recent price."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ema")
class EMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ema",
            display_name="Exponential Moving Average",
            description="Recursively weighted moving average that reacts faster to recent price than SMA.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        out[f"ema_{p['period']}"] = (
            out[p["source"]].ewm(span=p["period"], adjust=False, min_periods=p["period"]).mean()
        )
        return out
