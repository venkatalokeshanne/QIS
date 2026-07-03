"""
Kaufman's Adaptive Moving Average (Perry Kaufman).

Adjusts its own smoothing speed bar-by-bar based on an "efficiency
ratio" (net directional movement vs. total movement over the window):
near-1 efficiency (a clean trend) speeds the average up toward the
fast constant, near-0 efficiency (choppy/noisy) slows it down toward
the slow constant -- recursive, not a single vectorized rolling window.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("kama")
class KAMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kama",
            display_name="Kaufman's Adaptive Moving Average",
            description="Speeds up in clean trends and slows down in chop, via an efficiency-ratio-driven smoothing constant.",
            category="overlap",
            default_params={"period": 10, "fast_period": 2, "slow_period": 30, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        change = (src - src.shift(n)).abs()
        volatility = src.diff().abs().rolling(window=n, min_periods=n).sum()
        efficiency_ratio = (change / volatility.replace(0, np.nan)).fillna(0)

        fast_sc = 2 / (p["fast_period"] + 1)
        slow_sc = 2 / (p["slow_period"] + 1)
        smoothing_constant = (efficiency_ratio * (fast_sc - slow_sc) + slow_sc) ** 2

        values = src.to_numpy()
        sc = smoothing_constant.to_numpy()
        kama = np.full(len(out), np.nan)

        first_valid = n
        if first_valid < len(out):
            kama[first_valid] = values[first_valid]
            for i in range(first_valid + 1, len(out)):
                if np.isnan(sc[i]):
                    kama[i] = kama[i - 1]
                else:
                    kama[i] = kama[i - 1] + sc[i] * (values[i] - kama[i - 1])

        out[f"kama_{n}"] = kama
        return out
