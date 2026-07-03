"""McGinley Dynamic (John McGinley) — a self-adjusting moving average that speeds up/slows down with market speed, reducing whipsaw versus a fixed-period MA."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("mcginley_dynamic")
class McGinleyDynamic(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="mcginley_dynamic",
            display_name="McGinley Dynamic",
            description="A self-adjusting moving average that speeds up or slows down with the market, reducing whipsaw vs. a fixed-period MA.",
            category="overlap",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        values = out[p["source"]].to_numpy()
        md = np.full(len(out), np.nan)

        if len(out) > 0:
            md[0] = values[0]
            for i in range(1, len(out)):
                prev = md[i - 1]
                ratio = values[i] / prev if prev != 0 else 1.0
                md[i] = prev + (values[i] - prev) / (n * ratio**4)

        out[f"mcginley_dynamic_{n}"] = md
        return out
