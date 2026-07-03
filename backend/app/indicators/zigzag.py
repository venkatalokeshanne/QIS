"""
Zig Zag.

Connects successive swing highs/lows, filtering out any move smaller
than `deviation_pct` -- so minor retracements are ignored and only
"real" swings are marked. Recursive by nature (each new confirmed pivot
depends on the direction/level of the last one), not a single
vectorized rolling window.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("zigzag")
class ZigZag(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="zigzag",
            display_name="Zig Zag",
            description="Connects confirmed swing highs/lows, filtering out moves smaller than a minimum percentage.",
            category="price_action",
            default_params={"deviation_pct": 5.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        threshold = p["deviation_pct"] / 100

        high = out["high"].to_numpy()
        low = out["low"].to_numpy()
        n = len(out)
        zigzag = np.full(n, np.nan)

        if n == 0:
            out["zigzag"] = zigzag
            return out

        last_pivot_idx = 0
        last_pivot_price = high[0]
        direction = None  # None until the first swing is confirmed; then 1 (up) or -1 (down)

        for i in range(1, n):
            if direction != -1:
                move_up = (high[i] - last_pivot_price) / last_pivot_price
                if high[i] > last_pivot_price:
                    last_pivot_price = high[i]
                    last_pivot_idx = i
                elif (last_pivot_price - low[i]) / last_pivot_price >= threshold:
                    zigzag[last_pivot_idx] = last_pivot_price
                    direction = -1
                    last_pivot_price = low[i]
                    last_pivot_idx = i
                    continue

            if direction != 1:
                if low[i] < last_pivot_price:
                    last_pivot_price = low[i]
                    last_pivot_idx = i
                elif (high[i] - last_pivot_price) / last_pivot_price >= threshold:
                    zigzag[last_pivot_idx] = last_pivot_price
                    direction = 1
                    last_pivot_price = high[i]
                    last_pivot_idx = i

        zigzag[last_pivot_idx] = last_pivot_price
        out["zigzag"] = zigzag
        return out
