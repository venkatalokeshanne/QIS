"""Chandelier Exit (Chuck LeBeau) — an ATR-based trailing stop anchored to the highest high (long side) or lowest low (short side) over a trailing window."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("chandelier_exit")
class ChandelierExit(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="chandelier_exit",
            display_name="Chandelier Exit",
            description="ATR-based trailing stop anchored to the highest high (long) or lowest low (short) over a trailing window.",
            category="volatility",
            default_params={"period": 22, "atr_multiple": 3.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, mult = p["period"], p["atr_multiple"]

        atr = wilders_smooth(true_range(out), n)
        highest_high = out["high"].rolling(window=n, min_periods=n).max()
        lowest_low = out["low"].rolling(window=n, min_periods=n).min()

        out[f"chandelier_long_{n}"] = highest_high - mult * atr
        out[f"chandelier_short_{n}"] = lowest_low + mult * atr
        return out
