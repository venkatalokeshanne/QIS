"""Donchian Channel (Richard Donchian) — highest high / lowest low over a trailing N-period window."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("donchian")
class Donchian(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="donchian",
            display_name="Donchian Channel",
            description="Highest high and lowest low over a trailing N-period window, with their midline.",
            category="volatility",
            default_params={"period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        upper = out["high"].rolling(window=n, min_periods=n).max()
        lower = out["low"].rolling(window=n, min_periods=n).min()

        out[f"donchian_upper_{n}"] = upper
        out[f"donchian_lower_{n}"] = lower
        out[f"donchian_mid_{n}"] = (upper + lower) / 2
        return out
