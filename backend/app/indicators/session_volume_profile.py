"""
Session Volume Profile.

The same volume-by-price histogram as Volume Profile, but rebuilt
fresh each session (like VWAP) instead of over the whole dataset.

Optional Value Area (VAH/VAL): starting from the POC's own bin,
expand outward one bin at a time -- always toward whichever
neighboring bin (above or below) currently holds more volume -- until
the accumulated volume covers `value_area_pct` of the session's
total. The resulting band is where that percentage of the session's
volume actually changed hands, a tighter and more informative read
than the session's raw high-low range.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("session_volume_profile")
class SessionVolumeProfile(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="session_volume_profile",
            display_name="Session Volume Profile",
            description="Volume-by-price histogram rebuilt fresh each session: each bar's own bin volume, that session's Point of Control, and an optional Value Area.",
            category="volume",
            default_params={"num_bins": 24, "show_value_area": False, "value_area_pct": 70.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("SessionVolumeProfile requires a DatetimeIndex.")
        out = df.copy()
        n = p["num_bins"]

        session_date = pd.Series(out.index.date, index=out.index)
        bin_volume = pd.Series(np.nan, index=out.index)
        poc = pd.Series(np.nan, index=out.index)
        vah = pd.Series(np.nan, index=out.index)
        val = pd.Series(np.nan, index=out.index)

        for _, group_idx in session_date.groupby(session_date).groups.items():
            session_df = out.loc[group_idx]
            price = session_df["close"]
            lo, hi = price.min(), price.max()
            if hi == lo:
                bin_volume.loc[group_idx] = session_df["volume"].sum()
                poc.loc[group_idx] = float(price.iloc[0])
                if p["show_value_area"]:
                    vah.loc[group_idx] = float(price.iloc[0])
                    val.loc[group_idx] = float(price.iloc[0])
                continue

            edges = np.linspace(lo, hi, n + 1)
            bin_index = pd.cut(price, bins=edges, labels=False, include_lowest=True)
            volume_per_bin = session_df["volume"].groupby(bin_index).sum()

            bin_volume.loc[group_idx] = bin_index.map(volume_per_bin).astype(float)
            poc_bin = volume_per_bin.idxmax()
            poc.loc[group_idx] = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)

            if p["show_value_area"]:
                # Reindexed to the FULL 0..n-1 bin range (0.0 for any bin no
                # bar landed in) so expansion has real bounds to stop at --
                # indexing only the OBSERVED bins left a gap where a middle
                # bin with zero volume made one side's neighbor lookup
                # always miss, so ties always favored expanding the other
                # side and it grew without bound.
                full_volume_per_bin = volume_per_bin.reindex(range(n), fill_value=0.0)
                low_b = high_b = poc_bin
                acc = float(full_volume_per_bin.loc[poc_bin])
                total = float(full_volume_per_bin.sum())
                target = total * p["value_area_pct"] / 100.0
                while acc < target and (low_b > 0 or high_b < n - 1):
                    vol_below = float(full_volume_per_bin.loc[low_b - 1]) if low_b > 0 else -1.0
                    vol_above = float(full_volume_per_bin.loc[high_b + 1]) if high_b < n - 1 else -1.0
                    if vol_above >= vol_below:
                        high_b += 1
                        acc += max(vol_above, 0.0)
                    else:
                        low_b -= 1
                        acc += max(vol_below, 0.0)
                vah.loc[group_idx] = float(edges[high_b + 1])
                val.loc[group_idx] = float(edges[low_b])

        out["session_volume_profile_bin_volume"] = bin_volume
        out["session_volume_profile_poc"] = poc
        if p["show_value_area"]:
            out["session_volume_profile_vah"] = vah
            out["session_volume_profile_val"] = val
        return out
