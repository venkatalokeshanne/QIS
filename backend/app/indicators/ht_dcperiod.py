"""Hilbert Transform - Dominant Cycle Period (John Ehlers) — the dominant price cycle length detected by the shared MESA engine."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_dcperiod")
class HTDCPeriod(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_dcperiod",
            display_name="Hilbert Transform - Dominant Cycle Period",
            description="The dominant price cycle length (in bars) detected via Ehlers' Hilbert Transform (MESA) engine.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_dcperiod"] = ht["smooth_period"]
        return out
