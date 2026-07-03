"""Gap Down — session open is meaningfully below the prior session's close."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry
from app.utils.sessions import is_first_bar_of_session


@filter_registry.register("gap_down")
class GapDown(Filter):
    """True on the session's first bar if it opened below the prior session's close."""

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="gap_down",
            display_name="Gap Down",
            description="True on the session's first bar if it opened below the prior session's close.",
            category="price_action",
            default_params={"threshold_pct": 0.002},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("gap_down filter requires a DatetimeIndex.")
        p = self.validate_params(params)

        prior_session_close = df["close"].groupby(df.index.date).transform("last").shift(1)
        gapped = df["open"] < prior_session_close * (1 - p["threshold_pct"])
        return (gapped & is_first_bar_of_session(df.index)).fillna(False)
