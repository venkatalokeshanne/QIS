"""
BB Squeeze Histogram.

Bollinger Band width (the gap between the +N/-N standard-deviation
bands), expressed as a signed, MACD-style histogram instead of a
plain volatility line: signed positive when price sits above the
basis MA and negative when below, so the histogram doubles as a
trend-side read, not just a volatility magnitude. Optionally
normalized to a 0-100 percentile rank against its own trailing
history (so "wide" means something consistent across different
instruments/regimes) instead of a raw dollar width. A squeeze flag
fires when the raw width sits at its tightest point over its own
lookback window. Distinct from app.indicators.bbands_width (a plain
unsigned ratio) and app.indicators.squeeze_momentum (BB-inside-
Keltner-Channel squeeze definition, not a width percentile).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("bb_squeeze_histogram")
class BBSqueezeHistogram(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="bb_squeeze_histogram",
            display_name="BB Squeeze Histogram",
            description="Bollinger Band width as a signed, MACD-style histogram (positive above the basis MA, negative below), optionally normalized to a 0-100 percentile rank against its own history.",
            category="volatility",
            default_params={
                "period": 20,
                "std_dev": 3.0,
                "normalize": False,
                "normalize_lookback": 200,
                "squeeze_lookback": 100,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = (out["open"] + out["high"] + out["low"] + out["close"]) / 4

        basis = src.rolling(n, min_periods=n).mean()
        dev = src.rolling(n, min_periods=n).std()
        width = 2 * p["std_dev"] * dev

        if p["normalize"]:
            lb = p["normalize_lookback"]
            rank = width.rolling(window=lb + 1, min_periods=lb + 1).apply(
                lambda w: (w[:-1] < w[-1]).sum() / lb * 100, raw=True
            )
            mag = rank / 2.0
            neutral = 50.0
        else:
            mag = width
            neutral = 0.0

        above = src >= basis
        hist = np.where(above, neutral + mag, neutral - mag)

        out["bb_squeeze_width"] = width
        out["bb_squeeze_histogram"] = hist
        out["bb_squeeze_active"] = width == width.rolling(p["squeeze_lookback"], min_periods=p["squeeze_lookback"]).min()
        return out
