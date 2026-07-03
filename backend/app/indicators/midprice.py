"""Midprice — midpoint of the highest high and lowest low over a trailing window."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("midprice")
class Midprice(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="midprice",
            display_name="Midprice",
            description="(Highest high + Lowest low) / 2 over a trailing N-period window.",
            category="overlap",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        out[f"midprice_{n}"] = (
            out["high"].rolling(window=n, min_periods=n).max() + out["low"].rolling(window=n, min_periods=n).min()
        ) / 2
        return out
