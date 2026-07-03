"""SMI Ergodic Indicator (William Blau) — a double-smoothed momentum ratio (the same double-EMA-smoothing idea behind TSI), with its own signal-line EMA and a histogram (oscillator) of the two."""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("smi_ergodic")
class SMIErgodic(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="smi_ergodic",
            display_name="SMI Ergodic Indicator",
            description="Double-smoothed momentum ratio (Blau's TSI-style construction) with a signal line and oscillator histogram.",
            category="momentum",
            default_params={"long_period": 20, "short_period": 5, "signal_period": 5, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        src = out[p["source"]]
        long_n, short_n = p["long_period"], p["short_period"]

        momentum = src.diff()
        smoothed_momentum = momentum.ewm(span=long_n, adjust=False).mean()
        double_smoothed_momentum = smoothed_momentum.ewm(span=short_n, adjust=False).mean()

        abs_momentum = momentum.abs()
        smoothed_abs = abs_momentum.ewm(span=long_n, adjust=False).mean()
        double_smoothed_abs = smoothed_abs.ewm(span=short_n, adjust=False).mean()

        smi = 100 * double_smoothed_momentum / double_smoothed_abs.replace(0, float("nan"))
        signal = smi.ewm(span=p["signal_period"], adjust=False).mean()

        out["smi_ergodic"] = smi
        out["smi_ergodic_signal"] = signal
        out["smi_ergodic_oscillator"] = smi - signal
        return out
