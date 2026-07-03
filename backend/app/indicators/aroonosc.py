"""Aroon Oscillator — Aroon Up minus Aroon Down, collapsing the pair into a single -100..100 trend-direction reading."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("aroonosc")
class AroonOsc(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="aroonosc",
            display_name="Aroon Oscillator",
            description="Aroon Up minus Aroon Down (-100..100).",
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
        aroon_up = 100 * (n - bars_since_high) / n
        aroon_down = 100 * (n - bars_since_low) / n

        out[f"aroonosc_{n}"] = aroon_up - aroon_down
        return out
