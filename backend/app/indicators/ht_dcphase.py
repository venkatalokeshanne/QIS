"""Hilbert Transform - Dominant Cycle Phase (John Ehlers) — the current phase angle (degrees) within the detected dominant cycle."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_dcphase")
class HTDCPhase(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_dcphase",
            display_name="Hilbert Transform - Dominant Cycle Phase",
            description="Current phase angle (degrees) within the detected dominant price cycle.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_dcphase"] = ht["dcphase"]
        return out
