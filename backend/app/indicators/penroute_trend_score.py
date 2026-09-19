"""
Penroute Trend Score.

Five independent, cheap-to-check reads combined into a single 0-5
"is this actually trending" score -- deliberately not one clever
formula but five different lenses agreeing or disagreeing:

1. ADX above a threshold (classic trend-strength read).
2. Directional efficiency: net move over the lookback vs. the total
   path traveled to get there (close to 1 = a straight run, close to
   0 = pure chop covering the same net distance).
3. Closes lopsidedly on one side of an EMA over a trailing window
   (not just currently above/below it -- persistently so).
4. LOW sweep-reversion rate: when a bar breaks the prior bar's
   high/low, how often does it fail to hold there and revert back
   inside the prior range? A trending market breaks levels and keeps
   going; a ranging one keeps sweeping and snapping back.
5. ATR ratio: fast ATR meaningfully above slow ATR (volatility is
   currently expanding, not settled into a range-bound rhythm).

A score >= 3 reads as TREND, <= 1 as RANGE, otherwise MIXED.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement, true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("penroute_trend_score")
class PenrouteTrendScore(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="penroute_trend_score",
            display_name="Penroute Trend Score",
            description="A 0-5 composite of five independent trend reads (ADX, directional efficiency, EMA-side persistence, sweep-reversion rate, ATR expansion ratio) into a single TREND/MIXED/RANGE verdict.",
            category="trend",
            default_params={
                "adx_period": 14,
                "adx_threshold": 25.0,
                "efficiency_period": 20,
                "efficiency_threshold": 0.55,
                "ema_period": 50,
                "ema_lookback": 10,
                "ema_closes_needed": 8,
                "sweep_lookback": 20,
                "sweep_reversion_threshold": 0.40,
                "atr_fast_period": 5,
                "atr_slow_period": 20,
                "atr_ratio_threshold": 1.30,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        close, high, low = out["close"], out["high"], out["low"]

        dm = directional_movement(out, p["adx_period"])
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        adx = wilders_smooth(dx, p["adx_period"])
        c1 = adx > p["adx_threshold"]

        n_eff = p["efficiency_period"]
        net_move = (close - close.shift(n_eff)).abs()
        path_move = close.diff().abs().rolling(window=n_eff, min_periods=n_eff).sum()
        eff_ratio = net_move / path_move.replace(0, np.nan)
        c2 = eff_ratio > p["efficiency_threshold"]

        ema_val = close.ewm(span=p["ema_period"], adjust=False, min_periods=p["ema_period"]).mean()
        above = (close > ema_val).rolling(window=p["ema_lookback"], min_periods=p["ema_lookback"]).sum()
        same_side = np.maximum(above, p["ema_lookback"] - above)
        c3 = same_side >= p["ema_closes_needed"]

        prev_high, prev_low = high.shift(1), low.shift(1)
        broke_high = high > prev_high
        broke_low = low < prev_low
        broke = broke_high | broke_low

        reverted_both = (close <= prev_high) & (close >= prev_low)
        reverted_high_only = close <= prev_high
        reverted_low_only = close >= prev_low
        reverted = pd.Series(
            np.select(
                [broke_high & broke_low, broke_high, broke_low],
                [reverted_both, reverted_high_only, reverted_low_only],
                default=False,
            ),
            index=out.index,
        ).astype(bool)

        n_sweep = p["sweep_lookback"]
        breaks = broke.astype(int).rolling(window=n_sweep, min_periods=n_sweep).sum()
        reverts = reverted.astype(int).rolling(window=n_sweep, min_periods=n_sweep).sum()
        rev_rate = reverts / breaks.replace(0, np.nan)
        c4 = rev_rate.notna() & (breaks >= 5) & (rev_rate < p["sweep_reversion_threshold"])

        tr = true_range(out)
        atr_fast = wilders_smooth(tr, p["atr_fast_period"])
        atr_slow = wilders_smooth(tr, p["atr_slow_period"])
        atr_ratio = atr_fast / atr_slow.replace(0, np.nan)
        c5 = atr_ratio > p["atr_ratio_threshold"]

        score = c1.astype(int) + c2.astype(int) + c3.astype(int) + c4.astype(int) + c5.astype(int)
        verdict = pd.Series(np.where(score >= 3, "TREND", np.where(score <= 1, "RANGE", "MIXED")), index=out.index)

        out["penroute_adx"] = adx
        out["penroute_efficiency_ratio"] = eff_ratio
        out["penroute_atr_ratio"] = atr_ratio
        out["penroute_trend_score"] = score
        out["penroute_trend_verdict"] = verdict
        return out
