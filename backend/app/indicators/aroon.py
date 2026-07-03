"""Aroon (Tushar Chande) — how many bars since the highest high / lowest low within a trailing window, scaled 0-100."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("aroon")
class Aroon(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="aroon",
            display_name="Aroon",
            description="How recently (as a 0-100 score) the highest high / lowest low occurred within a trailing window.",
            category="momentum",
            default_params={"period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        bars_since_high = out["high"].rolling(window=n + 1, min_periods=n + 1).apply(
            lambda w: n - w.argmax(), raw=True
        )
        bars_since_low = out["low"].rolling(window=n + 1, min_periods=n + 1).apply(
            lambda w: n - w.argmin(), raw=True
        )

        out[f"aroon_up_{n}"] = 100 * (n - bars_since_high) / n
        out[f"aroon_down_{n}"] = 100 * (n - bars_since_low) / n
        return out
