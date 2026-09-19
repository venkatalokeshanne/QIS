"""
TEWMA Trend Strength.

Averages two TEMA-of-WMA baselines at different lengths (a fast one
and a slower one scaled by `length_multiplier`) into a single
lower-lag trend reference, then expresses price's ATR-normalized
distance from that reference as a "strength" oscillator -- how many
ATRs price currently sits above/below its own smoothed trend, plus an
EMA-smoothed version of that same reading.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


def _wma(series: pd.Series, n: int) -> pd.Series:
    weights = np.arange(1, n + 1)
    return series.rolling(window=n, min_periods=n).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)


def _tema(series: pd.Series, n: int) -> pd.Series:
    ema1 = series.ewm(span=n, adjust=False).mean()
    ema2 = ema1.ewm(span=n, adjust=False).mean()
    ema3 = ema2.ewm(span=n, adjust=False).mean()
    return 3 * ema1 - 3 * ema2 + ema3


@indicator_registry.register("tewma_trend_strength")
class TEWMATrendStrength(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="tewma_trend_strength",
            display_name="TEWMA Trend Strength",
            description="ATR-normalized distance of price from a dual-length TEMA-of-WMA trend baseline -- how many ATRs price currently sits above/below its own smoothed trend.",
            category="trend",
            default_params={
                "base_length": 50,
                "length_multiplier": 2.0,
                "atr_length": 40,
                "smooth_length": 50,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n1 = p["base_length"]
        n2 = round(n1 * p["length_multiplier"])

        tewma1 = _tema(_wma(out["close"], n1), n1)
        tewma2 = _tema(_wma(out["close"], n2), n2)
        tewma = (tewma1 + tewma2) / 2

        atr = wilders_smooth(true_range(out), p["atr_length"])
        strength = (out["close"] - tewma) / atr.replace(0, np.nan)
        smoothed = strength.ewm(span=p["smooth_length"], adjust=False, min_periods=p["smooth_length"]).mean()

        out["tewma_baseline"] = tewma
        out["tewma_strength"] = strength
        out["tewma_strength_smoothed"] = smoothed
        return out
