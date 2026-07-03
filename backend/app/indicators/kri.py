"""Kairi Relative Index (KRI) — percentage deviation of price from its own simple moving average."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("kri")
class KairiRelativeIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kri",
            display_name="Kairi Relative Index",
            description="(Close - SMA) / SMA * 100 -- how far price has stretched from its own moving average.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        sma = out["close"].rolling(window=n, min_periods=n).mean().replace(0, np.nan)
        out[f"kri_{n}"] = (out["close"] - sma) / sma * 100
        return out
