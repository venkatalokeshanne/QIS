"""Rate of Change Ratio — price now divided by price N bars ago (1.0 = unchanged)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rocr")
class ROCR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rocr",
            display_name="Rate of Change Ratio",
            description="Close / Close[n] -- 1.0 means unchanged over the lookback.",
            category="momentum",
            default_params={"period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        out[f"rocr_{n}"] = src / src.shift(n).replace(0, np.nan)
        return out
