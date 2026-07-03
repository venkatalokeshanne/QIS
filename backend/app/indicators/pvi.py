"""Positive Volume Index (Norman Fosback) — the mirror of NVI: a cumulative index that only updates on days volume RISES, on the theory that "crowd" activity dominates on high-volume days."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("pvi")
class PositiveVolumeIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="pvi",
            display_name="Positive Volume Index",
            description="Cumulative index that only updates on days volume rises vs. the prior day.",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        pct_change = out["close"].pct_change()
        volume_rose = out["volume"] > out["volume"].shift(1)

        pvi = np.full(len(out), np.nan)
        pvi[0] = 1000.0
        for i in range(1, len(out)):
            if volume_rose.iloc[i] and not np.isnan(pct_change.iloc[i]):
                pvi[i] = pvi[i - 1] * (1 + pct_change.iloc[i])
            else:
                pvi[i] = pvi[i - 1]

        out["pvi"] = pvi
        return out
