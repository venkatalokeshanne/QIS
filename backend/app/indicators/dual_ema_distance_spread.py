"""
Dual EMA Distance Spread.

Each EMA's % distance from price is computed independently, then the
FAST one is subtracted from the SLOW one -- a spread that's positive
when price is stretched further above (or less far below) its
long-term EMA than its short-term one, and negative when the
short-term stretch dominates. Distinct from plain MACD (spread of two
EMAs of price, not of two independent %-distance-from-EMA readings)
and from app.indicators.ema_distance_percentile_rank (single EMA,
percentile-ranked rather than compared to a second EMA's own distance).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("dual_ema_distance_spread")
class DualEMADistanceSpread(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dual_ema_distance_spread",
            display_name="Dual EMA Distance Spread",
            description="The fast EMA's %-distance from price minus the slow EMA's own %-distance -- positive when short-term stretch is outrunning the long-term trend's.",
            category="momentum",
            default_params={"fast_period": 50, "slow_period": 200},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        ema_fast = out["close"].ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        ema_slow = out["close"].ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        dist_fast = (out["close"] - ema_fast) / ema_fast.replace(0, np.nan) * 100
        dist_slow = (out["close"] - ema_slow) / ema_slow.replace(0, np.nan) * 100

        out["dual_ema_distance_fast_pct"] = dist_fast
        out["dual_ema_distance_slow_pct"] = dist_slow
        out["dual_ema_distance_spread"] = dist_slow - dist_fast
        return out
