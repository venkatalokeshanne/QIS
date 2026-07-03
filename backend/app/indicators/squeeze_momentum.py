"""
Squeeze Momentum Indicator (popularized by John Carter's "TTM Squeeze").

Detects a volatility "squeeze" -- Bollinger Bands compressed fully
inside Keltner Channels, meaning volatility has contracted ahead of a
likely expansion -- and pairs it with a momentum reading (a linear
regression of price vs. its own midline) showing which direction that
expansion is currently leaning.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("squeeze_momentum")
class SqueezeMomentum(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="squeeze_momentum",
            display_name="Squeeze Momentum Indicator",
            description="Flags a volatility squeeze (Bollinger Bands inside Keltner Channels) plus a momentum reading for the likely breakout direction.",
            category="momentum",
            default_params={
                "bb_period": 20,
                "bb_std_dev": 2.0,
                "kc_period": 20,
                "kc_atr_multiple": 1.5,
                "momentum_period": 20,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        bb_n, kc_n, mom_n = p["bb_period"], p["kc_period"], p["momentum_period"]

        close = out["close"]
        bb_mid = close.rolling(window=bb_n, min_periods=bb_n).mean()
        bb_std = close.rolling(window=bb_n, min_periods=bb_n).std()
        bb_upper = bb_mid + p["bb_std_dev"] * bb_std
        bb_lower = bb_mid - p["bb_std_dev"] * bb_std

        kc_mid = close.ewm(span=kc_n, adjust=False).mean()
        atr = wilders_smooth(true_range(out), kc_n)
        kc_upper = kc_mid + p["kc_atr_multiple"] * atr
        kc_lower = kc_mid - p["kc_atr_multiple"] * atr

        squeeze_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)

        # Momentum: linear-regression value of (close - average of the
        # highest-high/lowest-low midline and the SMA of close), a
        # smoothed measure of how far price has drifted from its own
        # recent equilibrium.
        highest_high = out["high"].rolling(window=mom_n, min_periods=mom_n).max()
        lowest_low = out["low"].rolling(window=mom_n, min_periods=mom_n).min()
        donchian_mid = (highest_high + lowest_low) / 2
        sma_close = close.rolling(window=mom_n, min_periods=mom_n).mean()
        deviation = close - (donchian_mid + sma_close) / 2

        def regression_endpoint(window: np.ndarray) -> float:
            x = np.arange(len(window))
            slope, intercept = np.polyfit(x, window, 1)
            return slope * (len(window) - 1) + intercept

        momentum = deviation.rolling(window=mom_n, min_periods=mom_n).apply(regression_endpoint, raw=True)

        out[f"squeeze_on_{bb_n}_{kc_n}"] = squeeze_on
        out[f"squeeze_momentum_{mom_n}"] = momentum
        return out
