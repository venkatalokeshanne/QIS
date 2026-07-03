"""Classic Pivot Points (floor-trader formula) — the standard pivot plus three support and three resistance levels, derived from the PRIOR session's high/low/close."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("pivot_points")
class PivotPoints(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="pivot_points",
            display_name="Pivot Points (Classic)",
            description="Standard floor-trader pivot plus three support/resistance levels from the prior session's H/L/C.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("PivotPoints requires a DatetimeIndex.")
        out = df.copy()

        session_date = pd.Series(out.index.date, index=out.index)
        daily_high = out["high"].groupby(session_date).transform("max")
        daily_low = out["low"].groupby(session_date).transform("min")
        daily_close = out["close"].groupby(session_date).transform("last")

        per_session_high = daily_high.groupby(session_date).first().shift(1)
        per_session_low = daily_low.groupby(session_date).first().shift(1)
        per_session_close = daily_close.groupby(session_date).first().shift(1)

        prior_high = session_date.map(per_session_high)
        prior_low = session_date.map(per_session_low)
        prior_close = session_date.map(per_session_close)

        pivot = (prior_high + prior_low + prior_close) / 3
        rng = prior_high - prior_low

        out["pivot_point"] = pivot
        out["pivot_r1"] = 2 * pivot - prior_low
        out["pivot_s1"] = 2 * pivot - prior_high
        out["pivot_r2"] = pivot + rng
        out["pivot_s2"] = pivot - rng
        out["pivot_r3"] = prior_high + 2 * (pivot - prior_low)
        out["pivot_s3"] = prior_low - 2 * (prior_high - pivot)
        return out
