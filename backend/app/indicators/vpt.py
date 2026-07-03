"""Volume Price Trend — cumulative volume weighted by each bar's percentage price change, rather than just its direction (unlike OBV)."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vpt")
class VolumePriceTrend(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vpt",
            display_name="Volume Price Trend",
            description="Cumulative volume weighted by each bar's percentage price change (unlike OBV, which only uses direction).",
            category="volume",
            default_params={},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        self.validate_params(params)
        out = df.copy()
        pct_change = out["close"].pct_change()
        out["vpt"] = (pct_change * out["volume"]).fillna(0).cumsum()
        return out
