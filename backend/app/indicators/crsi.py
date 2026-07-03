"""Connors RSI (Larry Connors) — a composite of plain RSI, a streak-length RSI, and the percentile rank of the latest 1-bar return."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


@indicator_registry.register("crsi")
class ConnorsRSI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="crsi",
            display_name="Connors RSI",
            description="Composite of plain RSI, a streak-length RSI, and the percentile rank of the latest return.",
            category="momentum",
            default_params={"rsi_period": 3, "streak_period": 2, "rank_period": 100, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        price_rsi = _rsi(src, p["rsi_period"])

        direction = pd.Series(0, index=out.index, dtype=float)
        diff = src.diff()
        direction[diff > 0] = 1
        direction[diff < 0] = -1
        streak_group = (direction != direction.shift(1)).cumsum()
        streak_length = direction.groupby(streak_group).cumcount() + 1
        streak = streak_length * direction
        streak_rsi = _rsi(streak, p["streak_period"])

        one_bar_return = src.pct_change()
        rank_period = p["rank_period"]
        percent_rank = one_bar_return.rolling(window=rank_period, min_periods=rank_period).apply(
            lambda w: (w.iloc[:-1] < w.iloc[-1]).sum() / (len(w) - 1) * 100 if len(w) > 1 else 50.0,
            raw=False,
        )

        out[f"crsi_{p['rsi_period']}_{p['streak_period']}_{rank_period}"] = (
            price_rsi + streak_rsi + percent_rank
        ) / 3
        return out
