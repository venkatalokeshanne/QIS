"""Stochastic Fast — the raw (unsmoothed) %K/%D pair, more sensitive and noisier than the slow Stochastic."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("stochf")
class StochasticFast(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="stochf",
            display_name="Stochastic Fast",
            description="Raw (unsmoothed) %K, with a lightly smoothed %D -- more sensitive than the slow Stochastic.",
            category="momentum",
            default_params={"k_period": 14, "d_period": 3},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["k_period"]
        highest_high = out["high"].rolling(window=n, min_periods=n).max()
        lowest_low = out["low"].rolling(window=n, min_periods=n).min()
        rng = (highest_high - lowest_low).replace(0, np.nan)
        fast_k = 100 * (out["close"] - lowest_low) / rng
        fast_d = fast_k.rolling(window=p["d_period"], min_periods=p["d_period"]).mean()

        suffix = f"{n}_{p['d_period']}"
        out[f"stochf_k_{suffix}"] = fast_k
        out[f"stochf_d_{suffix}"] = fast_d
        return out
