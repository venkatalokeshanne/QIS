"""DeMark Pivot Points (Tom DeMark) — a single pivot plus one support and one resistance level, derived from the prior session's open/high/low/close using DeMark's conditional formula (which of three cases applies depends on whether the session closed above, below, or at its own open)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("demark_pivots")
class DeMarkPivots(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="demark_pivots",
            display_name="DeMark Pivot Points",
            description="A single pivot/support/resistance level from the prior session's OHLC, using DeMark's close-vs-open conditional formula.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DeMarkPivots requires a DatetimeIndex.")
        out = df.copy()

        session_date = pd.Series(out.index.date, index=out.index)
        daily_open = out["open"].groupby(session_date).transform("first")
        daily_high = out["high"].groupby(session_date).transform("max")
        daily_low = out["low"].groupby(session_date).transform("min")
        daily_close = out["close"].groupby(session_date).transform("last")

        per_session_open = daily_open.groupby(session_date).first().shift(1)
        per_session_high = daily_high.groupby(session_date).first().shift(1)
        per_session_low = daily_low.groupby(session_date).first().shift(1)
        per_session_close = daily_close.groupby(session_date).first().shift(1)

        o = session_date.map(per_session_open)
        h = session_date.map(per_session_high)
        low = session_date.map(per_session_low)
        c = session_date.map(per_session_close)

        x = pd.Series(np.nan, index=out.index)
        close_above_open = c > o
        close_below_open = c < o
        close_equal_open = ~close_above_open & ~close_below_open

        x[close_above_open] = (2 * h + low + c)[close_above_open]
        x[close_below_open] = (h + 2 * low + c)[close_below_open]
        x[close_equal_open] = (h + low + 2 * c)[close_equal_open]

        out["demark_pivot"] = x / 4
        out["demark_resistance"] = x / 2 - low
        out["demark_support"] = x / 2 - h
        return out
