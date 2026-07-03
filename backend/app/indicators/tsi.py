"""True Strength Index (William Blau) — double-smoothed price change relative to double-smoothed absolute price change."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("tsi")
class TSI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="tsi",
            display_name="True Strength Index",
            description="Double-smoothed momentum relative to double-smoothed absolute momentum -- a low-noise oscillator.",
            category="momentum",
            default_params={"long_period": 25, "short_period": 13, "signal_period": 7, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        long_n, short_n = p["long_period"], p["short_period"]

        momentum = src.diff()
        smoothed_momentum = momentum.ewm(span=long_n, adjust=False, min_periods=long_n).mean()
        double_smoothed_momentum = smoothed_momentum.ewm(span=short_n, adjust=False, min_periods=short_n).mean()

        abs_momentum = momentum.abs()
        smoothed_abs = abs_momentum.ewm(span=long_n, adjust=False, min_periods=long_n).mean()
        double_smoothed_abs = smoothed_abs.ewm(span=short_n, adjust=False, min_periods=short_n).mean()

        tsi = 100 * double_smoothed_momentum / double_smoothed_abs.replace(0, np.nan)
        signal = tsi.ewm(span=p["signal_period"], adjust=False, min_periods=p["signal_period"]).mean()

        out["tsi"] = tsi
        out["tsi_signal"] = signal
        return out
