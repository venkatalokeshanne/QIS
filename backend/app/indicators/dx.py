"""Directional Movement Index (DX, J. Welles Wilder) — normalized spread between +DI and -DI, the raw input ADX smooths."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement
from app.indicators.registry import indicator_registry


@indicator_registry.register("dx")
class DX(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dx",
            display_name="Directional Movement Index",
            description="100 * |+DI - -DI| / (+DI + -DI) -- the raw input ADX smooths over time.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        dm = directional_movement(out, p["period"])
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        out[f"dx_{p['period']}"] = 100 * (plus_di - minus_di).abs() / di_sum
        return out
