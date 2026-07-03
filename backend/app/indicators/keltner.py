"""Keltner Channels (Chester Keltner) — EMA basis with ATR-multiple upper/lower bands."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("keltner")
class KeltnerChannels(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="keltner",
            display_name="Keltner Channels",
            description="EMA basis with upper/lower bands at N ATR multiples.",
            category="volatility",
            default_params={"ema_period": 20, "atr_period": 10, "atr_multiple": 2.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        middle = out["close"].ewm(span=p["ema_period"], adjust=False, min_periods=p["ema_period"]).mean()
        atr = wilders_smooth(true_range(out), p["atr_period"])

        suffix = f"{p['ema_period']}_{p['atr_period']}"
        out[f"keltner_middle_{suffix}"] = middle
        out[f"keltner_upper_{suffix}"] = middle + p["atr_multiple"] * atr
        out[f"keltner_lower_{suffix}"] = middle - p["atr_multiple"] * atr
        return out
