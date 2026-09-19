"""Gann HiLo Activator — a fast trend-flip line: switches to (and then trails) SMA(low) once close breaks above it, or SMA(high) once close breaks below it, holding its prior side on every other bar."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("gann_hilo_activator")
class GannHiLoActivator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="gann_hilo_activator",
            display_name="Gann HiLo Activator",
            description="Trend-flip line that trails SMA(low) while up, SMA(high) while down -- flips only when close breaks the opposite band.",
            category="trend",
            default_params={"period": 3},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]

        hi = out["high"].rolling(window=n, min_periods=n).mean().to_numpy()
        lo = out["low"].rolling(window=n, min_periods=n).mean().to_numpy()
        close = out["close"].to_numpy()
        length = len(out)

        direction = np.full(length, np.nan)
        line = np.full(length, np.nan)
        prev_dir = np.nan
        for i in range(length):
            if np.isnan(hi[i]) or np.isnan(lo[i]):
                continue
            if close[i] > hi[i]:
                prev_dir = 1.0
            elif close[i] < lo[i]:
                prev_dir = -1.0
            # else: holds prev_dir, which stays nan until the first resolved bar
            direction[i] = prev_dir
            if not np.isnan(prev_dir):
                # Up (prev_dir=1): the line trails at the LOW band (support). Down
                # (prev_dir=-1): the line trails at the HIGH band (resistance).
                line[i] = lo[i] if prev_dir == 1.0 else hi[i]

        out[f"gann_hilo_{n}"] = line
        out[f"gann_hilo_direction_{n}"] = direction
        return out
