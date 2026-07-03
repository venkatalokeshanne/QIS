"""Hilbert Transform - Phasor Components (John Ehlers) — the in-phase and quadrature components underlying the dominant-cycle calculation."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_phasor")
class HTPhasor(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_phasor",
            display_name="Hilbert Transform - Phasor Components",
            description="In-phase and quadrature components underlying the dominant-cycle calculation.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_phasor_inphase"] = ht["inphase"]
        out["ht_phasor_quadrature"] = ht["quadrature"]
        return out
