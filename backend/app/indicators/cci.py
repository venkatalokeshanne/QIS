"""Commodity Channel Index (Donald Lambert) — deviation of typical price from its own SMA, scaled by mean absolute deviation."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("cci")
class CCI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="cci",
            display_name="Commodity Channel Index",
            description="Deviation of typical price from its own SMA, scaled by mean absolute deviation.",
            category="momentum",
            default_params={"period": 20},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        sma = typical_price.rolling(window=n, min_periods=n).mean()
        mean_dev = typical_price.rolling(window=n, min_periods=n).apply(lambda w: (w - w.mean()).abs().mean(), raw=False)

        out[f"cci_{n}"] = (typical_price - sma) / (0.015 * mean_dev.replace(0, np.nan))
        return out
