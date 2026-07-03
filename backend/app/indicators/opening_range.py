"""
Opening Range.

Computes the high/low of the first N minutes of each session and
forward-fills those levels across the rest of the day. Used by
breakout strategies (ORB, ORB+VWAP).
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry
from app.utils.sessions import minutes_since_session_start


@indicator_registry.register("opening_range")
class OpeningRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="opening_range",
            display_name="Opening Range",
            description="High/low of the first N minutes of the session, held for the day.",
            category="price_action",
            default_params={"minutes": 15},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        if not isinstance(out.index, pd.DatetimeIndex):
            raise ValueError("OpeningRange requires a DatetimeIndex.")

        minutes = p["minutes"]
        day = out.index.date
        in_opening_window = minutes_since_session_start(out.index) < minutes

        high_col, low_col = f"or_high_{minutes}", f"or_low_{minutes}"

        masked_high = out["high"].where(in_opening_window)
        masked_low = out["low"].where(in_opening_window)

        or_high = masked_high.groupby(day).cummax().groupby(day).transform("max")
        or_low = masked_low.groupby(day).cummin().groupby(day).transform("min")

        out[high_col] = or_high
        out[low_col] = or_low
        return out
