"""Gap Up — session open is meaningfully above the prior session's close."""

from typing import Any

import pandas as pd

from app.domain.interfaces.filter import Filter, FilterMetadata
from app.filters.registry import filter_registry
from app.utils.sessions import is_first_bar_of_session


@filter_registry.register("gap_up")
class GapUp(Filter):
    """
    True on the first bar of a session if that session's open is more
    than `threshold_pct` above the previous session's last close.
    All other bars are False (a gap is a once-per-session event).
    """

    @property
    def metadata(self) -> FilterMetadata:
        return FilterMetadata(
            name="gap_up",
            display_name="Gap Up",
            description="True on the session's first bar if it opened above the prior session's close.",
            category="price_action",
            default_params={"threshold_pct": 0.002},
        )

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.Series:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("gap_up filter requires a DatetimeIndex.")
        p = self.validate_params(params)

        prior_session_close = df["close"].groupby(df.index.date).transform("last").shift(1)
        gapped = df["open"] > prior_session_close * (1 + p["threshold_pct"])
        return (gapped & is_first_bar_of_session(df.index)).fillna(False)
