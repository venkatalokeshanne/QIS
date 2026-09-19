"""
Fourier Extrapolation Forecast (DFT).

At each bar, fits a trailing window of closes with a linear trend
plus a truncated Discrete Fourier Transform of the DETRENDED residual
(only the low harmonics -- the high ones mostly fit noise), then
extrapolates that fitted trend+cycle model one bar forward. The
forecast is anchored so it starts exactly at the current close
(matching the source's `anchor_to_close` default), so what's exposed
is genuinely a next-bar prediction made from data available up to and
including the current bar -- not a plotted-forward line computed once
on the last bar the way the source script draws it.

This is inherently a per-bar recomputation (the whole point is a
rolling re-fit), so it's implemented as an explicit bar-by-bar loop.
The basis matrices (cos/sin at each harmonic/offset) depend only on
the window length, which is fixed, so they're precomputed once outside
the loop rather than rebuilt every bar.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("dft_forecast")
class DFTForecast(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dft_forecast",
            display_name="Fourier Extrapolation Forecast (DFT)",
            description="A rolling trend+truncated-Fourier fit of a trailing price window, extrapolated one bar ahead and anchored to the current close.",
            category="trend",
            default_params={"window_length": 128, "num_harmonics": 8},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["window_length"]
        m = min(p["num_harmonics"], n // 2 - 1)

        close = out["close"].to_numpy()
        length = len(out)
        forecast = np.full(length, np.nan)

        t = np.arange(n)
        sum_x = t.sum()
        sum_x2 = (t * t).sum()
        denom = n * sum_x2 - sum_x * sum_x

        harmonics = np.arange(m + 1)
        angle_matrix = 2 * np.pi * np.outer(harmonics, t) / n  # (m+1, n)
        cos_basis = np.cos(angle_matrix)
        sin_basis = np.sin(angle_matrix)

        angle_next = 2 * np.pi * harmonics * n / n  # t = n (one bar past the window's last index)
        cos_next = np.cos(angle_next)
        sin_next = np.sin(angle_next)

        for i in range(n - 1, length):
            window = close[i - n + 1 : i + 1]

            sum_y = window.sum()
            sum_xy = (t * window).sum()
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n

            resid = window - (intercept + slope * t)
            re = resid @ cos_basis.T
            im = -(resid @ sin_basis.T)

            model_now = intercept + slope * (n - 1) + (re[0] / n + 2.0 / n * (re[1:] * cos_basis[1:, -1] - im[1:] * sin_basis[1:, -1]).sum())
            offset = close[i] - model_now

            recon_next = re[0] / n + 2.0 / n * (re[1:] * cos_next[1:] - im[1:] * sin_next[1:]).sum()
            forecast[i] = intercept + slope * n + recon_next + offset

        out["dft_forecast_next_bar"] = forecast
        return out
