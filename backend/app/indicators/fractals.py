"""Fractals (Bill Williams) — a bar's high (low) counts as a fractal once it exceeds the 2 bars on both sides, the classic Williams swing-point definition (same underlying idea as pivot_points_hl, with Williams' own fixed 2-bar-each-side convention)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("fractals")
class Fractals(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fractals",
            display_name="Fractals",
            description="Bill Williams' swing-point definition: a high (low) that exceeds the 2 bars on both sides.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        left = right = 2
        window = left + right + 1

        def is_fractal_high(w: pd.Series) -> bool:
            return w.iloc[left] == w.max() and (w == w.iloc[left]).sum() == 1

        def is_fractal_low(w: pd.Series) -> bool:
            return w.iloc[left] == w.min() and (w == w.iloc[left]).sum() == 1

        fractal_high_mask = (
            out["high"].rolling(window=window, min_periods=window).apply(is_fractal_high, raw=False).astype(bool)
        )
        fractal_low_mask = (
            out["low"].rolling(window=window, min_periods=window).apply(is_fractal_low, raw=False).astype(bool)
        )
        fractal_high_mask = fractal_high_mask.shift(-right).fillna(False).astype(bool)
        fractal_low_mask = fractal_low_mask.shift(-right).fillna(False).astype(bool)

        out["fractal_high"] = out["high"].where(fractal_high_mask)
        out["fractal_low"] = out["low"].where(fractal_low_mask)
        return out
