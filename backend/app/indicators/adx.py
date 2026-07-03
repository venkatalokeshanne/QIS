"""Average Directional Index (J. Welles Wilder) — Wilder-smoothed DX; trend-strength (not direction) gauge."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("adx")
class ADX(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adx",
            display_name="Average Directional Index",
            description="Wilder-smoothed DX; measures trend strength regardless of direction (0-100).",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        dm = directional_movement(out, p["period"])
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        out[f"adx_{p['period']}"] = wilders_smooth(dx, p["period"])
        return out
