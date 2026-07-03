"""Heikin Ashi Candles — smoothed OHLC computed from averaged current/prior bars, filtering noise to make trends visually cleaner."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("heikinashicandles")
class HeikinAshiCandles(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="heikinashicandles",
            display_name="Heikin Ashi Candles",
            description="Smoothed OHLC (averaged with the prior bar) -- filters noise to make trends visually cleaner.",
            category="overlap",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        n = len(out)

        ha_close = (out["open"] + out["high"] + out["low"] + out["close"]) / 4
        ha_open = np.full(n, np.nan)
        if n > 0:
            ha_open[0] = (out["open"].iloc[0] + out["close"].iloc[0]) / 2
            for i in range(1, n):
                ha_open[i] = (ha_open[i - 1] + ha_close.iloc[i - 1]) / 2

        ha_open_s = pd.Series(ha_open, index=out.index)
        ha_high = pd.concat([out["high"], ha_open_s, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([out["low"], ha_open_s, ha_close], axis=1).min(axis=1)

        out["ha_open"] = ha_open_s
        out["ha_high"] = ha_high
        out["ha_low"] = ha_low
        out["ha_close"] = ha_close
        return out
