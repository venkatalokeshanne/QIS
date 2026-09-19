"""OBV Signal — On-Balance Volume with its own signal-line moving average (SMA or EMA)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("obv_signal")
class OBVSignal(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="obv_signal",
            display_name="OBV Signal",
            description="On-Balance Volume with its own signal-line moving average (SMA or EMA).",
            category="volume",
            default_params={"signal_period": 20, "signal_type": "sma"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, signal_type = p["signal_period"], p["signal_type"]

        direction = np.sign(out["close"].diff()).fillna(0)
        obv = (direction * out["volume"]).cumsum()
        signal = (
            obv.ewm(span=n, adjust=False, min_periods=n).mean()
            if signal_type == "ema"
            else obv.rolling(window=n, min_periods=n).mean()
        )

        out["obv_signal_obv"] = obv
        out[f"obv_signal_{signal_type}_{n}"] = signal
        return out
