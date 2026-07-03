"""Hilbert Transform - Instantaneous Trendline (John Ehlers) — a smoothed trendline whose lookback adapts to the detected dominant cycle length."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_trendline")
class HTTrendline(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_trendline",
            display_name="Hilbert Transform - Instantaneous Trendline",
            description="A smoothed trendline whose lookback adapts to the detected dominant cycle length.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_trendline"] = ht["trendline"]
        return out
