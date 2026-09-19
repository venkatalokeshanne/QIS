"""Thermometer Oscillator — a -5..+5 composite of three simple checks (close vs. prior close, close vs. today's open, today's range vs. prior close), smoothed by a configurable moving average."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("thermometer_oscillator")
class ThermometerOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="thermometer_oscillator",
            display_name="Thermometer Oscillator",
            description="Composite -5..+5 momentum reading (close vs prior close, close vs today's open, range vs prior close), smoothed.",
            category="momentum",
            default_params={"ma_period": 9, "ma_type": "ema"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, ma_type = p["ma_period"], p["ma_type"]

        prev_close = out["close"].shift(1)
        comp1 = pd.Series(0, index=out.index, dtype=float)
        comp1[out["close"] > prev_close] = 2
        comp1[out["close"] < prev_close] = -2

        comp2 = pd.Series(0, index=out.index, dtype=float)
        comp2[out["close"] > out["open"]] = 2
        comp2[out["close"] < out["open"]] = -2

        comp3 = pd.Series(0, index=out.index, dtype=float)
        comp3[out["low"] > prev_close] = 1
        comp3[out["high"] < prev_close] = -1

        thermo = comp1 + comp2 + comp3

        if ma_type == "sma":
            ma = thermo.rolling(window=n, min_periods=n).mean()
        elif ma_type == "wma":
            weights = pd.Series(range(1, n + 1), dtype=float)
            ma = thermo.rolling(window=n, min_periods=n).apply(lambda w: (w * weights.to_numpy()).sum() / weights.sum(), raw=True)
        elif ma_type == "rma":
            ma = wilders_smooth(thermo, n)
        else:  # ema (default)
            ma = thermo.ewm(span=n, adjust=False, min_periods=n).mean()

        out[f"thermometer_{n}"] = thermo
        out[f"thermometer_{n}_ma_{ma_type}"] = ma
        return out
