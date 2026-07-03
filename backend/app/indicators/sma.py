"""Simple Moving Average — unweighted mean of the trailing N bars."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("sma")
class SMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="sma",
            display_name="Simple Moving Average",
            description="Unweighted mean of the trailing N bars.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        out[f"sma_{p['period']}"] = out[p["source"]].rolling(window=p["period"], min_periods=p["period"]).mean()
        return out
