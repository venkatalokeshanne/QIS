"""Historical Volatility — annualized standard deviation of log returns over a trailing window, the standard statistical volatility measure (distinct from ATR's range-based approach)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("historical_volatility")
class HistoricalVolatility(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="historical_volatility",
            display_name="Historical Volatility",
            description="Annualized standard deviation of log returns over a trailing window.",
            category="volatility",
            default_params={"period": 20, "bars_per_year": 252, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        log_return = np.log(src / src.shift(1))
        rolling_std = log_return.rolling(window=n, min_periods=n).std()

        out[f"hv_{n}"] = rolling_std * np.sqrt(p["bars_per_year"]) * 100
        return out
