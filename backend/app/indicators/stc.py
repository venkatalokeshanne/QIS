"""Schaff Trend Cycle (Doug Schaff) — applies the Stochastic formula to MACD (instead of price), then smooths that twice, catching trend turns faster than MACD alone."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("stc")
class SchaffTrendCycle(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="stc",
            display_name="Schaff Trend Cycle",
            description="Stochastic formula applied to MACD, then double-smoothed -- catches trend turns faster than MACD alone.",
            category="momentum",
            default_params={
                "fast_period": 23,
                "slow_period": 50,
                "cycle_period": 10,
                "d1_period": 3,
                "d2_period": 3,
                "source": "close",
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        n = p["cycle_period"]

        fast_ema = src.ewm(span=p["fast_period"], adjust=False).mean()
        slow_ema = src.ewm(span=p["slow_period"], adjust=False).mean()
        macd_line = fast_ema - slow_ema

        lowest_macd = macd_line.rolling(window=n, min_periods=n).min()
        highest_macd = macd_line.rolling(window=n, min_periods=n).max()
        stoch_k = 100 * (macd_line - lowest_macd) / (highest_macd - lowest_macd).replace(0, float("nan"))
        smoothed_k = stoch_k.ewm(span=p["d1_period"], adjust=False).mean()

        lowest_k = smoothed_k.rolling(window=n, min_periods=n).min()
        highest_k = smoothed_k.rolling(window=n, min_periods=n).max()
        stoch_d = 100 * (smoothed_k - lowest_k) / (highest_k - lowest_k).replace(0, float("nan"))

        out[f"stc_{n}"] = stoch_d.ewm(span=p["d2_period"], adjust=False).mean()
        return out
