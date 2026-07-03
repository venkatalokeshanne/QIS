"""
Fisher Transform (John Ehlers).

Rescales price into a bounded -1..1 range using a trailing high/low
window, then applies the inverse hyperbolic tangent (via 0.5*ln((1+x)/(1-x)))
to sharpen turning points into extreme, clearly separated peaks/troughs
compared to a raw oscillator. Both stages are smoothed against their own
prior value, so this is computed as a recurrence (bar-by-bar), not a
single vectorized rolling window.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_CLAMP = 0.999  # keeps the value argument to ln() away from +-1 (undefined there)


@indicator_registry.register("fisher_transform")
class FisherTransform(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fisher_transform",
            display_name="Fisher Transform",
            description="Rescales price into a Gaussian-like distribution to sharpen turning points.",
            category="momentum",
            default_params={"period": 10},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        median_price = (out["high"] + out["low"]) / 2
        rolling_high = median_price.rolling(window=n, min_periods=n).max()
        rolling_low = median_price.rolling(window=n, min_periods=n).min()
        band = rolling_high - rolling_low

        values = np.full(len(out), np.nan)
        fisher = np.full(len(out), np.nan)
        prev_value = 0.0
        prev_fisher = 0.0

        median_arr = median_price.to_numpy()
        low_arr = rolling_low.to_numpy()
        band_arr = band.to_numpy()

        for i in range(len(out)):
            if np.isnan(band_arr[i]) or band_arr[i] == 0:
                continue
            raw = 2 * ((median_arr[i] - low_arr[i]) / band_arr[i] - 0.5)
            value = 0.33 * raw + 0.67 * prev_value
            value = max(min(value, _CLAMP), -_CLAMP)
            f = 0.5 * np.log((1 + value) / (1 - value)) + 0.5 * prev_fisher

            values[i] = value
            fisher[i] = f
            prev_value = value
            prev_fisher = f

        out[f"fisher_{n}"] = fisher
        out[f"fisher_signal_{n}"] = pd.Series(fisher, index=out.index).shift(1)
        return out
