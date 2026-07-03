"""Volume Weighted Moving Average — a moving average where each bar's contribution is weighted by its own volume, not just its recency."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vwma")
class VolumeWeightedMovingAverage(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vwma",
            display_name="Volume Weighted Moving Average",
            description="Moving average where each bar is weighted by its own volume, not just recency.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        price_volume = src * out["volume"]
        volume_sum = out["volume"].rolling(window=n, min_periods=n).sum().replace(0, float("nan"))
        out[f"vwma_{n}"] = price_volume.rolling(window=n, min_periods=n).sum() / volume_sum
        return out
