"""Volume Oscillator — percentage difference between a fast and slow moving average of volume, highlighting shifts in participation."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("volume_oscillator")
class VolumeOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volume_oscillator",
            display_name="Volume Oscillator",
            description="Percentage difference between a fast and slow moving average of volume.",
            category="volume",
            default_params={"fast_period": 5, "slow_period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        fast = out["volume"].rolling(window=p["fast_period"], min_periods=p["fast_period"]).mean()
        slow = out["volume"].rolling(window=p["slow_period"], min_periods=p["slow_period"]).mean()

        out[f"volume_osc_{p['fast_period']}_{p['slow_period']}"] = (fast - slow) / slow.replace(0, float("nan")) * 100
        return out
