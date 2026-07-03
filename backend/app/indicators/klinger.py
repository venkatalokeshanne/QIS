"""Klinger Volume Oscillator (Stephen Klinger) — a volume force (signed by trend direction and scaled by how far price swung) smoothed by two EMAs, like a volume-based MACD."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("klinger")
class KlingerOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="klinger",
            display_name="Klinger Volume Oscillator",
            description="Volume force (signed by trend direction, scaled by swing size) smoothed by two EMAs -- a volume-based MACD.",
            category="volume",
            default_params={"fast_period": 34, "slow_period": 55, "signal_period": 13},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        trend = np.sign(typical_price.diff()).fillna(0)
        # Daily measurement (dm): the day's trading range.
        dm = out["high"] - out["low"]
        # Cumulative measurement (cm): running total of dm, reset whenever trend flips.
        trend_group = (trend != trend.shift(1)).cumsum()
        cm = dm.groupby(trend_group).cumsum()

        volume_force = out["volume"] * trend * (2 * (dm / cm.replace(0, np.nan) - 1)).abs() * 100

        fast = volume_force.ewm(span=p["fast_period"], adjust=False, min_periods=p["fast_period"]).mean()
        slow = volume_force.ewm(span=p["slow_period"], adjust=False, min_periods=p["slow_period"]).mean()
        kvo = fast - slow
        signal = kvo.ewm(span=p["signal_period"], adjust=False, min_periods=p["signal_period"]).mean()

        out["kvo"] = kvo
        out["kvo_signal"] = signal
        return out
