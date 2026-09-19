"""
Prior Period POC.

The previous COMPLETED day's and week's Point of Control (the price
level with the most volume traded), held constant through the
following period. Distinct from app.indicators.volume_profile
(static, whole-dataset) and app.indicators.session_volume_profile
(the CURRENT, still-forming session) -- this only ever shows a PRIOR
period's already-finalized POC, computed once that period has fully
closed and then held flat, so it never repaints.

Reuses the same volume-by-price binning as volume_profile.py/
session_volume_profile.py, applied per calendar day/ISO week, then
shifted by one period and mapped back onto every bar of the
following period (the same non-repainting pattern used by
app.indicators.monthly_close_extremes for prior completed closes).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _period_poc(price: pd.Series, volume: pd.Series, period_key: pd.Series, num_bins: int) -> pd.Series:
    """One POC price per distinct period_key value, from that period's own bars only."""
    pocs: dict[Any, float] = {}
    for key, idx in period_key.groupby(period_key).groups.items():
        p, v = price.loc[idx], volume.loc[idx]
        lo, hi = p.min(), p.max()
        if hi == lo:
            pocs[key] = float(p.iloc[0])
            continue
        edges = np.linspace(lo, hi, num_bins + 1)
        bin_index = pd.cut(p, bins=edges, labels=False, include_lowest=True)
        volume_per_bin = v.groupby(bin_index).sum()
        poc_bin = volume_per_bin.idxmax()
        pocs[key] = float((edges[poc_bin] + edges[poc_bin + 1]) / 2)
    return pd.Series(pocs)


@indicator_registry.register("prior_period_poc")
class PriorPeriodPOC(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="prior_period_poc",
            display_name="Prior Period POC",
            description="The previous completed day's and week's Point of Control (highest-volume price level), held constant through the following period.",
            category="volume",
            default_params={"num_bins": 24},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("PriorPeriodPOC requires a DatetimeIndex.")
        out = df.copy()
        num_bins = p["num_bins"]

        price, volume = out["close"], out["volume"]

        day_key = pd.Series(out.index.date, index=out.index)
        week_key = pd.Series(
            out.index.isocalendar().week.to_numpy() + out.index.isocalendar().year.to_numpy() * 100,
            index=out.index,
        )

        daily_poc = _period_poc(price, volume, day_key, num_bins)
        weekly_poc = _period_poc(price, volume, week_key, num_bins)

        prior_daily_poc = daily_poc.shift(1)
        prior_weekly_poc = weekly_poc.shift(1)

        out["prior_day_poc"] = day_key.map(prior_daily_poc)
        out["prior_week_poc"] = week_key.map(prior_weekly_poc)
        return out
