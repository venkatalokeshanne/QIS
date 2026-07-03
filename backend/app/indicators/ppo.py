"""Percentage Price Oscillator — same idea as APO, expressed as a percentage of the slow MA so it's comparable across symbols/price levels."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("ppo")
class PPO(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ppo",
            display_name="Percentage Price Oscillator",
            description="(EMA(fast) - EMA(slow)) / EMA(slow) * 100 -- APO as a percentage, comparable across symbols.",
            category="momentum",
            default_params={"fast_period": 12, "slow_period": 26, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        fast = src.ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        slow = src.ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        out[f"ppo_{p['fast_period']}_{p['slow_period']}"] = (fast - slow) / slow.replace(0, np.nan) * 100
        return out
