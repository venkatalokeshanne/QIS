"""Inside Bar Sequence — flags EVERY bar that stays within a "mother bar" range, not just a single 2-bar inside pattern: once an inside bar opens a sequence, every subsequent bar that still fits inside that SAME mother bar's range keeps flagging, until one finally breaks out of it."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("inside_bar_sequence")
class InsideBarSequence(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="inside_bar_sequence",
            display_name="Inside Bar Sequence",
            description="Flags every bar that stays within a 'mother bar' range -- a multi-bar consolidation, not just a single 2-bar inside pattern.",
            category="price_action",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        high, low = out["high"].to_numpy(), out["low"].to_numpy()
        length = len(out)

        inside_mother = np.zeros(length, dtype=bool)
        in_sequence = False
        mother_high = np.nan
        mother_low = np.nan
        for i in range(1, length):
            first_inside = high[i] <= high[i - 1] and low[i] >= low[i - 1]
            if not in_sequence and first_inside:
                mother_high, mother_low = high[i - 1], low[i - 1]
                in_sequence = True

            still_inside = in_sequence and high[i] <= mother_high and low[i] >= mother_low
            if in_sequence and not still_inside:
                in_sequence = False
                mother_high, mother_low = np.nan, np.nan

            inside_mother[i] = still_inside

        out["inside_bar_sequence"] = inside_mother
        return out
