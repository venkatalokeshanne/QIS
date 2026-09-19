"""Close Outside Prior Range — flags a close beyond the ENTIRE prior bar's range (above its high or below its low), regardless of the current bar's own wick -- a full outside-close breakout, distinct from candle_range_sweep (which requires closing back INSIDE the prior range after sweeping past one extreme)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("close_outside_prior_range")
class CloseOutsidePriorRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="close_outside_prior_range",
            display_name="Close Outside Prior Range",
            description="Flags a close beyond the entire prior bar's range (above its high or below its low) -- a full outside-close breakout.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        prev_high, prev_low = out["high"].shift(1), out["low"].shift(1)

        out["close_above_prior_range"] = out["close"] > prev_high
        out["close_below_prior_range"] = out["close"] < prev_low
        return out
