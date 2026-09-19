"""Gravestone Doji — a small body, a small (or absent) lower wick, and a large upper wick: a bearish reversal pattern typically found near tops.

The source script also gates on the CURRENT bar being an hourly bar and
within the final 10 minutes before its close (a live-trading-only
concern -- a backtest only ever sees completed bars, so there's no
"time remaining" to gate on). Only the candlestick-shape criteria are
ported here.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("gravestone_doji")
class GravestoneDoji(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="gravestone_doji",
            display_name="Gravestone Doji",
            description="Small body, small/absent lower wick, large upper wick -- a bearish reversal pattern typically found near tops.",
            category="price_action",
            default_params={"max_body_pct": 0.20, "min_wick_to_body": 2.0, "max_lower_wick_pct": 0.10},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        max_body_pct, wick_ratio, max_lower_pct = p["max_body_pct"], p["min_wick_to_body"], p["max_lower_wick_pct"]

        rng = out["high"] - out["low"]
        body = (out["close"] - out["open"]).abs()
        upper_wick = out["high"] - out[["open", "close"]].max(axis=1)
        lower_wick = out[["open", "close"]].min(axis=1) - out["low"]

        body_pct = (body / rng).where(rng > 0, 0.0)
        lower_pct = (lower_wick / rng).where(rng > 0, 0.0)

        small_body = body_pct <= max_body_pct
        large_upper_wick = (upper_wick >= body * wick_ratio).where(body > 0, upper_wick > 0)
        small_lower_wick = lower_pct <= max_lower_pct

        out["gravestone_doji"] = (rng > 0) & small_body & large_upper_wick & small_lower_wick
        return out
