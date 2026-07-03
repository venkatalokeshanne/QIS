"""Linear Regression Slope — the slope coefficient of the least-squares line fit to the trailing N bars, in price-per-bar terms."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("linearregslope")
class LinearRegressionSlope(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="linearregslope",
            display_name="Linear Regression Slope",
            description="Slope of the least-squares line fit to the trailing N bars, in price-per-bar terms.",
            category="statistics",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        def slope(window: np.ndarray) -> float:
            x = np.arange(len(window))
            m, _ = np.polyfit(x, window, 1)
            return m

        out[f"linearregslope_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).apply(slope, raw=True)
        return out
