"""
Range Expansion Volume Breakout.

Flags an "outside bar" relative to a trailing window -- today's high
exceeds every one of the last `swing_bars` highs AND today's low
undercuts every one of the last `swing_bars` lows, meaning the bar's
range fully engulfs the recent range in both directions -- confirmed
by a volume climax (today's volume exceeds the highest volume of the
same trailing window). A distinct, literal price-action definition
from app.strategies.vol_range_expansion's rolling z-score approach.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("range_expansion_volume_breakout")
class RangeExpansionVolumeBreakout(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="range_expansion_volume_breakout",
            display_name="Range Expansion Volume Breakout",
            description="Flags an outside bar (engulfs the last N bars' highs and lows) confirmed by a volume climax over the same window.",
            category="volume",
            default_params={"swing_bars": 5, "volume_lookback": 75},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["swing_bars"]

        prior_high_max = out["high"].shift(1).rolling(window=n, min_periods=n).max()
        prior_low_min = out["low"].shift(1).rolling(window=n, min_periods=n).min()
        prior_vol_max = out["volume"].shift(1).rolling(window=p["volume_lookback"], min_periods=p["volume_lookback"]).max()

        high_cond = out["high"] > prior_high_max
        low_cond = out["low"] < prior_low_min
        vol_cond = out["volume"] > prior_vol_max

        out["range_expansion_volume_breakout"] = high_cond & low_cond & vol_cond
        return out
