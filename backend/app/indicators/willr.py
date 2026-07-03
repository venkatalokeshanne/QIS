"""Williams %R (Larry Williams) — Close's position within the N-period high/low range, scaled -100 to 0."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("willr")
class WilliamsR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="willr",
            display_name="Williams %R",
            description="Close's position within the N-period high/low range, scaled -100 (low) to 0 (high).",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        highest_high = out["high"].rolling(window=n, min_periods=n).max()
        lowest_low = out["low"].rolling(window=n, min_periods=n).min()
        rng = (highest_high - lowest_low).replace(0, np.nan)

        out[f"willr_{n}"] = -100 * (highest_high - out["close"]) / rng
        return out
