"""Weighted Moving Average — linearly weighted mean, most recent bar weighted heaviest."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("wma")
class WMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="wma",
            display_name="Weighted Moving Average",
            description="Linearly weighted moving average -- the most recent bar carries the most weight.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        weights = np.arange(1, n + 1)

        out[f"wma_{n}"] = (
            out[p["source"]].rolling(window=n, min_periods=n).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)
        )
        return out
