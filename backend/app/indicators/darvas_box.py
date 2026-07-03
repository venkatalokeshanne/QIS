"""
Darvas Box (Nicolas Darvas).

A simplified, widely-used algorithmic reading of Darvas's box theory:
track the trailing N-bar high as a candidate "box top"; once that high
has held (not been exceeded) for `confirmation_bars` bars, lock it in
as the box top, and the box bottom becomes the lowest low since that
top was set. A new, higher N-bar high resets the box.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("darvas_box")
class DarvasBox(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="darvas_box",
            display_name="Darvas Box",
            description="Box top/bottom levels from a trailing high that has held for N bars, Darvas box-theory style.",
            category="price_action",
            default_params={"period": 20, "confirmation_bars": 3},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, confirm = p["period"], p["confirmation_bars"]

        rolling_high = out["high"].rolling(window=n, min_periods=n).max()
        low_arr = out["low"].to_numpy()
        candidate_arr = rolling_high.to_numpy()

        box_top = np.full(len(out), np.nan)
        box_bottom = np.full(len(out), np.nan)

        current_top = np.nan
        bars_held = 0
        box_low_since_top = np.nan

        for i in range(len(out)):
            candidate = candidate_arr[i]
            if np.isnan(candidate):
                continue

            if np.isnan(current_top) or candidate > current_top:
                current_top = candidate
                bars_held = 0
                box_low_since_top = low_arr[i]
            else:
                bars_held += 1
                box_low_since_top = min(box_low_since_top, low_arr[i])

            if bars_held >= confirm:
                box_top[i] = current_top
                box_bottom[i] = box_low_since_top

        out[f"darvas_box_top_{n}"] = box_top
        out[f"darvas_box_bottom_{n}"] = box_bottom
        return out
