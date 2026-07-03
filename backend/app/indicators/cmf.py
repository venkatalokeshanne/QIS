"""Chaikin Money Flow (Marc Chaikin) — volume-weighted average of each bar's close-location value over a trailing window."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("cmf")
class ChaikinMoneyFlow(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="cmf",
            display_name="Chaikin Money Flow",
            description="Volume-weighted average of each bar's close-location value over a trailing window.",
            category="volume",
            default_params={"period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        price_range = (out["high"] - out["low"]).replace(0, np.nan)
        money_flow_multiplier = ((out["close"] - out["low"]) - (out["high"] - out["close"])) / price_range
        money_flow_volume = money_flow_multiplier * out["volume"]

        volume_sum = out["volume"].rolling(window=n, min_periods=n).sum().replace(0, np.nan)
        out[f"cmf_{n}"] = money_flow_volume.rolling(window=n, min_periods=n).sum() / volume_sum
        return out
