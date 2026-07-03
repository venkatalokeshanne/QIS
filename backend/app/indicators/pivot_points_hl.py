"""Pivot High/Low — a bar counts as a swing pivot only once N bars on both sides fail to exceed it, confirming the swing after the fact."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("pivot_points_hl")
class PivotPointsHL(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="pivot_points_hl",
            display_name="Pivot High/Low",
            description="Confirmed swing high/low points -- a bar's high (low) exceeds N bars on both sides.",
            category="price_action",
            default_params={"left_range": 5, "right_range": 5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        left, right = p["left_range"], p["right_range"]
        window = left + right + 1

        def is_pivot_high(w: pd.Series) -> bool:
            return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

        def is_pivot_low(w: pd.Series) -> bool:
            return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

        pivot_high_mask = (
            out["high"].rolling(window=window, min_periods=window).apply(is_pivot_high, raw=False).astype(bool)
        )
        pivot_low_mask = (
            out["low"].rolling(window=window, min_periods=window).apply(is_pivot_low, raw=False).astype(bool)
        )
        # The rolling window is right-aligned, but the pivot itself sits
        # `right` bars BEFORE the window's last bar (needs `right` bars of
        # confirmation after it) -- shift the flag back to the pivot bar.
        pivot_high_mask = pivot_high_mask.shift(-right).fillna(False)
        pivot_low_mask = pivot_low_mask.shift(-right).fillna(False)

        out["pivot_points_hl_high"] = out["high"].where(pivot_high_mask)
        out["pivot_points_hl_low"] = out["low"].where(pivot_low_mask)
        return out
