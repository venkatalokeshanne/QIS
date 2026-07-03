"""MACD (Gerald Appel) — difference of two EMAs, with its own EMA as a signal line and their difference as a histogram."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("macd")
class MACD(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="macd",
            display_name="MACD",
            description="EMA(fast) - EMA(slow), with a signal-line EMA and histogram.",
            category="momentum",
            default_params={"fast_period": 12, "slow_period": 26, "signal_period": 9, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        fast_ema = src.ewm(span=p["fast_period"], adjust=False).mean()
        slow_ema = src.ewm(span=p["slow_period"], adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=p["signal_period"], adjust=False).mean()

        suffix = f"{p['fast_period']}_{p['slow_period']}_{p['signal_period']}"
        out[f"macd_line_{suffix}"] = macd_line
        out[f"macd_signal_{suffix}"] = signal_line
        out[f"macd_hist_{suffix}"] = macd_line - signal_line
        return out
