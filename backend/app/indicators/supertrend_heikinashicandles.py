"""SuperTrend on Heikin Ashi — the same ATR-based flipping band as SuperTrend, but computed against Heikin Ashi's smoothed OHLC instead of raw price."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.heikinashicandles import HeikinAshiCandles
from app.indicators.registry import indicator_registry


@indicator_registry.register("supertrend_heikinashicandles")
class SuperTrendHeikinAshi(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="supertrend_heikinashicandles",
            display_name="SuperTrend on Heikin Ashi",
            description="The same ATR-based flipping band as SuperTrend, computed against Heikin Ashi's smoothed OHLC.",
            category="overlap",
            default_params={"period": 10, "multiple": 3.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        n, mult = p["period"], p["multiple"]
        ha = HeikinAshiCandles().calculate(df, {})
        out = ha.copy()

        # Select the ha_* columns FIRST, then rename -- renaming in place on
        # `out` would collide with the original open/high/low/close columns
        # it also carries, producing duplicate column labels.
        ha_ohlc = out[["ha_open", "ha_high", "ha_low", "ha_close"]].rename(
            columns={"ha_open": "open", "ha_high": "high", "ha_low": "low", "ha_close": "close"}
        )
        prev_close = ha_ohlc["close"].shift(1)
        tr = pd.concat(
            [
                ha_ohlc["high"] - ha_ohlc["low"],
                (ha_ohlc["high"] - prev_close).abs(),
                (ha_ohlc["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = wilders_smooth(tr, n)

        hl2 = (ha_ohlc["high"] + ha_ohlc["low"]) / 2
        basic_upper = (hl2 + mult * atr).to_numpy()
        basic_lower = (hl2 - mult * atr).to_numpy()
        close = ha_ohlc["close"].to_numpy()
        length = len(out)

        final_upper = np.full(length, np.nan)
        final_lower = np.full(length, np.nan)
        trend = np.full(length, np.nan)
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

        out[f"supertrend_ha_{n}_{mult}"] = trend
        out[f"supertrend_ha_direction_{n}_{mult}"] = direction
        return out
