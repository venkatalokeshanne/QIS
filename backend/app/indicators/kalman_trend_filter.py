"""Kalman Trend Filter — two independent 1D Kalman filters (short/long period) smoothing price, with the short filter above the long one read as an uptrend.

A genuinely different smoothing family from EMA/SMA: each filter
tracks a state estimate and its own uncertainty, weighting new price
observations more or less heavily bar-to-bar depending on how
confident the filter currently is (the Kalman gain), rather than a
fixed decay factor.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _kalman_filter(close: np.ndarray, period: int, process_noise: float) -> np.ndarray:
    length = len(close)
    x = np.full(length, np.nan)
    measurement_noise = period * 0.1
    state = close[0] if length else np.nan
    variance = 1.0
    for i in range(length):
        if i == 0:
            state = close[0]
        predicted_variance = variance + process_noise
        gain = predicted_variance / (predicted_variance + measurement_noise)
        state = state + gain * (close[i] - state)
        variance = (1.0 - gain) * predicted_variance
        x[i] = state
    return x


@indicator_registry.register("kalman_trend_filter")
class KalmanTrendFilter(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="kalman_trend_filter",
            display_name="Kalman Trend Filter",
            description="Two Kalman-filtered price estimates (short/long period) -- short above long reads as an uptrend.",
            category="trend",
            default_params={"short_period": 50, "long_period": 150, "process_noise": 0.01},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        short_n, long_n, q = p["short_period"], p["long_period"], p["process_noise"]

        close = out["close"].to_numpy()
        short_x = _kalman_filter(close, short_n, q)
        long_x = _kalman_filter(close, long_n, q)

        out[f"kalman_short_{short_n}"] = short_x
        out[f"kalman_long_{long_n}"] = long_x
        out[f"kalman_trend_up_{short_n}_{long_n}"] = short_x > long_x
        return out
