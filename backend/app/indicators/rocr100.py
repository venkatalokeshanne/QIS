"""Rate of Change Ratio x100 — same as ROCR, scaled so "unchanged" reads as 100 instead of 1.0."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rocr100")
class ROCR100(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rocr100",
            display_name="Rate of Change Ratio x100",
            description="(Close / Close[n]) * 100 -- 100 means unchanged over the lookback.",
            category="momentum",
            default_params={"period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        out[f"rocr100_{n}"] = src / src.shift(n).replace(0, np.nan) * 100
        return out
