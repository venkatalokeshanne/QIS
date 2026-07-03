"""%B — Close's position relative to the Bollinger Bands themselves (0 = at the lower band, 1 = at the upper band; can exceed 0-1 during breakouts)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("percent_b")
class PercentB(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="percent_b",
            display_name="%B",
            description="Close's position relative to the Bollinger Bands (0 = lower band, 1 = upper band).",
            category="volatility",
            default_params={"period": 20, "std_dev": 2.0, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        middle = src.rolling(window=n, min_periods=n).mean()
        std = src.rolling(window=n, min_periods=n).std()
        upper = middle + p["std_dev"] * std
        lower = middle - p["std_dev"] * std

        out[f"percent_b_{n}"] = (src - lower) / (upper - lower).replace(0, np.nan)
        return out
