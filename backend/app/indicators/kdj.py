"""KDJ — extends the standard slow Stochastic Oscillator with a third "%J" line (3*%K - 2*%D) that overshoots both for an earlier turn signal."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("kdj")
class KDJ(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kdj",
            display_name="KDJ",
            description="Stochastic %K/%D plus %J = 3*%K - 2*%D, which overshoots both for an earlier turn signal.",
            category="momentum",
            default_params={"k_period": 9, "k_slowing": 3, "d_period": 3},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["k_period"]

        highest_high = out["high"].rolling(window=n, min_periods=n).max()
        lowest_low = out["low"].rolling(window=n, min_periods=n).min()
        rng = (highest_high - lowest_low).replace(0, np.nan)
        fast_k = 100 * (out["close"] - lowest_low) / rng

        slow_k = fast_k.rolling(window=p["k_slowing"], min_periods=p["k_slowing"]).mean()
        slow_d = slow_k.rolling(window=p["d_period"], min_periods=p["d_period"]).mean()
        j = 3 * slow_k - 2 * slow_d

        suffix = f"{n}_{p['k_slowing']}_{p['d_period']}"
        out[f"kdj_k_{suffix}"] = slow_k
        out[f"kdj_d_{suffix}"] = slow_d
        out[f"kdj_j_{suffix}"] = j
        return out
