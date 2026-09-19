"""
Volume Exhaustion Trend Line.

Tracks swing-confirmed trend direction (higher high + higher low =
uptrend, lower high + lower low = downtrend, same as
app.indicators.market_structure) and hugs price with an ATR-offset
line on the trend's supporting side -- but flips that line to the
OPPOSING side the moment a new swing pivot confirms on BELOW-average
volume while the prior pivot of that type was strong: a weak pivot
right after a strong one reads as the trend running out of
participation, flagged before the trend formally breaks. The line
snaps back once a fresh strong pivot reconfirms the trend.

The persistent "pending reversal" state depends on comparing each new
pivot's volume to the running trend/strength history, so this is
computed with an explicit bar-by-bar loop.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("volume_exhaustion_trend_line")
class VolumeExhaustionTrendLine(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volume_exhaustion_trend_line",
            display_name="Volume Exhaustion Trend Line",
            description="An ATR-offset trend line that flips to the opposing side when a confirmed swing pivot arrives on below-average volume right after a strong one -- flagging fading participation before the trend structurally breaks.",
            category="trend",
            default_params={
                "pivot_left": 20,
                "pivot_right": 1,
                "volume_ma_period": 20,
                "line_ma_period": 20,
                "atr_period": 14,
                "atr_multiple": 1.5,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left, right = p["pivot_left"], p["pivot_right"]
        window = left + right + 1

        vol_ma = out["volume"].rolling(p["volume_ma_period"], min_periods=p["volume_ma_period"]).mean()
        basis = out["close"].rolling(p["line_ma_period"], min_periods=p["line_ma_period"]).mean()
        atr = wilders_smooth(true_range(out), p["atr_period"])
        upper_band = basis + p["atr_multiple"] * atr
        lower_band = basis - p["atr_multiple"] * atr

        def pivot_mask(values: pd.Series, is_high: bool) -> np.ndarray:
            def check(w: np.ndarray) -> bool:
                target = w.max() if is_high else w.min()
                return w[left] == target and (w == w[left]).sum() == 1

            mask = values.rolling(window=window, min_periods=window).apply(check, raw=True)
            return mask.fillna(0).astype(bool).to_numpy()

        ph_mask = pivot_mask(out["high"], is_high=True)
        pl_mask = pivot_mask(out["low"], is_high=False)
        high_arr, low_arr = out["high"].to_numpy(), out["low"].to_numpy()
        volume_arr, vol_ma_arr = out["volume"].to_numpy(), vol_ma.to_numpy()
        upper_arr, lower_arr, close_arr = upper_band.to_numpy(), lower_band.to_numpy(), out["close"].to_numpy()

        n = len(out)
        last_high = prev_high = np.nan
        last_low = prev_low = np.nan
        last_high_was_strong = False
        last_low_was_strong = False
        has_last_high = has_last_low = False
        pending_up = pending_down = False
        trend = "none"

        line_value = np.full(n, np.nan)

        for i in range(n):
            if ph_mask[i]:
                pivot_bar = i - right
                is_weak = volume_arr[pivot_bar] < vol_ma_arr[pivot_bar]
                if trend == "up":
                    if is_weak:
                        if pending_up or (has_last_high and last_high_was_strong):
                            pending_up = True
                    else:
                        pending_up = False
                else:
                    pending_up = False

                last_high_was_strong = not is_weak
                has_last_high = True
                prev_high, last_high = last_high, high_arr[pivot_bar]

                if not np.isnan(prev_high) and not np.isnan(last_low) and not np.isnan(prev_low):
                    if last_high > prev_high and last_low > prev_low:
                        new_trend = "up"
                    elif last_high < prev_high and last_low < prev_low:
                        new_trend = "down"
                    else:
                        new_trend = "none"
                    if new_trend != "up":
                        pending_up = False
                    if new_trend != "down":
                        pending_down = False
                    trend = new_trend

            if pl_mask[i]:
                pivot_bar = i - right
                is_weak = volume_arr[pivot_bar] < vol_ma_arr[pivot_bar]
                if trend == "down":
                    if is_weak:
                        if pending_down or (has_last_low and last_low_was_strong):
                            pending_down = True
                    else:
                        pending_down = False
                else:
                    pending_down = False

                last_low_was_strong = not is_weak
                has_last_low = True
                prev_low, last_low = last_low, low_arr[pivot_bar]

                if not np.isnan(prev_high) and not np.isnan(last_high) and not np.isnan(prev_low):
                    if last_high > prev_high and last_low > prev_low:
                        new_trend = "up"
                    elif last_high < prev_high and last_low < prev_low:
                        new_trend = "down"
                    else:
                        new_trend = "none"
                    if new_trend != "up":
                        pending_up = False
                    if new_trend != "down":
                        pending_down = False
                    trend = new_trend

            if trend == "up":
                line_value[i] = upper_arr[i] if pending_up else lower_arr[i]
            elif trend == "down":
                line_value[i] = lower_arr[i] if pending_down else upper_arr[i]

        out["volume_exhaustion_line"] = line_value
        out["volume_exhaustion_bullish"] = line_value < close_arr
        return out
