"""Normalized Average True Range — ATR expressed as a percentage of close, comparable across symbols/price levels."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("natr")
class NATR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="natr",
            display_name="Normalized Average True Range",
            description="ATR / close * 100 -- volatility as a percentage, comparable across symbols.",
            category="volatility",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        atr = wilders_smooth(true_range(out), p["period"])
        out[f"natr_{p['period']}"] = 100 * atr / out["close"].replace(0, np.nan)
        return out
