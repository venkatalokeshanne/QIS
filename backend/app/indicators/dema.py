"""Double Exponential Moving Average (Patrick Mulloy) — reduces EMA lag by removing the "lag of the lag"."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("dema")
class DEMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dema",
            display_name="Double Exponential Moving Average",
            description="2*EMA(price) - EMA(EMA(price)) -- reduces lag versus a plain EMA.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        ema1 = out[p["source"]].ewm(span=n, adjust=False).mean()
        ema2 = ema1.ewm(span=n, adjust=False).mean()
        out[f"dema_{n}"] = 2 * ema1 - ema2
        return out
