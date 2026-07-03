"""
EMA above EMA (e.g. EMA20 > EMA50).

Generic two-period EMA comparison filter rather than a hardcoded
"ema20_above_ema50" filter, so any pair of periods can be compared
without adding a new file per combination.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry


@filter_registry.register("ema_above")
class EMAAbove(Filter):
    """Requires ema_{fast_period} and ema_{slow_period} columns already computed."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="ema_above",
            display_name="EMA Above EMA",
            description="True where the faster EMA is above the slower EMA (e.g. EMA20 > EMA50).",
            category="trend",
            default_params={"fast_period": 20, "slow_period": 50},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        p = self.validate_params(params)
        fast_col, slow_col = f"ema_{p['fast_period']}", f"ema_{p['slow_period']}"
        for col in (fast_col, slow_col):
            if col not in df.columns:
                raise KeyError(f"ema_above filter requires a '{col}' column (run the EMA indicator first).")
        return df[fast_col] > df[slow_col]
