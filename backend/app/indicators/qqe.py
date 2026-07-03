"""
QQE (Quantitative Qualitative Estimation).

A smoothed RSI, further smoothed by a second EMA pass (the "slow"
line), tracked by a trailing volatility-based band -- the band's width
is set from a Wilder-smoothed average of the slow line's own bar-to-
bar changes, so it widens/narrows with how quickly RSI itself is
moving. The RSI trend line crossing outside that band is the signal.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("qqe")
class QQE(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="qqe",
            display_name="QQE (Quantitative Qualitative Estimation)",
            description="A smoothed RSI tracked by a volatility-adaptive trailing band, derived from the RSI's own rate of change.",
            category="momentum",
            default_params={"rsi_period": 14, "smoothing_period": 5, "factor": 4.236, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        rsi_n, smooth_n = p["rsi_period"], p["smoothing_period"]

        delta = src.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = wilders_smooth(gain, rsi_n)
        avg_loss = wilders_smooth(loss, rsi_n)
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))

        smoothed_rsi = rsi.ewm(span=smooth_n, adjust=False).mean()
        rsi_range = smoothed_rsi.diff().abs()
        atr_rsi = wilders_smooth(rsi_range, rsi_n)
        band_width = wilders_smooth(atr_rsi, rsi_n) * p["factor"]

        out[f"qqe_rsi_{rsi_n}_{smooth_n}"] = smoothed_rsi
        out[f"qqe_upper_{rsi_n}_{smooth_n}"] = smoothed_rsi + band_width
        out[f"qqe_lower_{rsi_n}_{smooth_n}"] = smoothed_rsi - band_width
        return out
