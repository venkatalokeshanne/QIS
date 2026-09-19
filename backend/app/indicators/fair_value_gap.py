"""
Fair Value Gap (FVG).

A three-bar imbalance: a bullish FVG forms when bar[i-2]'s high sits
below bar[i]'s low (the middle bar's impulsive move left an
un-traded gap between them); a bearish FVG mirrors this on the
downside. This is the standard, widely-published definition used
across independent trading-education sources (not any one platform's
proprietary formula) -- the gap zone is flagged on the bar that
confirms it (bar[i]).

require_same_color_run (off by default) adds a stricter, commonly-used
variant: all 3 bars must share the same candle color matching the
gap's direction (3 green candles for a bullish gap, 3 red for a
bearish one) -- filters out gaps formed by a mixed-direction 3-bar
sequence.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("fair_value_gap")
class FairValueGap(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fair_value_gap",
            display_name="Fair Value Gap",
            description="A 3-bar imbalance where the middle bar's move leaves an un-traded gap between bar[i-2] and bar[i].",
            category="price_action",
            default_params={"require_same_color_run": False},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        prior_high = out["high"].shift(2)
        prior_low = out["low"].shift(2)

        bullish_fvg = out["low"] > prior_high
        bearish_fvg = out["high"] < prior_low

        if p["require_same_color_run"]:
            is_green, is_red = out["close"] > out["open"], out["close"] < out["open"]
            three_green = is_green & is_green.shift(1) & is_green.shift(2)
            three_red = is_red & is_red.shift(1) & is_red.shift(2)
            bullish_fvg = bullish_fvg & three_green
            bearish_fvg = bearish_fvg & three_red

        out["fvg_bullish_top"] = out["low"].where(bullish_fvg)
        out["fvg_bullish_bottom"] = prior_high.where(bullish_fvg)
        out["fvg_bearish_top"] = prior_low.where(bearish_fvg)
        out["fvg_bearish_bottom"] = out["high"].where(bearish_fvg)
        return out
