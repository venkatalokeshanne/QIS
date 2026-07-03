"""Negative Volume Index (Paul Dysart, popularized by Norman Fosback) — a cumulative index that only updates on days volume FALLS, on the theory that "smart money" is more active on quiet days."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("nvi")
class NegativeVolumeIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="nvi",
            display_name="Negative Volume Index",
            description="Cumulative index that only updates on days volume falls vs. the prior day.",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        pct_change = out["close"].pct_change()
        volume_fell = out["volume"] < out["volume"].shift(1)

        nvi = np.full(len(out), np.nan)
        nvi[0] = 1000.0
        for i in range(1, len(out)):
            if volume_fell.iloc[i] and not np.isnan(pct_change.iloc[i]):
                nvi[i] = nvi[i - 1] * (1 + pct_change.iloc[i])
            else:
                nvi[i] = nvi[i - 1]

        out["nvi"] = nvi
        return out
