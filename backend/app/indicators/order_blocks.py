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

Causality: whether candle i qualifies depends on candles AFTER it
(i+1 .. i+impulse_bars) -- that's inherent to the definition, not a
bug. The bug would be recording the zone AT candle i itself, which is
what an earlier version of this file did: a strategy backtesting
against that recording could "trade" the zone on candles between i and
its actual confirmation bar, using information nobody -- backtest or
live -- could have had yet at that point in time. Recorded at the bar
where the threshold is genuinely first crossed instead (mirroring
app.indicators.confluence_order_block's confirm_index pattern), the
zone's geometry still comes from candle i's own high/low, but nothing
downstream (order_block_retest's forward-fill, in particular) can mark
it "active" before that's actually knowable.
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
            a = atr_arr[i]
            if np.isnan(a) or a == 0:
                continue

            is_down_candle = close[i] < open_[i]
            is_up_candle = close[i] > open_[i]
            if not (is_down_candle or is_up_candle):
                continue

            threshold = mult * a

            # First bar the threshold is genuinely crossed -- not the
            # window's eventual max/min regardless of when it happens,
            # and never candle i itself. Matches confluence_order_block's
            # own "do not keep scanning for a better confirmation" rule.
            confirm_idx = None
            if is_down_candle:
                running_max = -np.inf
                for k in range(i + 1, i + 1 + lookahead):
                    running_max = max(running_max, close[k])
                    if running_max - close[i] >= threshold:
                        confirm_idx = k
                        break
            else:
                running_min = np.inf
                for k in range(i + 1, i + 1 + lookahead):
                    running_min = min(running_min, close[k])
                    if close[i] - running_min >= threshold:
                        confirm_idx = k
                        break

            if confirm_idx is None:
                continue

            if is_down_candle:
                bullish_ob_top[confirm_idx] = high[i]
                bullish_ob_bottom[confirm_idx] = low[i]
            else:
                bearish_ob_top[confirm_idx] = high[i]
                bearish_ob_bottom[confirm_idx] = low[i]

        out["bullish_ob_top"] = bullish_ob_top
        out["bullish_ob_bottom"] = bullish_ob_bottom
        out["bearish_ob_top"] = bearish_ob_top
        out["bearish_ob_bottom"] = bearish_ob_bottom
        return out
