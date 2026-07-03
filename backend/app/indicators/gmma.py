"""Guppy Multiple Moving Average (Daryl Guppy) — two groups of EMAs (a fast/trader group and a slow/investor group); their separation and compression signal trend strength and turning points."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_DEFAULT_SHORT_PERIODS = [3, 5, 8, 10, 12, 15]
_DEFAULT_LONG_PERIODS = [30, 35, 40, 45, 50, 60]


@indicator_registry.register("gmma")
class GuppyMultipleMovingAverage(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="gmma",
            display_name="Guppy Multiple Moving Average",
            description="A fast (trader) group and a slow (investor) group of EMAs -- their separation/compression signals trend strength and turns.",
            category="overlap",
            default_params={
                "short_periods": _DEFAULT_SHORT_PERIODS,
                "long_periods": _DEFAULT_LONG_PERIODS,
                "source": "close",
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        for period in p["short_periods"]:
            out[f"gmma_short_ema_{period}"] = src.ewm(span=period, adjust=False).mean()
        for period in p["long_periods"]:
            out[f"gmma_long_ema_{period}"] = src.ewm(span=period, adjust=False).mean()
        return out
