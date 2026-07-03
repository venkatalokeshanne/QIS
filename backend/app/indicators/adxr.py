"""Average Directional Index Rating (J. Welles Wilder) — average of the current ADX and ADX from N periods ago, smoothing out ADX's own whipsaws."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("adxr")
class ADXR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adxr",
            display_name="Average Directional Index Rating",
            description="Average of the current ADX and ADX from N periods ago -- smooths out ADX's own whipsaws.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        dm = directional_movement(out, n)
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        adx = wilders_smooth(dx, n)

        out[f"adxr_{n}"] = (adx + adx.shift(n)) / 2
        return out
