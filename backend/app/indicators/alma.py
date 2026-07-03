"""
ALMA (Arnaud Legoux Moving Average).

A Gaussian-weighted moving average: weights are shaped like a bell
curve positioned by `offset` (0 = weight concentrated at the oldest
bar, 1 = at the newest) and widened/narrowed by `sigma`, trading off
lag against smoothness more finely than a plain SMA/EMA.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _alma_weights(period: int, offset: float, sigma: float) -> np.ndarray:
    m = offset * (period - 1)
    s = period / sigma
    i = np.arange(period)
    weights = np.exp(-((i - m) ** 2) / (2 * s**2))
    return weights / weights.sum()


@indicator_registry.register("alma")
class ALMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="alma",
            display_name="ALMA (Arnaud Legoux Moving Average)",
            description="Gaussian-weighted moving average balancing lag and smoothness via offset/sigma.",
            category="overlap",
            default_params={"period": 9, "offset": 0.85, "sigma": 6.0, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        weights = _alma_weights(n, p["offset"], p["sigma"])

        out[f"alma_{n}"] = (
            out[p["source"]].rolling(window=n, min_periods=n).apply(lambda w: np.dot(w, weights), raw=True)
        )
        return out
