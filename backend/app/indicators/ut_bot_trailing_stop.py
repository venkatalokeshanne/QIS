"""
UT Bot Trailing Stop.

A single, recursive ATR-trailing-stop line that flips in place rather
than two separate long/short lines: while price is above the stop,
the stop only ever ratchets UP (max of its own prior value and
close-minus-nLoss); while below, it only ever ratchets DOWN. A close
crossing the stop flips which side it's trailing from. Distinct from
app.indicators.chandelier_exit (which trails off the rolling
highest-high/lowest-low, not off close) and app.indicators.supertrend
(which trails off the bar's median price +/- ATR, not a recursive
close-based ratchet) -- this is the well-known "UT Bot" construction,
a genuinely different recursive formula from either.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth, true_range
from app.indicators.registry import indicator_registry


@indicator_registry.register("ut_bot_trailing_stop")
class UTBotTrailingStop(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ut_bot_trailing_stop",
            display_name="UT Bot Trailing Stop",
            description="A single recursive ATR-trailing-stop line (close-based, not range-based) that ratchets favorably and flips sides on a close-through -- the classic 'UT Bot' construction.",
            category="trend",
            default_params={"atr_period": 10, "sensitivity": 1.2},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        atr = wilders_smooth(true_range(out), p["atr_period"])
        n_loss = p["sensitivity"] * atr

        close = out["close"].to_numpy()
        n_loss_arr = n_loss.to_numpy()
        n = len(out)

        stop = np.full(n, np.nan)
        position = np.zeros(n, dtype=np.int64)

        prev_stop = 0.0
        prev_close = np.nan
        prev_position = 0
        for i in range(n):
            if np.isnan(n_loss_arr[i]):
                stop[i] = np.nan
                position[i] = prev_position
                continue

            c = close[i]
            if not np.isnan(prev_close) and c > prev_stop and prev_close > prev_stop:
                cur_stop = max(prev_stop, c - n_loss_arr[i])
            elif not np.isnan(prev_close) and c < prev_stop and prev_close < prev_stop:
                cur_stop = min(prev_stop, c + n_loss_arr[i])
            elif c > prev_stop:
                cur_stop = c - n_loss_arr[i]
            else:
                cur_stop = c + n_loss_arr[i]

            stop[i] = cur_stop
            if not np.isnan(prev_close) and prev_close < prev_stop < c:
                cur_position = 1
            elif not np.isnan(prev_close) and prev_close > prev_stop > c:
                cur_position = -1
            else:
                cur_position = prev_position

            position[i] = cur_position
            prev_stop = cur_stop
            prev_close = c
            prev_position = cur_position

        position_series = pd.Series(position, index=out.index)
        prev_position_series = position_series.shift(1).fillna(0)
        out["ut_bot_stop"] = stop
        out["ut_bot_position"] = position_series
        out["ut_bot_buy_signal"] = (position_series == 1) & (prev_position_series != 1)
        out["ut_bot_sell_signal"] = (position_series == -1) & (prev_position_series != -1)
        return out
