"""
Order Blocks (simplified).

A widely-used heuristic reading: the last down-candle immediately
before a strong up-impulse becomes a "bullish order block" (its
high-to-low range is treated as future support); the mirror applies
to bearish order blocks. "Strong impulse" here means the close within
`impulse_bars` afterward moves at least `impulse_atr_multiple` ATRs
away from that candle's own close -- a concrete, checkable stand-in
for the more subjective "aggressive move" definitions used across
different trading-education sources.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("order_blocks")
class OrderBlocks(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="order_blocks",
            display_name="Order Blocks",
            description="The last down-candle before a strong up-impulse (or up-candle before a strong down-impulse), flagged as a future support/resistance zone.",
            category="price_action",
            default_params={"atr_period": 14, "impulse_bars": 5, "impulse_atr_multiple": 2.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        atr = wilders_smooth(true_range(out), p["atr_period"])
        lookahead, mult = p["impulse_bars"], p["impulse_atr_multiple"]

        close = out["close"].to_numpy()
        open_ = out["open"].to_numpy()
        high = out["high"].to_numpy()
        low = out["low"].to_numpy()
        atr_arr = atr.to_numpy()
        n = len(out)

        bullish_ob_top = np.full(n, np.nan)
        bullish_ob_bottom = np.full(n, np.nan)
        bearish_ob_top = np.full(n, np.nan)
        bearish_ob_bottom = np.full(n, np.nan)

        for i in range(n - lookahead):
            if np.isnan(atr_arr[i]) or atr_arr[i] == 0:
                continue
            future_close = close[i + 1 : i + 1 + lookahead]
            if len(future_close) == 0:
                continue

            is_down_candle = close[i] < open_[i]
            is_up_candle = close[i] > open_[i]

            if is_down_candle and (future_close.max() - close[i]) >= mult * atr_arr[i]:
                bullish_ob_top[i] = high[i]
                bullish_ob_bottom[i] = low[i]

            if is_up_candle and (close[i] - future_close.min()) >= mult * atr_arr[i]:
                bearish_ob_top[i] = high[i]
                bearish_ob_bottom[i] = low[i]

        out["bullish_ob_top"] = bullish_ob_top
        out["bullish_ob_bottom"] = bullish_ob_bottom
        out["bearish_ob_top"] = bearish_ob_top
        out["bearish_ob_bottom"] = bearish_ob_bottom
        return out
