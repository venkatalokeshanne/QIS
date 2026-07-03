"""Force Index (Alexander Elder) — price change times volume, smoothed -- combines direction, magnitude, and conviction into one reading."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("force_index")
class ForceIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="force_index",
            display_name="Force Index",
            description="Price change * volume, smoothed -- combines direction, magnitude, and conviction.",
            category="volume",
            default_params={"period": 13},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        raw_force = out["close"].diff() * out["volume"]
        out[f"force_index_{n}"] = raw_force.ewm(span=n, adjust=False, min_periods=n).mean()
        return out
