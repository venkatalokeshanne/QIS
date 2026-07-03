"""Hull Moving Average (Alan Hull) — a WMA of a lag-corrected WMA blend, faster and smoother than a plain WMA/EMA of the same period."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _wma(series: pd.Series, period: int) -> pd.Series:
    weights = np.arange(1, period + 1)
    return series.rolling(window=period, min_periods=period).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)


@indicator_registry.register("hma")
class HullMovingAverage(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="hma",
            display_name="Hull Moving Average",
            description="WMA(2*WMA(n/2) - WMA(n)) over sqrt(n) -- faster and smoother than a plain WMA/EMA.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        half_wma = _wma(src, max(n // 2, 1))
        full_wma = _wma(src, n)
        raw_hma_input = 2 * half_wma - full_wma
        sqrt_n = max(int(round(np.sqrt(n))), 1)

        out[f"hma_{n}"] = _wma(raw_hma_input, sqrt_n)
        return out
