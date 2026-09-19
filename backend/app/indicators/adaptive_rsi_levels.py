"""
Adaptive RSI Levels.

Replaces RSI's fixed 70/30 overbought/oversold lines with levels that
adapt to RSI's OWN recent range: the midpoint between its trailing
highest and lowest reading, pulled in toward that midpoint by a
discount percentage. An instrument whose RSI rarely leaves 40-60 gets
tight adaptive levels that actually trigger; one that regularly spans
20-90 gets wide ones -- both read on the same self-relative basis
instead of one-size-fits-all fixed lines. Distinct from
app.indicators.ema_distance_percentile_rank (a percentile-rank
transform, not a level-narrowing discount off the historical range).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("adaptive_rsi_levels")
class AdaptiveRSILevels(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adaptive_rsi_levels",
            display_name="Adaptive RSI Levels",
            description="Overbought/oversold levels that adapt to RSI's own trailing high/low range, narrowed toward the midpoint by a discount percentage, instead of fixed 70/30 lines.",
            category="momentum",
            default_params={
                "rsi_period": 14,
                "range_lookback": 200,
                "discount_pct": 5.0,
                "short_ma_period": 9,
                "long_ma_period": 50,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["rsi_period"]

        delta = out["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        avg_loss = loss.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        lb = p["range_lookback"]
        rsi_max = rsi.rolling(lb, min_periods=lb).max()
        rsi_min = rsi.rolling(lb, min_periods=lb).min()
        center = (rsi_max + rsi_min) / 2
        upper_level = rsi_max - center * 2 * p["discount_pct"] / 100
        lower_level = rsi_min + center * 2 * p["discount_pct"] / 100

        short_ma = rsi.rolling(p["short_ma_period"], min_periods=p["short_ma_period"]).mean()
        long_ma = rsi.rolling(p["long_ma_period"], min_periods=p["long_ma_period"]).mean()

        out[f"rsi_{n}"] = rsi
        out["adaptive_rsi_upper"] = upper_level
        out["adaptive_rsi_lower"] = lower_level
        out["adaptive_rsi_center"] = center
        out["adaptive_rsi_short_ma"] = short_ma
        out["adaptive_rsi_long_ma"] = long_ma
        out["adaptive_rsi_overbought"] = rsi >= upper_level
        out["adaptive_rsi_oversold"] = rsi <= lower_level
        return out
