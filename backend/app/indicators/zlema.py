"""Zero Lag EMA (John Ehlers & Ric Way) — an EMA applied to a de-lagged price series (price plus its own recent momentum), reducing the lag inherent to any EMA."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("zlema")
class ZeroLagEMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="zlema",
            display_name="Zero Lag EMA",
            description="EMA of a de-lagged price series (price + its own recent momentum) -- reduces EMA's inherent lag.",
            category="overlap",
            default_params={"period": 20, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        lag = (n - 1) // 2
        de_lagged = 2 * src - src.shift(lag)
        out[f"zlema_{n}"] = de_lagged.ewm(span=n, adjust=False).mean()
        return out
