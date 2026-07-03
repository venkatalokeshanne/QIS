"""MACD Slope — bar-over-bar rate of change of the MACD histogram, flagging momentum acceleration/deceleration a beat before the histogram itself flips sign."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("macd_slope")
class MACDSlope(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="macd_slope",
            display_name="MACD Slope",
            description="Bar-over-bar change of the MACD histogram -- momentum acceleration/deceleration.",
            category="momentum",
            default_params={"fast_period": 12, "slow_period": 26, "signal_period": 9, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        fast_ema = src.ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        slow_ema = src.ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=p["signal_period"], adjust=False, min_periods=p["signal_period"]).mean()
        histogram = macd_line - signal_line

        suffix = f"{p['fast_period']}_{p['slow_period']}_{p['signal_period']}"
        out[f"macd_slope_{suffix}"] = histogram.diff()
        return out
