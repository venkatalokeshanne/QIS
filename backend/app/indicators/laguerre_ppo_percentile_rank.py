"""
Laguerre PPO Percentile Rank (tops & bottoms).

Runs hl2 through two 4-stage Laguerre filters at different gamma
("Short"/"Long") smoothing factors, takes their percentage spread
(a Percentage Price Oscillator built from Laguerre-smoothed inputs
instead of plain EMAs), then transforms that PPO into its own
percentile rank over a trailing window. A top score near 100 means
today's bullish PPO reading is more extreme than nearly all of the
last `lookback` bars -- a statistical (not fixed-threshold) way to
flag potential tops/bottoms. Tops and bottoms are tracked as separate
series since the source script computes them from independently
signed PPO variants.

Laguerre filtering is a recursive/stateful construct (each stage
feeds the previous bar's own output back into itself), so it's
computed with an explicit bar-by-bar loop rather than a vectorized
pandas expression -- the same pattern used by
app.indicators.kalman_trend_filter.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _laguerre_filter(price: np.ndarray, gamma: float) -> np.ndarray:
    length = len(price)
    result = np.full(length, np.nan)
    l0 = l1 = l2 = l3 = 0.0
    for i in range(length):
        p = price[i]
        if np.isnan(p):
            continue
        prev_l0, prev_l1, prev_l2 = l0, l1, l2
        l0 = (1 - gamma) * p + gamma * l0
        l1 = -gamma * l0 + prev_l0 + gamma * l1
        l2 = -gamma * l1 + prev_l1 + gamma * l2
        l3 = -gamma * l2 + prev_l2 + gamma * l3
        result[i] = (l0 + 2 * l1 + 2 * l2 + l3) / 6
    return result


def _percent_rank(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period + 1, min_periods=period + 1).apply(
        lambda w: (w[:-1] < w[-1]).sum() / period * 100, raw=True
    )


@indicator_registry.register("laguerre_ppo_percentile_rank")
class LaguerrePPOPercentileRank(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="laguerre_ppo_percentile_rank",
            display_name="Laguerre PPO Percentile Rank",
            description="Percentage spread between two Laguerre-smoothed price filters, transformed into its own percentile rank -- a statistical extreme-reading detector for tops and bottoms.",
            category="momentum",
            default_params={"gamma_short": 0.4, "gamma_long": 0.8, "lookback_tops": 200, "lookback_bottoms": 200},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        hl2 = ((out["high"] + out["low"]) / 2).to_numpy()

        lag_short = _laguerre_filter(hl2, p["gamma_short"])
        lag_long = _laguerre_filter(hl2, p["gamma_long"])
        lag_long_s = pd.Series(lag_long, index=out.index).replace(0, np.nan)
        lag_short_s = pd.Series(lag_short, index=out.index)

        ppo_top = (lag_short_s - lag_long_s) / lag_long_s * 100
        ppo_bottom = (lag_long_s - lag_short_s) / lag_long_s * 100

        out["laguerre_ppo_rank_top"] = _percent_rank(ppo_top, p["lookback_tops"])
        out["laguerre_ppo_rank_bottom"] = -_percent_rank(ppo_bottom, p["lookback_bottoms"])
        return out
