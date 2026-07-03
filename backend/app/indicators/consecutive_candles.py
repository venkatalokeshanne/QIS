"""Consecutive Candles — running streak length of same-direction (close vs. open) bars."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("consecutive_candles")
class ConsecutiveCandles(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="consecutive_candles",
            display_name="Consecutive Candles",
            description="Running count of consecutive bullish (or bearish) closes, resetting whenever direction flips.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()

        direction = np.sign(out["close"] - out["open"])
        streak_group = (direction != direction.shift(1)).cumsum()
        streak_length = direction.groupby(streak_group).cumcount() + 1

        out["consecutive_candles"] = streak_length * direction
        return out
