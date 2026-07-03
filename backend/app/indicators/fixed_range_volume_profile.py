"""Fixed Range Volume Profile — the same volume-by-price histogram, computed ONCE over a fixed trailing window of the dataframe (matching how this tool is normally used: a user-drawn fixed range, not a rolling recalculation)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("fixed_range_volume_profile")
class FixedRangeVolumeProfile(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="fixed_range_volume_profile",
            display_name="Fixed Range Volume Profile",
            description="Volume-by-price histogram computed once over the trailing N bars (a fixed range, not a rolling recalculation).",
            category="volume",
            default_params={"window_bars": 100, "num_bins": 24},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        window, n = p["window_bars"], p["num_bins"]
        windowed = out.iloc[-window:] if len(out) >= window else out

        price = windowed["close"]
        lo, hi = price.min(), price.max()

        bin_volume = pd.Series(np.nan, index=out.index)
        poc_series = pd.Series(np.nan, index=out.index)

        if hi == lo:
            bin_volume.loc[windowed.index] = windowed["volume"].sum()
            poc_series.loc[windowed.index] = float(price.iloc[0])
        else:
            edges = np.linspace(lo, hi, n + 1)
            bin_index = pd.cut(price, bins=edges, labels=False, include_lowest=True)
            volume_per_bin = windowed["volume"].groupby(bin_index).sum()

            bin_volume.loc[windowed.index] = bin_index.map(volume_per_bin).astype(float).values
            poc_bin = volume_per_bin.idxmax()
            poc_series.loc[windowed.index] = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)

        out["fixed_range_volume_profile_bin_volume"] = bin_volume
        out["fixed_range_volume_profile_poc"] = poc_series
        return out
