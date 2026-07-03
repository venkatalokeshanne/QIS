"""MESA Adaptive Moving Average (John Ehlers) — a moving average whose smoothing speed adapts to the dominant price cycle, via the shared Hilbert Transform engine."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("mama")
class MAMA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="mama",
            display_name="MESA Adaptive Moving Average",
            description="A moving average whose smoothing speed adapts to the dominant detected price cycle (MAMA/FAMA pair).",
            category="overlap",
            default_params={"fast_limit": 0.5, "slow_limit": 0.05},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out, fast_limit=p["fast_limit"], slow_limit=p["slow_limit"])
        out["mama"] = ht["mama"]
        out["fama"] = ht["fama"]
        return out
