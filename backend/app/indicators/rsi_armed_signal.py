"""RSI Armed Signal — an RSI-EMA signal line with a one-shot "arm/disarm" gate: crossing the midline (50) re-arms it, and it disarms the instant it fires an overbought or oversold signal, so it won't repeat-fire while pinned at an extreme."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("rsi_armed_signal")
class RSIArmedSignal(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rsi_armed_signal",
            display_name="RSI Armed Signal",
            description="RSI-EMA signal line gated by an arm/disarm state -- re-arms on a midline (50) cross, disarms after firing, so repeated extremes only fire once per swing.",
            category="momentum",
            default_params={"rsi_period": 14, "signal_period": 14, "upper_level": 65.0, "lower_level": 35.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        rsi_n, sig_n, upper, lower = p["rsi_period"], p["signal_period"], p["upper_level"], p["lower_level"]

        delta = out["close"].diff()
        avg_gain = delta.clip(lower=0).ewm(alpha=1 / rsi_n, adjust=False, min_periods=rsi_n).mean()
        avg_loss = (-delta.clip(upper=0)).ewm(alpha=1 / rsi_n, adjust=False, min_periods=rsi_n).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_val = 100 - (100 / (1 + rs))
        sig_line = rsi_val.ewm(span=sig_n, adjust=False, min_periods=sig_n).mean()

        sig = sig_line.to_numpy()
        length = len(sig)
        armed = np.full(length, np.nan)
        upper_signal = np.zeros(length, dtype=bool)
        lower_signal = np.zeros(length, dtype=bool)

        is_armed = True
        for i in range(length):
            if np.isnan(sig[i]):
                continue
            if i > 0 and not np.isnan(sig[i - 1]) and ((sig[i - 1] - 50) * (sig[i] - 50) < 0 or sig[i] == 50):
                is_armed = True  # crossed (or landed on) the midline this bar
            crossed_up = i > 0 and not np.isnan(sig[i - 1]) and sig[i] > upper and sig[i - 1] <= upper
            crossed_down = i > 0 and not np.isnan(sig[i - 1]) and sig[i] < lower and sig[i - 1] >= lower
            fire_upper = crossed_up and is_armed
            fire_lower = crossed_down and is_armed
            upper_signal[i] = fire_upper
            lower_signal[i] = fire_lower
            if fire_upper or fire_lower:
                is_armed = False
            armed[i] = is_armed

        out[f"rsi_armed_signal_{rsi_n}_{sig_n}"] = sig_line
        out["rsi_armed_signal_is_armed"] = armed
        out["rsi_armed_signal_overbought_fire"] = upper_signal
        out["rsi_armed_signal_oversold_fire"] = lower_signal
        return out
