"""Bollinger Bands (John Bollinger) — SMA basis with upper/lower bands N standard deviations away."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("bbands")
class BollingerBands(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="bbands",
            display_name="Bollinger Bands",
            description="SMA basis with upper/lower bands N standard deviations away.",
            category="volatility",
            default_params={"period": 20, "std_dev": 2.0, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        middle = src.rolling(window=p["period"], min_periods=p["period"]).mean()
        std = src.rolling(window=p["period"], min_periods=p["period"]).std()

        suffix = f"{p['period']}"
        out[f"bbands_middle_{suffix}"] = middle
        out[f"bbands_upper_{suffix}"] = middle + p["std_dev"] * std
        out[f"bbands_lower_{suffix}"] = middle - p["std_dev"] * std
        return out
