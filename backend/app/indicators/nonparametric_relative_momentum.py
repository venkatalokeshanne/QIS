"""
Nonparametric Relative Momentum.

A rank-based oscillator: instead of a fixed 0-100 formula like RSI or
a min/max-normalized read like Stochastic, this counts where the
current value of a target series sits among its own recent history --
a genuine empirical percentile, with ties given half weight so the
result is a proper mid-rank rather than a naive "how many bars beat
me" count. Two rank targets are supported: "price" (rank the raw
source -- smooth, stochastic-like) or "momentum" (rank the source's
own rate-of-change -- a truer nonparametric RSI, since it ranks
CHANGE rather than level). Distinct from
app.indicators.ema_distance_percentile_rank (ranks EMA distance) and
app.indicators.laguerre_ppo_percentile_rank (ranks a Laguerre-smoothed
PPO spread) -- this ranks the price/momentum series directly, with no
smoothing filter ahead of the rank.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _percentile_rank_with_ties(series: pd.Series, length: int) -> pd.Series:
    """Percentile rank of the current value against the PRIOR `length` bars
    (current bar excluded), with ties counted at half weight -- a proper
    empirical mid-rank rather than a strict less-than count.
    """

    def rank(w):
        current, history = w[-1], w[:-1]
        less = (history < current).sum()
        eq = (history == current).sum()
        return 100.0 * (less + 0.5 * eq) / length

    return series.rolling(window=length + 1, min_periods=length + 1).apply(rank, raw=True)


@indicator_registry.register("nonparametric_relative_momentum")
class NonparametricRelativeMomentum(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="nonparametric_relative_momentum",
            display_name="Nonparametric Relative Momentum",
            description="Percentile rank of price (or its rate-of-change) against its own trailing window -- a rank-based, distribution-free alternative to RSI/Stochastic, with an EMA signal line and OB/OS zones.",
            category="momentum",
            default_params={
                "source": "close",
                "mode": "momentum",
                "rank_window": 50,
                "momentum_length": 32,
                "output_smoothing": 1,
                "signal_length": 9,
                "overbought": 90.0,
                "oversold": 10.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        target = src - src.shift(p["momentum_length"]) if p["mode"] == "momentum" else src
        rank = _percentile_rank_with_ties(target, p["rank_window"])

        smooth = p["output_smoothing"]
        oscillator = rank.ewm(span=smooth, adjust=False, min_periods=1).mean() if smooth > 1 else rank
        signal = oscillator.ewm(span=p["signal_length"], adjust=False, min_periods=p["signal_length"]).mean()

        out["nrm_rank"] = rank
        out["nrm_oscillator"] = oscillator
        out["nrm_signal"] = signal
        return out
