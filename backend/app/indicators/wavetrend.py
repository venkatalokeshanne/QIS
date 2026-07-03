"""
WaveTrend Oscillator.

Smooths the typical price with an EMA, measures how far price has
strayed from that smoothed baseline relative to its own average
absolute deviation (a channel-style normalization rather than a
min/max one), then applies a second EMA/SMA stage to produce a
two-line (wt1/wt2) crossover oscillator.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("wavetrend")
class WaveTrend(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="wavetrend",
            display_name="WaveTrend Oscillator",
            description="Channel-normalized deviation of typical price from its own EMA, in a two-line crossover form.",
            category="momentum",
            default_params={"channel_period": 10, "average_period": 21, "signal_period": 4},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n1, n2, sig = p["channel_period"], p["average_period"], p["signal_period"]

        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        esa = typical_price.ewm(span=n1, adjust=False, min_periods=n1).mean()
        deviation = (typical_price - esa).abs().ewm(span=n1, adjust=False, min_periods=n1).mean()

        channel_index = (typical_price - esa) / (0.015 * deviation.replace(0, np.nan))
        wt1 = channel_index.ewm(span=n2, adjust=False, min_periods=n2).mean()
        wt2 = wt1.rolling(window=sig, min_periods=sig).mean()

        suffix = f"{n1}_{n2}_{sig}"
        out[f"wavetrend_wt1_{suffix}"] = wt1
        out[f"wavetrend_wt2_{suffix}"] = wt2
        return out
