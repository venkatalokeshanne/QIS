"""Money Flow Index (Gene Quong & Avrum Soudack) — a volume-weighted RSI, using typical price and raw volume as the money flow."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("mfi")
class MFI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="mfi",
            display_name="Money Flow Index",
            description="A volume-weighted RSI -- money flow (typical price * volume) instead of plain price change.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        money_flow = typical_price * out["volume"]
        price_up = typical_price.diff() > 0

        positive_flow = money_flow.where(price_up, 0.0)
        negative_flow = money_flow.where(~price_up, 0.0)

        positive_sum = positive_flow.rolling(window=n, min_periods=n).sum()
        negative_sum = negative_flow.rolling(window=n, min_periods=n).sum()
        money_ratio = positive_sum / negative_sum.replace(0, np.nan)

        out[f"mfi_{n}"] = 100 - (100 / (1 + money_ratio))
        return out
