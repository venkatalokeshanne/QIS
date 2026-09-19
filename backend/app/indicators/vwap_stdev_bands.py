"""VWAP StDev Bands — VWAP with standard-deviation bands (population variance of price around VWAP, volume-weighted), the VWAP analogue of Bollinger Bands. Anchors to session, week, or month."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

_ANCHOR_KEYS = {
    "session": lambda idx: idx.date,
    "week": lambda idx: idx.to_period("W"),
    "month": lambda idx: idx.to_period("M"),
}


@indicator_registry.register("vwap_stdev_bands")
class VWAPStDevBands(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vwap_stdev_bands",
            display_name="VWAP StDev Bands",
            description="Session/week/month-anchored VWAP with volume-weighted standard-deviation bands -- the VWAP analogue of Bollinger Bands.",
            category="volatility",
            default_params={"source": "hlc3", "band1_multiple": 1.0, "band2_multiple": 2.0, "anchor_period": "session"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("VWAPStDevBands requires a DatetimeIndex.")
        out = df.copy()
        source, mult1, mult2 = p["source"], p["band1_multiple"], p["band2_multiple"]

        src = (out["high"] + out["low"] + out["close"]) / 3 if source == "hlc3" else out[source]
        anchor_key = pd.Series(_ANCHOR_KEYS[p["anchor_period"]](out.index), index=out.index)

        sum_src_vol = (src * out["volume"]).groupby(anchor_key).cumsum()
        sum_vol = out["volume"].groupby(anchor_key).cumsum().replace(0, np.nan)
        sum_src_sq_vol = (src * src * out["volume"]).groupby(anchor_key).cumsum()

        vwap = sum_src_vol / sum_vol
        variance = (sum_src_sq_vol / sum_vol) - (vwap * vwap)
        stdev = np.sqrt(variance.clip(lower=0))

        out["vwap_stdev_bands_vwap"] = vwap
        out["vwap_stdev_bands_upper1"] = vwap + stdev * mult1
        out["vwap_stdev_bands_lower1"] = vwap - stdev * mult1
        out["vwap_stdev_bands_upper2"] = vwap + stdev * mult2
        out["vwap_stdev_bands_lower2"] = vwap - stdev * mult2
        return out
