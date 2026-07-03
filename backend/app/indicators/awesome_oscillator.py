"""Awesome Oscillator (Bill Williams) — difference between a fast and slow SMA of the median price."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("awesome_oscillator")
class AwesomeOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="awesome_oscillator",
            display_name="Awesome Oscillator",
            description="SMA(5) minus SMA(34) of the median price ((high+low)/2) -- a momentum gauge.",
            category="momentum",
            default_params={"fast_period": 5, "slow_period": 34},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        median_price = (out["high"] + out["low"]) / 2

        fast = median_price.rolling(window=p["fast_period"], min_periods=p["fast_period"]).mean()
        slow = median_price.rolling(window=p["slow_period"], min_periods=p["slow_period"]).mean()

        out[f"ao_{p['fast_period']}_{p['slow_period']}"] = fast - slow
        return out
