"""Hilbert Transform - SineWave (John Ehlers) — sine and lead-sine of the dominant cycle phase; their crossover anticipates cycle turns."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._hilbert import hilbert_transform
from app.indicators.registry import indicator_registry


@indicator_registry.register("ht_sine")
class HTSine(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ht_sine",
            display_name="Hilbert Transform - SineWave",
            description="Sine and lead-sine of the dominant cycle phase -- their crossover anticipates cycle turns.",
            category="cycle",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        ht = hilbert_transform(out)
        out["ht_sine"] = ht["sine"]
        out["ht_leadsine"] = ht["leadsine"]
        return out
