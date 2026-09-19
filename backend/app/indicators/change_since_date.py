"""Change Since Date — percent change from the close on (or just after) a fixed calendar anchor date, NaN before it."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("change_since_date")
class ChangeSinceDate(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="change_since_date",
            display_name="Change Since Date",
            description="Percent change from the close on (or just after) a fixed anchor date -- NaN before that date.",
            category="price_transform",
            default_params={"anchor_date": "2023-10-15"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        anchor = pd.Timestamp(p["anchor_date"])

        on_or_after = out.index >= anchor
        anchor_price = out.loc[on_or_after, "close"].iloc[0] if on_or_after.any() else None

        pct_change = pd.Series(np.nan, index=out.index) if anchor_price is None else pd.Series(
            ((out["close"] - anchor_price) / anchor_price * 100).where(on_or_after)
        )
        out["change_since_date_pct"] = pct_change
        return out
