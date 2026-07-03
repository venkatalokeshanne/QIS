"""SuperTrend — an ATR-based trend-following band that flips sides (and resets) whenever price closes through it."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("supertrend")
class SuperTrend(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="supertrend",
            display_name="SuperTrend",
            description="An ATR-based trend-following band that flips sides whenever price closes through it.",
            category="overlap",
            default_params={"period": 10, "multiple": 3.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, mult = p["period"], p["multiple"]

        atr = wilders_smooth(true_range(out), n)
        hl2 = (out["high"] + out["low"]) / 2
        basic_upper = (hl2 + mult * atr).to_numpy()
        basic_lower = (hl2 - mult * atr).to_numpy()
        close = out["close"].to_numpy()
        length = len(out)

        final_upper = np.full(length, np.nan)
        final_lower = np.full(length, np.nan)
        trend = np.full(length, np.nan)
        # 1 = uptrend (line below price), -1 = downtrend (line above price). Always
        # one of the two (never 0/NaN) -- pre-warmup bars just carry an arbitrary
        # placeholder lean since there's no ATR yet to base a real direction on,
        # but `trend` itself (the actual line) stays NaN for those bars regardless.
        direction = np.ones(length)

        first_valid = n
        for i in range(first_valid, length):
            if i == first_valid:
                final_upper[i] = basic_upper[i]
                final_lower[i] = basic_lower[i]
                direction[i] = 1 if close[i] > basic_upper[i] else -1
            else:
                final_upper[i] = (
                    basic_upper[i]
                    if (basic_upper[i] < final_upper[i - 1] or close[i - 1] > final_upper[i - 1])
                    else final_upper[i - 1]
                )
                final_lower[i] = (
                    basic_lower[i]
                    if (basic_lower[i] > final_lower[i - 1] or close[i - 1] < final_lower[i - 1])
                    else final_lower[i - 1]
                )

                if direction[i - 1] == 1:
                    direction[i] = -1 if close[i] < final_lower[i] else 1
                else:
                    direction[i] = 1 if close[i] > final_upper[i] else -1

            trend[i] = final_lower[i] if direction[i] == 1 else final_upper[i]

        out[f"supertrend_{n}_{mult}"] = trend
        out[f"supertrend_direction_{n}_{mult}"] = direction
        return out
