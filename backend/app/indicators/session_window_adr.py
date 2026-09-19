"""Session Window ADR — average high-minus-low range of an arbitrary intraday time window (e.g. regular trading hours only) over the trailing N sessions, plus today's own window range as a % of that average.

Generalizes app.indicators.adr (which uses the FULL session) to an
arbitrary sub-window, and app.indicators.session_window_high_low (which
tracks the window's H/L but not a multi-day average of its range).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("session_window_adr")
class SessionWindowADR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="session_window_adr",
            display_name="Session Window ADR",
            description="Average range of an arbitrary intraday time window over the trailing N sessions, plus today's window range as a % of that average.",
            category="volatility",
            default_params={"window_start": "09:30", "window_end": "16:00", "lookback_days": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("SessionWindowADR requires a DatetimeIndex.")
        out = df.copy()
        start, end, n = p["window_start"], p["window_end"], p["lookback_days"]

        times = out.index.strftime("%H:%M")
        in_window = (times >= start) & (times < end)
        session_date = pd.Series(out.index.date, index=out.index)

        window_high = out["high"].where(in_window).groupby(session_date).transform("max")
        window_low = out["low"].where(in_window).groupby(session_date).transform("min")
        window_range = window_high - window_low

        per_session_range = window_range.groupby(session_date).first()
        # Average of the trailing N sessions STRICTLY BEFORE today (shift(1)),
        # same "never leak today's still-forming range" convention as adr.py.
        avg_range_per_session = per_session_range.rolling(window=n, min_periods=n).mean().shift(1)

        suffix = f"{start}_{end}_{n}"
        avg_range = session_date.map(avg_range_per_session)
        out[f"session_window_adr_{suffix}"] = avg_range
        out[f"session_window_range_{suffix}"] = window_range
        out[f"session_window_range_pct_of_adr_{suffix}"] = (window_range / avg_range.replace(0, np.nan)) * 100
        return out
