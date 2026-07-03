"""HLC3 — mean of high, low, and close (equivalent to Typical Price, kept as its own name since several other indicators reference "hlc3" directly as a source option)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("hlc3")
class HLC3(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="hlc3",
            display_name="HLC3",
            description="(High + Low + Close) / 3.",
            category="price_transform",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        out["hlc3"] = (out["high"] + out["low"] + out["close"]) / 3
        return out
