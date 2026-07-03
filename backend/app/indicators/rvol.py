"""Relative Volume — current volume vs. its own rolling average."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rvol")
class RelativeVolume(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rvol",
            display_name="Relative Volume",
            description="Current volume divided by its rolling average; 1.0 = typical, >1 = above-average activity.",
            category="volume",
            default_params={"period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        avg_volume = out["volume"].rolling(window=p["period"], min_periods=p["period"]).mean()
        out[f"rvol_{p['period']}"] = out["volume"] / avg_volume.replace(0, np.nan)
        return out
