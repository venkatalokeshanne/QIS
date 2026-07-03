"""Rate of Change Percentage — same idea as ROC, expressed as a fraction (0.05) instead of a percent (5)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rocp")
class ROCP(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rocp",
            display_name="Rate of Change (Fractional)",
            description="(Close - Close[n]) / Close[n] -- ROC expressed as a fraction rather than a percent.",
            category="momentum",
            default_params={"period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        out[f"rocp_{n}"] = (src - src.shift(n)) / src.shift(n).replace(0, np.nan)
        return out
