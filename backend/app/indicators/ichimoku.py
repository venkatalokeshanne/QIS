"""Ichimoku Kinko Hyo (Goichi Hosoda) — a five-line system (conversion, base, two displaced leading spans forming the cloud, and a displaced lagging span) combining trend, momentum, and support/resistance."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _midline(df: pd.DataFrame, period: int) -> pd.Series:
    return (
        df["high"].rolling(window=period, min_periods=period).max()
        + df["low"].rolling(window=period, min_periods=period).min()
    ) / 2


@indicator_registry.register("ichimoku")
class Ichimoku(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ichimoku",
            display_name="Ichimoku Cloud",
            description="Conversion/base lines, a displaced leading cloud (Senkou A/B), and a displaced lagging span.",
            category="overlap",
            default_params={
                "conversion_period": 9,
                "base_period": 26,
                "leading_span_b_period": 52,
                "displacement": 26,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        disp = p["displacement"]

        conversion = _midline(out, p["conversion_period"])
        base = _midline(out, p["base_period"])
        leading_span_a = ((conversion + base) / 2).shift(disp)
        leading_span_b = _midline(out, p["leading_span_b_period"]).shift(disp)
        lagging_span = out["close"].shift(-disp)

        out["ichimoku_conversion"] = conversion
        out["ichimoku_base"] = base
        out["ichimoku_leading_span_a"] = leading_span_a
        out["ichimoku_leading_span_b"] = leading_span_b
        out["ichimoku_lagging_span"] = lagging_span
        return out
