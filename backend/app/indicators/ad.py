"""Accumulation/Distribution Line (Marc Chaikin) — cumulative money-flow-volume, based on where the close settled within each bar's range."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ad")
class AccumulationDistribution(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ad",
            display_name="Accumulation/Distribution Line",
            description="Cumulative money-flow-volume, based on where the close settled within each bar's range.",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        price_range = (out["high"] - out["low"]).replace(0, np.nan)
        money_flow_multiplier = ((out["close"] - out["low"]) - (out["high"] - out["close"])) / price_range
        money_flow_volume = (money_flow_multiplier * out["volume"]).fillna(0)

        out["ad"] = money_flow_volume.cumsum()
        return out
