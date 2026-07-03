"""Ease of Movement (Richard Arms) — price change per unit of volume, normalized by the bar's range; smoothed by a moving average."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("eom")
class EaseOfMovement(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="eom",
            display_name="Ease of Movement",
            description="Price change per unit of volume, normalized by the bar's range and smoothed.",
            category="volume",
            default_params={"period": 14, "volume_divisor": 100_000_000},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        midpoint_move = (out["high"] + out["low"]) / 2 - (out["high"].shift(1) + out["low"].shift(1)) / 2
        box_ratio = (out["volume"] / p["volume_divisor"]) / (out["high"] - out["low"]).replace(0, np.nan)
        raw_eom = midpoint_move / box_ratio.replace(0, np.nan)

        out[f"eom_{n}"] = raw_eom.rolling(window=n, min_periods=n).mean()
        return out
