"""Chaikin A/D Oscillator (Marc Chaikin) — difference between a fast and slow EMA of the Accumulation/Distribution Line."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("adosc")
class ADOsc(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adosc",
            display_name="Chaikin A/D Oscillator",
            description="EMA(fast) - EMA(slow) of the Accumulation/Distribution Line.",
            category="volume",
            default_params={"fast_period": 3, "slow_period": 10},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        price_range = (out["high"] - out["low"]).replace(0, np.nan)
        money_flow_multiplier = ((out["close"] - out["low"]) - (out["high"] - out["close"])) / price_range
        ad_line = (money_flow_multiplier * out["volume"]).fillna(0).cumsum()

        fast = ad_line.ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        slow = ad_line.ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        out[f"adosc_{p['fast_period']}_{p['slow_period']}"] = fast - slow
        return out
