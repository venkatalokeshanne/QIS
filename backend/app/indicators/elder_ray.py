"""Elder Ray / Bull Bear Power (Alexander Elder) — high/low vs. a trend EMA, measuring buyer/seller strength."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("elder_ray")
class ElderRay(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="elder_ray",
            display_name="Elder Ray (Bull/Bear Power)",
            description="Bull Power = high - EMA(close); Bear Power = low - EMA(close).",
            category="momentum",
            default_params={"period": 13},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        ema = out["close"].ewm(span=n, adjust=False, min_periods=n).mean()
        out[f"bull_power_{n}"] = out["high"] - ema
        out[f"bear_power_{n}"] = out["low"] - ema
        return out
