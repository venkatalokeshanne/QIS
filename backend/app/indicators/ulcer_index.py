"""Ulcer Index (Peter Martin) — RMS of drawdown-from-rolling-high, a volatility measure that only penalizes downside."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ulcer_index")
class UlcerIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ulcer_index",
            display_name="Ulcer Index",
            description="Root-mean-square of the percentage drawdown from the trailing N-period high.",
            category="volatility",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        rolling_high = out["close"].rolling(window=n, min_periods=n).max().replace(0, np.nan)
        drawdown_pct = (out["close"] - rolling_high) / rolling_high * 100

        out[f"ulcer_index_{n}"] = np.sqrt((drawdown_pct**2).rolling(window=n, min_periods=n).mean())
        return out
