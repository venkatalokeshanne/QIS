"""Cumulative Relative Volume — cumulative volume since session start, compared against the average cumulative volume at that SAME time-of-day over the trailing N prior sessions.

Distinct from app.indicators.rvol (which compares each bar's raw
volume to a simple rolling average of past bars): this accounts for a
trading day's natural volume seasonality (heavier at the open/close,
lighter midday) by only ever comparing a given time-of-day against
that same time-of-day on prior sessions, not against volume from other
parts of the day.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("cumulative_relative_volume")
class CumulativeRelativeVolume(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="cumulative_relative_volume",
            display_name="Cumulative Relative Volume",
            description="Cumulative volume since session start vs. the average cumulative volume at the same time-of-day over the trailing N sessions.",
            category="volume",
            default_params={"lookback_days": 10, "high_threshold": 3.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("CumulativeRelativeVolume requires a DatetimeIndex.")
        out = df.copy()
        n, threshold = p["lookback_days"], p["high_threshold"]

        session_date = pd.Series(out.index.date, index=out.index)
        time_key = out.index.strftime("%H:%M")
        cum_vol = out["volume"].groupby(session_date).cumsum()

        pivot = pd.DataFrame({"date": session_date.to_numpy(), "time": time_key, "cum_vol": cum_vol.to_numpy()}).pivot(
            index="date", columns="time", values="cum_vol"
        )
        # Average cumulative volume at each time-of-day over the trailing N
        # sessions STRICTLY BEFORE today (shift(1) -- never leak today's own reading).
        avg_pivot = pivot.rolling(window=n, min_periods=n).mean().shift(1)
        avg_stacked = avg_pivot.stack()

        lookup_index = pd.MultiIndex.from_arrays([session_date.to_numpy(), time_key])
        avg_cum_vol = pd.Series(avg_stacked.reindex(lookup_index).to_numpy(), index=out.index)

        rvol = cum_vol / avg_cum_vol.replace(0, np.nan)
        out[f"cum_rvol_{n}"] = rvol
        out[f"cum_rvol_{n}_high"] = rvol > threshold
        return out
