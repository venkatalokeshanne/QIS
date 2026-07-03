"""Camarilla Pivot Points — eight support/resistance levels derived from the PRIOR session's high/low/close, using Camarilla's own fixed multipliers (tighter around price than classic floor pivots, popular for intraday mean-reversion)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("camarilla_pivots")
class CamarillaPivots(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="camarilla_pivots",
            display_name="Camarilla Pivot Points",
            description="Eight support/resistance levels from the prior session's H/L/C, using Camarilla's fixed multipliers.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("CamarillaPivots requires a DatetimeIndex.")
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
        rng = prior_high - prior_low

        out["camarilla_r4"] = prior_close + rng * 1.1 / 2
        out["camarilla_r3"] = prior_close + rng * 1.1 / 4
        out["camarilla_r2"] = prior_close + rng * 1.1 / 6
        out["camarilla_r1"] = prior_close + rng * 1.1 / 12
        out["camarilla_s1"] = prior_close - rng * 1.1 / 12
        out["camarilla_s2"] = prior_close - rng * 1.1 / 6
        out["camarilla_s3"] = prior_close - rng * 1.1 / 4
        out["camarilla_s4"] = prior_close - rng * 1.1 / 2
        return out
