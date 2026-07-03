"""Fibonacci Retracement — the standard Fibonacci ratios (23.6/38.2/50/61.8/78.6%) applied to the most recent swing high-to-low range, marking likely pullback levels within that swing."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_RATIOS = [0.236, 0.382, 0.5, 0.618, 0.786]


@indicator_registry.register("fibonacci_retracement")
class FibonacciRetracement(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fibonacci_retracement",
            display_name="Fibonacci Retracement",
            description="Standard Fibonacci ratios (23.6/38.2/50/61.8/78.6%) applied to the trailing N-bar swing range.",
            category="price_action",
            default_params={"period": 50},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        swing_high = out["high"].rolling(window=n, min_periods=n).max()
        swing_low = out["low"].rolling(window=n, min_periods=n).min()
        swing_range = swing_high - swing_low

        for ratio in _RATIOS:
            label = str(ratio).replace("0.", "")
            out[f"fib_retracement_{label}"] = swing_high - swing_range * ratio
        return out
