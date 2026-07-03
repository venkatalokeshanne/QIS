"""Momentum — raw price difference over a trailing N-period lookback."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("mom")
class Momentum(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="mom",
            display_name="Momentum",
            description="Close - Close[n] -- raw price change over a trailing lookback.",
            category="momentum",
            default_params={"period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        out[f"mom_{n}"] = out[p["source"]] - out[p["source"]].shift(n)
        return out
