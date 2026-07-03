"""Linear Regression — the regression line's endpoint value at each bar, over a trailing N-period window."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _fit(window: np.ndarray) -> tuple[float, float]:
    x = np.arange(len(window))
    slope, intercept = np.polyfit(x, window, 1)
    return slope, intercept


@indicator_registry.register("linearreg")
class LinearRegression(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="linearreg",
            display_name="Linear Regression",
            description="Endpoint value of the least-squares regression line fit to the trailing N bars.",
            category="statistics",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        def endpoint(window: np.ndarray) -> float:
            slope, intercept = _fit(window)
            return slope * (len(window) - 1) + intercept

        out[f"linearreg_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).apply(endpoint, raw=True)
        return out
