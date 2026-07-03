"""
Market Structure — Break of Structure (BOS) / Change of Character (CHoCH).

Tracks a running sequence of confirmed swing highs/lows (via the same
fractal-style rolling-window swing detection used elsewhere) to
maintain a simple trend state: uptrend once a higher high AND higher
low are confirmed, downtrend once a lower high AND lower low are
confirmed. A close beyond the most recent opposing swing point is a
"structure break" -- BOS if it continues the existing trend state,
CHoCH if it's the first one to contradict it (the trend state then
flips).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("market_structure")
class MarketStructure(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="market_structure",
            display_name="Market Structure (BOS / CHoCH)",
            description="Classifies each swing-point break as a Break of Structure (trend continuation) or Change of Character (trend flip).",
            category="price_action",
            default_params={"swing_range": 5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left = right = p["swing_range"]
        window = left + right + 1

        def is_swing_high(w: pd.Series) -> bool:
            return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

        def is_swing_low(w: pd.Series) -> bool:
            return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

        swing_high_mask = (
            out["high"].rolling(window=window, min_periods=window).apply(is_swing_high, raw=False).astype(bool)
        )
        swing_low_mask = (
            out["low"].rolling(window=window, min_periods=window).apply(is_swing_low, raw=False).astype(bool)
        )
        swing_high_mask = swing_high_mask.shift(-right, fill_value=False)
        swing_low_mask = swing_low_mask.shift(-right, fill_value=False)

        swing_high_price = out["high"].where(swing_high_mask)
        swing_low_price = out["low"].where(swing_low_mask)
        close = out["close"].to_numpy()
        n = len(out)

        bos = np.zeros(n, dtype=bool)
        choch = np.zeros(n, dtype=bool)

        trend = 0  # 0 = undetermined, 1 = uptrend, -1 = downtrend
        last_confirmed_high = np.nan
        last_confirmed_low = np.nan
        prev_confirmed_high = np.nan
        prev_confirmed_low = np.nan
        broken_high = np.nan  # most recent swing high not yet broken
        broken_low = np.nan  # most recent swing low not yet broken

        swing_high_arr = swing_high_price.to_numpy()
        swing_low_arr = swing_low_price.to_numpy()

        for i in range(n):
            if not np.isnan(swing_high_arr[i]):
                prev_confirmed_high = last_confirmed_high
                last_confirmed_high = swing_high_arr[i]
                broken_high = last_confirmed_high
            if not np.isnan(swing_low_arr[i]):
                prev_confirmed_low = last_confirmed_low
                last_confirmed_low = swing_low_arr[i]
                broken_low = last_confirmed_low

            # A close beyond the most recent un-broken swing high/low is a structure break.
            if not np.isnan(broken_high) and close[i] > broken_high:
                is_continuation = trend == 1
                if trend == 0 or is_continuation:
                    bos[i] = True
                else:
                    choch[i] = True
                trend = 1
                broken_high = np.nan  # consumed -- wait for the next confirmed swing high

            elif not np.isnan(broken_low) and close[i] < broken_low:
                is_continuation = trend == -1
                if trend == 0 or is_continuation:
                    bos[i] = True
                else:
                    choch[i] = True
                trend = -1
                broken_low = np.nan

        out["market_structure_bos"] = bos
        out["market_structure_choch"] = choch
        return out
