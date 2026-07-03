"""Relative Strength Index (J. Welles Wilder) — Wilder-smoothed ratio of average gains to average losses, the standard overbought/oversold oscillator."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("rsi")
class RSI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rsi",
            display_name="Relative Strength Index",
            description="Wilder-smoothed ratio of average gains to average losses (0-100).",
            category="momentum",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        delta = out[p["source"]].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = wilders_smooth(gain, n)
        avg_loss = wilders_smooth(loss, n)

        rs = avg_gain / avg_loss.replace(0, np.nan)
        out[f"rsi_{n}"] = 100 - (100 / (1 + rs))
        return out
