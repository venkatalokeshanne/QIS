"""Linear Regression Intercept — the y-intercept of the least-squares line fit to the trailing N bars."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("linearregintercept")
class LinearRegressionIntercept(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="linearregintercept",
            display_name="Linear Regression Intercept",
            description="Y-intercept of the least-squares line fit to the trailing N bars.",
            category="statistics",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        def intercept(window: np.ndarray) -> float:
            x = np.arange(len(window))
            _, b = np.polyfit(x, window, 1)
            return b

        out[f"linearregintercept_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).apply(intercept, raw=True)
        return out
