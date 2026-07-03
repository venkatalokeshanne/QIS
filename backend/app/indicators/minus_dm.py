"""Minus Directional Movement (-DM, J. Welles Wilder) — Wilder-smoothed raw downward directional movement, before normalization into -DI."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement
from app.indicators.registry import indicator_registry


@indicator_registry.register("minus_dm")
class MinusDM(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="minus_dm",
            display_name="Minus Directional Movement (-DM)",
            description="Wilder-smoothed raw downward directional movement, before normalization into -DI.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        dm = directional_movement(out, p["period"])
        out[f"minus_dm_{p['period']}"] = dm["minus_dm"]
        return out
