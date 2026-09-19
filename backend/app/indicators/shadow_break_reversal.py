"""Shadow Break Reversal — a bar that wicks beyond the prior bar's high but closes below its low (bearish rejection), or wicks beyond the prior low but closes above its high (bullish rejection): a more aggressive rejection than a plain engulfing bar, since the wick alone breaks one extreme and the close alone breaks the other."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("shadow_break_reversal")
class ShadowBreakReversal(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="shadow_break_reversal",
            display_name="Shadow Break Reversal",
            description="A bar whose wick breaks the prior bar's high (or low) but closes beyond the prior bar's OPPOSITE extreme -- an aggressive rejection.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        prev_high, prev_low = out["high"].shift(1), out["low"].shift(1)

        out["shadow_break_bearish"] = (out["high"] > prev_high) & (out["close"] < prev_low)
        out["shadow_break_bullish"] = (out["low"] < prev_low) & (out["close"] > prev_high)
        return out
