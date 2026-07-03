"""Ultimate Oscillator (Larry Williams) — weighted blend of buying-pressure-vs-true-range ratios across three periods, reducing single-period whipsaw."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ultosc")
class UltimateOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ultosc",
            display_name="Ultimate Oscillator",
            description="Weighted blend of buying-pressure/true-range ratios across three periods (short/medium/long).",
            category="momentum",
            default_params={"period1": 7, "period2": 14, "period3": 28},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        prev_close = out["close"].shift(1)

        buying_pressure = out["close"] - pd.concat([out["low"], prev_close], axis=1).min(axis=1)
        true_range = pd.concat([out["high"], prev_close], axis=1).max(axis=1) - pd.concat(
            [out["low"], prev_close], axis=1
        ).min(axis=1)
        true_range = true_range.replace(0, np.nan)

        n1, n2, n3 = p["period1"], p["period2"], p["period3"]
        avg1 = buying_pressure.rolling(n1, min_periods=n1).sum() / true_range.rolling(n1, min_periods=n1).sum()
        avg2 = buying_pressure.rolling(n2, min_periods=n2).sum() / true_range.rolling(n2, min_periods=n2).sum()
        avg3 = buying_pressure.rolling(n3, min_periods=n3).sum() / true_range.rolling(n3, min_periods=n3).sum()

        out[f"ultosc_{n1}_{n2}_{n3}"] = 100 * (4 * avg1 + 2 * avg2 + avg3) / 7
        return out
