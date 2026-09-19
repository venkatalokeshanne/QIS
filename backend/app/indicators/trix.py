"""TRIX — rate of change of a triple-smoothed EMA of log(close), plus its own signal-line MA (SMA or EMA)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("trix")
class TRIX(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="trix",
            display_name="TRIX",
            description="Rate of change of a triple-smoothed EMA of log(close) -- a momentum oscillator with built-in noise filtering.",
            category="momentum",
            default_params={"period": 9, "signal_period": 4, "signal_type": "sma"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, signal_n, signal_type = p["period"], p["signal_period"], p["signal_type"]

        log_close = np.log(out["close"])
        triple_ema = log_close.ewm(span=n, adjust=False, min_periods=n).mean()
        triple_ema = triple_ema.ewm(span=n, adjust=False, min_periods=n).mean()
        triple_ema = triple_ema.ewm(span=n, adjust=False, min_periods=n).mean()
        trix = 10000 * triple_ema.diff()

        signal = (
            trix.ewm(span=signal_n, adjust=False, min_periods=signal_n).mean()
            if signal_type == "ema"
            else trix.rolling(window=signal_n, min_periods=signal_n).mean()
        )

        out[f"trix_{n}"] = trix
        out[f"trix_{n}_signal_{signal_n}"] = signal
        return out
