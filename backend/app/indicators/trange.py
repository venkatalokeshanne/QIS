"""True Range — the single-bar volatility reading ATR smooths over time."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range
from app.indicators.registry import indicator_registry


@indicator_registry.register("trange")
class TrueRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="trange",
            display_name="True Range",
            description="max(high-low, |high-prev_close|, |low-prev_close|) -- the raw, unsmoothed volatility reading.",
            category="volatility",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["trange"] = true_range(out)
        return out
