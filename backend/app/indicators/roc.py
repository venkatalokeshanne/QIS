"""Rate of Change — percentage price change over a trailing N-period lookback."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("roc")
class ROC(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="roc",
            display_name="Rate of Change",
            description="Percentage price change over a trailing N-period lookback.",
            category="momentum",
            default_params={"period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        out[f"roc_{n}"] = (src - src.shift(n)) / src.shift(n).replace(0, np.nan) * 100
        return out
