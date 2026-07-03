"""
Volume Profile.

Bins the dataset's whole price range into `num_bins` levels and sums
the volume traded at each level, over the entire dataframe (a static,
"visible range" profile). Each bar is tagged with the total volume
traded at its own price bin (a proxy for whether it sits at a high-
or low-volume node) plus the Point of Control (POC) -- the single
highest-volume price level -- broadcast to every row.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _profile(df: pd.DataFrame, num_bins: int) -> tuple[pd.Series, float]:
    price = df["close"]
    lo, hi = price.min(), price.max()
    if hi == lo:
        bin_index = pd.Series(0, index=df.index)
        bin_volume = pd.Series(df["volume"].sum(), index=df.index)
        return bin_volume, float(price.iloc[0])

    edges = np.linspace(lo, hi, num_bins + 1)
    bin_index = pd.cut(price, bins=edges, labels=False, include_lowest=True)
    volume_per_bin = df["volume"].groupby(bin_index).sum()
    bin_volume = bin_index.map(volume_per_bin)

    poc_bin = volume_per_bin.idxmax()
    poc_price = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)
    return bin_volume, poc_price


@indicator_registry.register("volume_profile")
class VolumeProfile(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volume_profile",
            display_name="Volume Profile",
            description="Static whole-dataset volume-by-price histogram: each bar's own bin volume, plus the Point of Control.",
            category="volume",
            default_params={"num_bins": 24},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        bin_volume, poc_price = _profile(out, p["num_bins"])

        out["volume_profile_bin_volume"] = bin_volume.astype(float)
        out["volume_profile_poc"] = poc_price
        return out
