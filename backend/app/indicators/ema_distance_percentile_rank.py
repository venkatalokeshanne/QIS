"""
EMA Distance Percentile Rank.

The percentage distance of price from its own EMA, transformed into
that distance's percentile rank against its own trailing history --
answering "is today's stretch from the EMA unusually large FOR THIS
INSTRUMENT specifically" rather than against a fixed threshold that
would mean different things for a calm vs. a volatile name. A rank
near 100 reads as historically overheated/hot; near 0 as historically
compressed/cold.

The source script fixes this to a weekly-timeframe 200-period EMA via
its own request.security fetch -- computed here on whatever timeframe
and period this is given instead, since there's no second-timeframe
fetch available from within an Indicator (see period_high_low.py for
the same MTF-to-same-timeframe reduction pattern).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ema_distance_percentile_rank")
class EMADistancePercentileRank(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ema_distance_percentile_rank",
            display_name="EMA Distance Percentile Rank",
            description="Percentage distance from an EMA, transformed into its own percentile rank over a trailing lookback -- a self-relative hot/cold gauge.",
            category="momentum",
            default_params={"ema_period": 200, "lookback": 260},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        ema = out["close"].ewm(span=p["ema_period"], adjust=False, min_periods=p["ema_period"]).mean()
        pct_distance = (out["close"] - ema) / ema.replace(0, np.nan) * 100

        lb = p["lookback"]
        rank = pct_distance.rolling(window=lb + 1, min_periods=lb + 1).apply(
            lambda w: (w[:-1] < w[-1]).sum() / lb * 100, raw=True
        )

        out["ema_distance_pct"] = pct_distance
        out["ema_distance_percentile_rank"] = rank
        return out
