"""Absolute Price Oscillator — difference between a fast and slow moving average, in raw price terms."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("apo")
class APO(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="apo",
            display_name="Absolute Price Oscillator",
            description="EMA(fast) - EMA(slow), in raw price terms (MACD without a signal line).",
            category="momentum",
            default_params={"fast_period": 12, "slow_period": 26, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        fast = src.ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        slow = src.ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        out[f"apo_{p['fast_period']}_{p['slow_period']}"] = fast - slow
        return out
