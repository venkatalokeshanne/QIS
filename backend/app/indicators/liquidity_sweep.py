"""
Liquidity Sweep Detector.

Flags a "stop hunt" style reversal: price briefly pokes beyond a
recent confirmed swing low (or high) -- where resting stop orders are
assumed to cluster -- then closes back inside it on the same bar,
suggesting the breach was a liquidity grab rather than a genuine
breakout. Builds on the same swing-detection idea as fractals/
pivot_points_hl.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("liquidity_sweep")
class LiquiditySweep(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="liquidity_sweep",
            display_name="Liquidity Sweep Detector",
            description="Price pokes beyond a recent swing high/low then closes back inside it -- a stop-hunt-style reversal signal.",
            category="price_action",
            default_params={"swing_lookback": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["swing_lookback"]

        # Prior swing extremes: the highest high / lowest low over the
        # trailing window EXCLUDING the current bar (shifted by 1), so the
        # current bar's own high/low can genuinely "sweep" past them.
        prior_high = out["high"].rolling(window=n, min_periods=n).max().shift(1)
        prior_low = out["low"].rolling(window=n, min_periods=n).min().shift(1)

        bullish_sweep = (out["low"] < prior_low) & (out["close"] > prior_low)
        bearish_sweep = (out["high"] > prior_high) & (out["close"] < prior_high)

        out["liquidity_sweep_bullish"] = bullish_sweep
        out["liquidity_sweep_bearish"] = bearish_sweep
        return out
