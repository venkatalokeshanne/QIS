"""Triple Exponential Moving Average (Patrick Mulloy) — further lag reduction beyond DEMA using a third EMA pass."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("tema")
class TEMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="tema",
            display_name="Triple Exponential Moving Average",
            description="3*EMA - 3*EMA(EMA) + EMA(EMA(EMA)) -- less lag than DEMA.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        ema1 = out[p["source"]].ewm(span=n, adjust=False).mean()
        ema2 = ema1.ewm(span=n, adjust=False).mean()
        ema3 = ema2.ewm(span=n, adjust=False).mean()
        out[f"tema_{n}"] = 3 * ema1 - 3 * ema2 + ema3
        return out
