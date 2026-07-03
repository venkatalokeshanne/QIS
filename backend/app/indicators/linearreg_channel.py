"""Linear Regression Channel — a least-squares regression line over a trailing window, banded by its own residual stddev."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _endpoint_and_residual_std(window: np.ndarray) -> tuple[float, float]:
    x = np.arange(len(window))
    slope, intercept = np.polyfit(x, window, 1)
    fitted = slope * x + intercept
    residual_std = float(np.std(window - fitted))
    endpoint = float(slope * (len(window) - 1) + intercept)
    return endpoint, residual_std


@indicator_registry.register("linearreg_channel")
class LinearRegressionChannel(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="linearreg_channel",
            display_name="Linear Regression Channel",
            description="Least-squares regression line over a trailing window, with upper/lower bands at N standard deviations of its own residuals.",
            category="statistics",
            default_params={"period": 20, "std_dev": 2.0, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]

        endpoints = np.full(len(out), np.nan)
        residual_stds = np.full(len(out), np.nan)
        values = src.to_numpy()

        for i in range(n - 1, len(out)):
            window = values[i - n + 1 : i + 1]
            endpoint, residual_std = _endpoint_and_residual_std(window)
            endpoints[i] = endpoint
            residual_stds[i] = residual_std

        mid = pd.Series(endpoints, index=out.index)
        std = pd.Series(residual_stds, index=out.index)

        out[f"linearreg_channel_mid_{n}"] = mid
        out[f"linearreg_channel_upper_{n}"] = mid + p["std_dev"] * std
        out[f"linearreg_channel_lower_{n}"] = mid - p["std_dev"] * std
        return out
