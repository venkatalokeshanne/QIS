"""Midpoint — midpoint of the highest and lowest CLOSE over a trailing window (distinct from Midprice, which uses high/low)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("midpoint")
class Midpoint(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="midpoint",
            display_name="Midpoint",
            description="(Highest close + Lowest close) / 2 over a trailing N-period window.",
            category="overlap",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        out[f"midpoint_{n}"] = (
            src.rolling(window=n, min_periods=n).max() + src.rolling(window=n, min_periods=n).min()
        ) / 2
        return out
