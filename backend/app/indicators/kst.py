"""Know Sure Thing / KST (Martin Pring) — a weighted sum of four smoothed ROC readings across increasing lookbacks, plus its own signal-line SMA."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("kst")
class KST(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kst",
            display_name="Know Sure Thing (KST)",
            description="Weighted sum of four smoothed ROC readings across increasing lookbacks, plus a signal line.",
            category="momentum",
            default_params={
                "roc1": 10, "roc2": 15, "roc3": 20, "roc4": 30,
                "sma1": 10, "sma2": 10, "sma3": 10, "sma4": 15,
                "signal_period": 9, "source": "close",
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        def roc(period: int) -> pd.Series:
            return (src - src.shift(period)) / src.shift(period).replace(0, np.nan) * 100

        rcma1 = roc(p["roc1"]).rolling(window=p["sma1"], min_periods=p["sma1"]).mean()
        rcma2 = roc(p["roc2"]).rolling(window=p["sma2"], min_periods=p["sma2"]).mean()
        rcma3 = roc(p["roc3"]).rolling(window=p["sma3"], min_periods=p["sma3"]).mean()
        rcma4 = roc(p["roc4"]).rolling(window=p["sma4"], min_periods=p["sma4"]).mean()

        kst = rcma1 * 1 + rcma2 * 2 + rcma3 * 3 + rcma4 * 4
        signal = kst.rolling(window=p["signal_period"], min_periods=p["signal_period"]).mean()

        out["kst"] = kst
        out["kst_signal"] = signal
        return out
