"""Detrended Price Oscillator — close vs. a moving average shifted back in time, isolating cycles from the trend."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("dpo")
class DPO(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dpo",
            display_name="Detrended Price Oscillator",
            description="Close minus a centered SMA -- strips the trend out to highlight cycles.",
            category="momentum",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        shift = n // 2 + 1
        sma = src.rolling(window=n, min_periods=n).mean()

        out[f"dpo_{n}"] = src - sma.shift(shift)
        return out
