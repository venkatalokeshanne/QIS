"""Relative Vigor Index (John Ehlers) — a smoothed ratio of (close-open) to (high-low), on the idea that markets close higher than they open in strong up-trends (and vice versa)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rvi")
class RelativeVigorIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rvi",
            display_name="Relative Vigor Index",
            description="Smoothed ratio of (close-open) to (high-low) -- strong trends close away from the open.",
            category="momentum",
            default_params={"period": 10, "signal_period": 4},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        # 4-bar symmetrically-weighted smoothing (1,2,2,1)/6, the classic RVI filter.
        def four_bar_smooth(series: pd.Series) -> pd.Series:
            return (series + 2 * series.shift(1) + 2 * series.shift(2) + series.shift(3)) / 6

        numerator = four_bar_smooth(out["close"] - out["open"])
        denominator = four_bar_smooth(out["high"] - out["low"])

        num_sum = numerator.rolling(window=n, min_periods=n).sum()
        den_sum = denominator.rolling(window=n, min_periods=n).sum()
        rvi = num_sum / den_sum.replace(0, float("nan"))

        signal = (rvi + 2 * rvi.shift(1) + 2 * rvi.shift(2) + rvi.shift(3)) / 6

        out[f"rvi_{n}"] = rvi
        out[f"rvi_signal_{n}"] = signal
        return out
