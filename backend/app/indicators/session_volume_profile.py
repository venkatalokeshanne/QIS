"""Session Volume Profile — the same volume-by-price histogram as Volume Profile, but rebuilt fresh each session (like VWAP) instead of over the whole dataset."""

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
            description="Volume-by-price histogram rebuilt fresh each session: each bar's own bin volume and that session's Point of Control.",
            category="volume",
            default_params={"num_bins": 24},
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

        for _, group_idx in session_date.groupby(session_date).groups.items():
            session_df = out.loc[group_idx]
            price = session_df["close"]
            lo, hi = price.min(), price.max()
            if hi == lo:
                bin_volume.loc[group_idx] = session_df["volume"].sum()
                poc.loc[group_idx] = float(price.iloc[0])
                continue

            edges = np.linspace(lo, hi, n + 1)
            bin_index = pd.cut(price, bins=edges, labels=False, include_lowest=True)
            volume_per_bin = session_df["volume"].groupby(bin_index).sum()

            bin_volume.loc[group_idx] = bin_index.map(volume_per_bin).astype(float)
            poc_bin = volume_per_bin.idxmax()
            poc.loc[group_idx] = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)

        out["session_volume_profile_bin_volume"] = bin_volume
        out["session_volume_profile_poc"] = poc
        return out
