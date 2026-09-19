"""Session Open Price — the open price captured at a specific time-of-day (e.g. 09:30), held constant for the rest of that day until the next occurrence resets it. Optionally also captures that same anchor bar's high/low (e.g. to use its range as a reference candle)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("session_open_price")
class SessionOpenPrice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="session_open_price",
            display_name="Session Open Price",
            description="The open price captured at a specific time-of-day, held constant until the next day's occurrence. Optionally also captures that bar's high/low.",
            category="overlap",
            default_params={"session_time": "09:30", "include_high_low": False},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("SessionOpenPrice requires a DatetimeIndex.")
        out = df.copy()
        session_time = p["session_time"]

        is_open_bar = out.index.strftime("%H:%M") == session_time
        open_price = out["open"].where(is_open_bar).ffill()
        out[f"session_open_price_{session_time}"] = open_price

        if p["include_high_low"]:
            out[f"session_open_price_{session_time}_high"] = out["high"].where(is_open_bar).ffill()
            out[f"session_open_price_{session_time}_low"] = out["low"].where(is_open_bar).ffill()
        return out
