"""Variance — rolling variance of price (standard deviation squared), a raw dispersion measure."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("variance")
class Variance(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="variance",
            display_name="Variance",
            description="Rolling variance of price over a trailing N-period window.",
            category="statistics",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        out[f"variance_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).var()
        return out
