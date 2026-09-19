"""Session Window High/Low — the running high/low of an arbitrary intraday time window (e.g. 09:00-10:00), updating while inside the window each day and holding its final value until the next occurrence."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("session_window_high_low")
class SessionWindowHighLow(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="session_window_high_low",
            display_name="Session Window High/Low",
            description="Running high/low of an arbitrary intraday time window (e.g. 09:00-10:00), holding its final value until the window's next occurrence.",
            category="overlap",
            default_params={"window_start": "09:00", "window_end": "10:00"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("SessionWindowHighLow requires a DatetimeIndex.")
        out = df.copy()
        start, end = p["window_start"], p["window_end"]

        times = out.index.strftime("%H:%M")
        in_window = (times >= start) & (times < end)
        high, low = out["high"].to_numpy(), out["low"].to_numpy()
        length = len(out)

        window_high = np.full(length, np.nan)
        window_low = np.full(length, np.nan)
        cur_high, cur_low = np.nan, np.nan
        was_in_window = False
        for i in range(length):
            if in_window[i]:
                cur_high = high[i] if not was_in_window else max(cur_high, high[i])
                cur_low = low[i] if not was_in_window else min(cur_low, low[i])
            window_high[i], window_low[i] = cur_high, cur_low
            was_in_window = in_window[i]

        out[f"session_window_high_{start}_{end}"] = window_high
        out[f"session_window_low_{start}_{end}"] = window_low
        return out
