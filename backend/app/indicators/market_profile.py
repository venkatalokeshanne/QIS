"""
Market Profile (Time Price Opportunity / TPO).

Bins price into levels the same way Volume Profile does, but instead
of summing volume per level, counts how many distinct fixed-length
time periods (the classic "TPO periods", 30 minutes by default)
touched each level -- the core Market Profile idea of "which prices
were visited by the most discrete time periods," independent of how
much volume traded there. The Value Area (the price band containing
the busiest ~70% of periods, centered on the mode) is exposed too.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("market_profile")
class MarketProfile(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="market_profile",
            display_name="Market Profile (TPO)",
            description="Counts distinct fixed-length time periods that touched each price level -- the classic TPO concept.",
            category="price_action",
            default_params={"tpo_period_minutes": 30, "num_bins": 24, "value_area_pct": 0.70},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("MarketProfile requires a DatetimeIndex.")
        out = df.copy()
        n = p["num_bins"]

        price = out["close"]
        lo, hi = price.min(), price.max()
        if hi == lo:
            out["market_profile_tpo_count"] = 1.0
            out["market_profile_poc"] = float(price.iloc[0])
            out["market_profile_value_area_high"] = float(price.iloc[0])
            out["market_profile_value_area_low"] = float(price.iloc[0])
            return out

        edges = np.linspace(lo, hi, n + 1)
        bin_index = pd.cut(price, bins=edges, labels=False, include_lowest=True)

        tpo_period = pd.Series(out.index, index=out.index).dt.floor(f"{p['tpo_period_minutes']}min")
        # One TPO "touch" per (bin, period) pair, regardless of how many bars
        # of that period landed in that bin -- counts periods, not volume.
        touches = pd.DataFrame({"bin": bin_index, "period": tpo_period}).drop_duplicates()
        tpo_count_per_bin = touches.groupby("bin").size()

        out["market_profile_tpo_count"] = bin_index.map(tpo_count_per_bin).astype(float)

        poc_bin = tpo_count_per_bin.idxmax()
        poc_price = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)
        out["market_profile_poc"] = poc_price

        # Value area: expand outward from the POC bin, adding whichever
        # neighboring bin (above/below) has more TPO touches, until the
        # accumulated share reaches value_area_pct of all touches.
        total_touches = tpo_count_per_bin.sum()
        target = total_touches * p["value_area_pct"]
        sorted_bins = sorted(tpo_count_per_bin.index)
        low_idx = high_idx = sorted_bins.index(poc_bin)
        accumulated = tpo_count_per_bin.loc[poc_bin]

        while accumulated < target and (low_idx > 0 or high_idx < len(sorted_bins) - 1):
            below = tpo_count_per_bin.get(sorted_bins[low_idx - 1], 0) if low_idx > 0 else -1
            above = tpo_count_per_bin.get(sorted_bins[high_idx + 1], 0) if high_idx < len(sorted_bins) - 1 else -1
            if above >= below:
                high_idx += 1
                accumulated += tpo_count_per_bin.get(sorted_bins[high_idx], 0)
            else:
                low_idx -= 1
                accumulated += tpo_count_per_bin.get(sorted_bins[low_idx], 0)

        va_low_bin, va_high_bin = sorted_bins[low_idx], sorted_bins[high_idx]
        out["market_profile_value_area_low"] = float(edges[va_low_bin])
        out["market_profile_value_area_high"] = float(edges[va_high_bin + 1])
        return out
