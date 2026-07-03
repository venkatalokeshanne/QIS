"""On-Balance Volume (Joseph Granville) — running total of volume, added on up bars and subtracted on down bars."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("obv")
class OBV(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="obv",
            display_name="On-Balance Volume",
            description="Running total of volume, added on up closes and subtracted on down closes.",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        direction = np.sign(out["close"].diff()).fillna(0)
        out["obv"] = (direction * out["volume"]).cumsum()
        return out
