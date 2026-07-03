"""MACD Ext — the standard MACD, but letting the fast/slow/signal stage each independently choose SMA or EMA."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _ma(series: pd.Series, period: int, ma_type: str) -> pd.Series:
    if ma_type == "sma":
        return series.rolling(window=period, min_periods=period).mean()
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


@indicator_registry.register("macdext")
class MACDExt(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="macdext",
            display_name="MACD Ext",
            description="MACD with an independently selectable moving-average type (SMA or EMA) for each stage.",
            category="momentum",
            default_params={
                "fast_period": 12,
                "fast_ma_type": "ema",
                "slow_period": 26,
                "slow_ma_type": "ema",
                "signal_period": 9,
                "signal_ma_type": "ema",
                "source": "close",
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]

        fast = _ma(src, p["fast_period"], p["fast_ma_type"])
        slow = _ma(src, p["slow_period"], p["slow_ma_type"])
        macd_line = fast - slow
        signal_line = _ma(macd_line, p["signal_period"], p["signal_ma_type"])

        suffix = f"{p['fast_period']}_{p['slow_period']}_{p['signal_period']}"
        out[f"macdext_{suffix}"] = macd_line
        out[f"macdext_signal_{suffix}"] = signal_line
        out[f"macdext_hist_{suffix}"] = macd_line - signal_line
        return out
