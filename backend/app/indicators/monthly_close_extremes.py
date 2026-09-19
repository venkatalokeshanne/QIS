"""Monthly Close Extremes — the highest and lowest DAILY CLOSE (not price high/low) among fully COMPLETED days so far within the current calendar month, resetting at each new month. Distinct from app.indicators.period_high_low, which tracks the high/low of PRICE, not of closes. Uses only the prior completed day's close at every intraday bar, so it never leaks the still-forming current day's eventual close."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("monthly_close_extremes")
class MonthlyCloseExtremes(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="monthly_close_extremes",
            display_name="Monthly Close Extremes",
            description="Highest and lowest daily CLOSE (not price high/low) among fully completed days so far within the current calendar month.",
            category="overlap",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("MonthlyCloseExtremes requires a DatetimeIndex.")
        out = df.copy()

        session_date = pd.Series(out.index.date, index=out.index)
        month_key = pd.Series(out.index.to_period("M"), index=out.index)

        # One row per calendar day (that day's own final close), then shifted
        # by one day so each bar only ever sees PRIOR completed days -- never
        # its own still-forming day's eventual close.
        daily_close = out["close"].groupby(session_date).last()
        prior_completed_close = daily_close.shift(1)
        completed_close_per_bar = session_date.map(prior_completed_close)

        out["monthly_close_high"] = completed_close_per_bar.groupby(month_key).cummax()
        out["monthly_close_low"] = completed_close_per_bar.groupby(month_key).cummin()
        return out
