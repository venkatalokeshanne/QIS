"""Hilbert Transform - Trend vs. Cycle Mode (John Ehlers) — binary classification of whether the dominant-cycle detector considers the market trending or cycling."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_trendmode")
class HTTrendMode(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_trendmode",
            display_name="Hilbert Transform - Trend vs. Cycle Mode",
            description="Binary read (1/0) of whether the dominant-cycle detector considers the market trending or cycling.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_trendmode"] = ht["trendmode"]
        return out
