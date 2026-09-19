"""Period High/Low — the running high/low of the CURRENT (still-forming) day/week/month, resetting at each new period boundary.

Computed on the same timeframe the data is given at (an expanding
max/min grouped by calendar period), not via a genuine higher-timeframe
fetch -- the source script explicitly opts into intrabar repainting via
request.security(..., lookahead_on) to get this same "current period's
high/low so far" read, which this reproduces without needing a second
timeframe at all.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_PERIOD_KEYS = {"D": lambda idx: idx.date, "W": lambda idx: idx.to_period("W"), "M": lambda idx: idx.to_period("M")}


@indicator_registry.register("period_high_low")
class PeriodHighLow(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="period_high_low",
            display_name="Period High/Low",
            description="Running high/low of the current (still-forming) day/week/month, resetting at each new period.",
            category="overlap",
            default_params={"period": "D"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("PeriodHighLow requires a DatetimeIndex.")
        out = df.copy()
        period = p["period"]

        period_key = pd.Series(_PERIOD_KEYS[period](out.index), index=out.index)
        out[f"period_high_{period}"] = out["high"].groupby(period_key).cummax()
        out[f"period_low_{period}"] = out["low"].groupby(period_key).cummin()
        return out
