"""Time Series Forecast — the least-squares regression line's projected value ONE bar past the trailing window, instead of at its endpoint."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("tsf")
class TimeSeriesForecast(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="tsf",
            display_name="Time Series Forecast",
            description="The least-squares regression line's projected value one bar beyond the trailing window.",
            category="statistics",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        def forecast(window: np.ndarray) -> float:
            x = np.arange(len(window))
            slope, intercept = np.polyfit(x, window, 1)
            return slope * len(window) + intercept

        out[f"tsf_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).apply(forecast, raw=True)
        return out
