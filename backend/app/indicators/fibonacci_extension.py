"""Fibonacci Extensions — the standard Fibonacci extension ratios (127.2/161.8/261.8%) projected beyond the trailing N-bar swing range, marking likely target levels for a continuation move."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_RATIOS = [1.272, 1.618, 2.618]


@indicator_registry.register("fibonacci_extension")
class FibonacciExtension(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fibonacci_extension",
            display_name="Fibonacci Extensions",
            description="Standard Fibonacci extension ratios (127.2/161.8/261.8%) projected beyond the trailing N-bar swing range.",
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
            label = str(ratio).replace(".", "_")
            out[f"fib_extension_up_{label}"] = swing_high + swing_range * (ratio - 1)
            out[f"fib_extension_down_{label}"] = swing_low - swing_range * (ratio - 1)
        return out
