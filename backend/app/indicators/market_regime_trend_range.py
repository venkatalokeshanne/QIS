"""
Market Regime — Trend or Range.

A 2-of-3 ensemble vote across three independent trend-strength reads
-- ADX, Kaufman Efficiency Ratio, and the Choppiness Index -- rather
than trusting any single measure's threshold alone. Each votes +1
(trending), -1 (ranging), or 0 (inconclusive); the votes are summed
into a -3..+3 score, and TREND/RANGE only get called once at least
two of the three agree (MIXED otherwise). Distinct from
app.indicators.adx_atr_regime_classifier, which combines ADX + ATR%
volatility + EMA direction into a bull/bear/range/high-vol label --
this indicator's inputs (Efficiency Ratio, Choppiness Index) aren't
used anywhere else in this codebase, and the ensemble-voting
construction is its own approach to the trend-vs-range question.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement, true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("market_regime_trend_range")
class MarketRegimeTrendRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="market_regime_trend_range",
            display_name="Market Regime — Trend or Range",
            description="2-of-3 ensemble vote (ADX, Kaufman Efficiency Ratio, Choppiness Index) on whether the market is currently trending or ranging.",
            category="trend",
            default_params={
                "adx_period": 14,
                "adx_trend_threshold": 25.0,
                "adx_range_threshold": 20.0,
                "efficiency_ratio_period": 20,
                "efficiency_ratio_trend_threshold": 0.50,
                "efficiency_ratio_range_threshold": 0.30,
                "choppiness_period": 14,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        dm = directional_movement(out, p["adx_period"])
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        adx = wilders_smooth(dx, p["adx_period"])
        adx_vote = pd.Series(
            np.select(
                [adx > p["adx_trend_threshold"], adx < p["adx_range_threshold"]],
                [1, -1],
                default=0,
            ),
            index=out.index,
        )
        adx_vote[adx.isna()] = 0

        er_len = p["efficiency_ratio_period"]
        er_change = (out["close"] - out["close"].shift(er_len)).abs()
        er_volatility = out["close"].diff().abs().rolling(window=er_len, min_periods=er_len).sum()
        efficiency_ratio = (er_change / er_volatility.replace(0, np.nan)).fillna(0.0)
        er_vote = pd.Series(
            np.select(
                [
                    efficiency_ratio > p["efficiency_ratio_trend_threshold"],
                    efficiency_ratio < p["efficiency_ratio_range_threshold"],
                ],
                [1, -1],
                default=0,
            ),
            index=out.index,
        )
        er_vote[er_volatility.isna()] = 0

        chop_len = p["choppiness_period"]
        chop_range = out["high"].rolling(chop_len, min_periods=chop_len).max() - out["low"].rolling(
            chop_len, min_periods=chop_len
        ).min()
        tr_sum = true_range(out).rolling(chop_len, min_periods=chop_len).sum()
        choppiness = 100.0 * np.log10(tr_sum / chop_range.replace(0, np.nan)) / np.log10(chop_len)
        choppiness = choppiness.fillna(50.0)
        chop_vote = pd.Series(
            np.select([choppiness < 38.2, choppiness > 61.8], [1, -1], default=0),
            index=out.index,
        )
        chop_vote[chop_range.isna()] = 0

        score = adx_vote + er_vote + chop_vote
        is_trend = score >= 2
        is_range = score <= -2
        regime = pd.Series(np.where(is_trend, "trend", np.where(is_range, "range", "mixed")), index=out.index)
        warmup = adx.isna() | er_volatility.isna() | chop_range.isna()
        regime[warmup] = None

        out["mrtr_adx"] = adx
        out["mrtr_efficiency_ratio"] = efficiency_ratio
        out["mrtr_choppiness"] = choppiness
        out["mrtr_score"] = score.where(~warmup)
        out["mrtr_regime"] = regime
        return out
