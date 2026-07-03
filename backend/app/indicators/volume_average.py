"""Volume Average — simple rolling mean of volume, the baseline most relative-volume/volume-filter logic compares against."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("volume_average")
class VolumeAverage(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volume_average",
            display_name="Volume Average",
            description="Simple rolling mean of volume over a trailing N-period window.",
            category="volume",
            default_params={"period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        out[f"volume_avg_{p['period']}"] = out["volume"].rolling(window=p["period"], min_periods=p["period"]).mean()
        return out
