"""Bollinger Band Width — (upper - lower) / middle, a normalized volatility reading used to spot squeezes (low readings) ahead of expansion."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("bbands_width")
class BollingerBandWidth(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="bbands_width",
            display_name="Bollinger Band Width",
            description="(Upper - Lower) / Middle -- a normalized volatility reading; low values flag a squeeze.",
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

        out[f"bbands_width_{n}"] = (upper - lower) / middle.replace(0, np.nan)
        return out
