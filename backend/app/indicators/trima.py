"""Triangular Moving Average — an SMA of an SMA, weighting the middle of the window most heavily."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("trima")
class TRIMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="trima",
            display_name="Triangular Moving Average",
            description="An SMA of an SMA -- weights the middle of the window most heavily.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        first_len = (n + 1) // 2
        second_len = n // 2 + 1

        first_pass = out[p["source"]].rolling(window=first_len, min_periods=first_len).mean()
        out[f"trima_{n}"] = first_pass.rolling(window=second_len, min_periods=second_len).mean()
        return out
