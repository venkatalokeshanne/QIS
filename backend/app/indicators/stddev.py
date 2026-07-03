"""Standard Deviation — rolling standard deviation of price, the basic dispersion measure several other indicators (Bollinger Bands, etc.) build on."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("stddev")
class StandardDeviation(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="stddev",
            display_name="Standard Deviation",
            description="Rolling standard deviation of price over a trailing N-period window.",
            category="statistics",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        out[f"stddev_{n}"] = out[p["source"]].rolling(window=n, min_periods=n).std()
        return out
