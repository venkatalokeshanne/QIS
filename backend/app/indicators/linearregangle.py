"""Linear Regression Angle — the slope of the least-squares line, expressed as an angle in degrees rather than raw price-per-bar."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("linearregangle")
class LinearRegressionAngle(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="linearregangle",
            display_name="Linear Regression Angle",
            description="arctan(slope) in degrees -- the least-squares line's steepness, independent of price scale.",
            category="statistics",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        def angle(window: np.ndarray) -> float:
            x = np.arange(len(window))
            m, _ = np.polyfit(x, window, 1)
            return np.degrees(np.arctan(m))

        out[f"linearregangle_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).apply(angle, raw=True)
        return out
