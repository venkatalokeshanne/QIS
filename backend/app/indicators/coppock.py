"""Coppock Curve (Edwin Coppock) — a weighted moving average of two long-term ROC readings, originally designed to flag major bottoms."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("coppock")
class CoppockCurve(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="coppock",
            display_name="Coppock Curve",
            description="Weighted moving average of a long and a longer-term Rate of Change -- designed to flag major bottoms.",
            category="momentum",
            default_params={"roc1_period": 14, "roc2_period": 11, "wma_period": 10, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        roc1 = (src - src.shift(p["roc1_period"])) / src.shift(p["roc1_period"]).replace(0, np.nan) * 100
        roc2 = (src - src.shift(p["roc2_period"])) / src.shift(p["roc2_period"]).replace(0, np.nan) * 100
        combined = roc1 + roc2

        n = p["wma_period"]
        weights = np.arange(1, n + 1)
        out[f"coppock_{n}"] = combined.rolling(window=n, min_periods=n).apply(
            lambda w: np.dot(w, weights) / weights.sum(), raw=True
        )
        return out
