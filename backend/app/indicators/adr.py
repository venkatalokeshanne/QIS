"""Average Daily Range (ADR) — rolling average of each session's own high-minus-low, held for the following session."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("adr")
class AverageDailyRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adr",
            display_name="Average Daily Range",
            description="Rolling average of each session's high-minus-low over the trailing N sessions.",
            category="volatility",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("AverageDailyRange requires a DatetimeIndex.")
        out = df.copy()
        n = p["period"]

        session_date = pd.Series(out.index.date, index=out.index)
        daily_high = out["high"].groupby(session_date).transform("max")
        daily_low = out["low"].groupby(session_date).transform("min")
        daily_range = daily_high - daily_low

        # One range value per session -- de-duplicate to session level, roll
        # the average over the trailing N *sessions*, then shift by one
        # session so today's ADR reflects the N sessions strictly BEFORE
        # today (never today's own still-forming range), then broadcast
        # back so every bar of a session carries that session's own reading.
        per_session_range = daily_range.groupby(session_date).first()
        adr_per_session = per_session_range.rolling(window=n, min_periods=n).mean().shift(1)

        out[f"adr_{n}"] = session_date.map(adr_per_session)
        return out
