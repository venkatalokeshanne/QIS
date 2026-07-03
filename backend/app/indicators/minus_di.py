"""Minus Directional Indicator (-DI, J. Welles Wilder) — Wilder-smoothed downward directional movement, normalized by true range."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement
from app.indicators.registry import indicator_registry


@indicator_registry.register("minus_di")
class MinusDI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="minus_di",
            display_name="Minus Directional Indicator (-DI)",
            description="Wilder-smoothed downward directional movement, normalized by true range (0-100).",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        dm = directional_movement(out, p["period"])
        out[f"minus_di_{p['period']}"] = dm["minus_di"]
        return out
