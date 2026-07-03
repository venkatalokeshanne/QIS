"""Volume-Weighted Average Price — cumulative (price*volume)/volume, reset every session; the standard intraday fair-value anchor."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vwap")
class VWAP(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vwap",
            display_name="Volume-Weighted Average Price",
            description="Cumulative (typical price * volume) / cumulative volume, reset every session.",
            category="overlap",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("VWAP requires a DatetimeIndex.")
        out = df.copy()

        session_date = pd.Series(out.index.date, index=out.index)
        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        pv = typical_price * out["volume"]

        cumulative_pv = pv.groupby(session_date).cumsum()
        cumulative_volume = out["volume"].groupby(session_date).cumsum().replace(0, np.nan)

        out["vwap"] = cumulative_pv / cumulative_volume
        return out
