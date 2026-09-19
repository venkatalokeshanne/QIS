"""Candle Range Sweep (Basic CRT) — a candle that sweeps beyond the prior bar's low (or high) but closes back inside its range on the opposite side, higher (or lower) than the prior close: a sweep-and-reclaim pattern, distinct from a full outside-close break (which closes beyond the prior extreme too, not back inside it)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("candle_range_sweep")
class CandleRangeSweep(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="candle_range_sweep",
            display_name="Candle Range Sweep (CRT)",
            description="A candle that sweeps beyond the prior bar's low/high but closes back inside its range, higher/lower than the prior close -- a sweep-and-reclaim pattern.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        prev_close, prev_low, prev_high = out["close"].shift(1), out["low"].shift(1), out["high"].shift(1)

        out["candle_range_sweep_bullish"] = (out["close"] > prev_close) & (out["low"] < prev_low) & (out["high"] < prev_high)
        out["candle_range_sweep_bearish"] = (out["close"] < prev_close) & (out["low"] > prev_low) & (out["high"] > prev_high)
        return out
