"""Distance from SMA — % distance of price from its own SMA, plus a smoothed signal line of that distance.

The source script anchors to the DAILY 200-SMA regardless of the
chart's own timeframe (via request.security), which this platform's
single-timeframe Indicator interface has no equivalent for -- this is
the same-timeframe version instead (distance from an SMA computed on
whatever bars it's given). At a daily interval it's identical to the
source; at an intraday interval it's a same-timeframe analogue, not a
literal port of the daily-anchored multi-timeframe behavior.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("distance_from_sma")
class DistanceFromSMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="distance_from_sma",
            display_name="Distance from SMA",
            description="% distance of price from its own SMA(period), plus a smoothed signal line of that distance.",
            category="trend",
            default_params={"period": 200, "source": "close", "smooth_period": 15},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, source, smooth_n = p["period"], p["source"], p["smooth_period"]

        sma = out[source].rolling(window=n, min_periods=n).mean()
        distance = (out[source] - sma) / sma * 100

        out[f"distance_from_sma_{n}"] = distance
        out[f"distance_from_sma_{n}_smooth_{smooth_n}"] = distance.rolling(window=smooth_n, min_periods=smooth_n).mean()
        return out
