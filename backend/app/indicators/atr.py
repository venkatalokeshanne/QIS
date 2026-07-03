"""Average True Range (J. Welles Wilder) — Wilder-smoothed true range, the standard volatility measure."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("atr")
class ATR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="atr",
            display_name="Average True Range",
            description="Wilder's average true range, a volatility measure.",
            category="volatility",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        out[f"atr_{p['period']}"] = wilders_smooth(true_range(out), p["period"])
        return out
