"""Standard Error Bands (Jon Andersen) — a linear regression line banded by multiples of its own standard error, tightening as the fit gets more reliable rather than using a fixed multiple like Bollinger Bands."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _endpoint_and_std_error(window: np.ndarray) -> tuple[float, float]:
    n = len(window)
    x = np.arange(n)
    slope, intercept = np.polyfit(x, window, 1)
    fitted = slope * x + intercept
    residuals = window - fitted
    # Standard error of the regression estimate (n-2 degrees of freedom).
    std_error = float(np.sqrt(np.sum(residuals**2) / max(n - 2, 1)))
    endpoint = float(slope * (n - 1) + intercept)
    return endpoint, std_error


@indicator_registry.register("standard_error_bands")
class StandardErrorBands(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="standard_error_bands",
            display_name="Standard Error Bands",
            description="A linear regression line banded by multiples of its own standard error -- tightens as the fit improves.",
            category="volatility",
            default_params={"period": 20, "std_error_multiple": 2.0, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        src = out[p["source"]]
        values = src.to_numpy()

        endpoints = np.full(len(out), np.nan)
        std_errors = np.full(len(out), np.nan)

        for i in range(n - 1, len(out)):
            window = values[i - n + 1 : i + 1]
            endpoint, std_error = _endpoint_and_std_error(window)
            endpoints[i] = endpoint
            std_errors[i] = std_error

        mid = pd.Series(endpoints, index=out.index)
        se = pd.Series(std_errors, index=out.index)

        out[f"seb_mid_{n}"] = mid
        out[f"seb_upper_{n}"] = mid + p["std_error_multiple"] * se
        out[f"seb_lower_{n}"] = mid - p["std_error_multiple"] * se
        return out
