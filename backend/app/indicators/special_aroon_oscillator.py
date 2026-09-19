"""Special Aroon Oscillator — the classic Aroon Up/Down formula (100 x how recently a window's extreme occurred), but applied to a single EMA-blended smoothed price series instead of separate raw high/low -- a smoother, less noise-prone variant of the standard Aroon Oscillator (already in app.indicators.aroonosc)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("special_aroon_oscillator")
class SpecialAroonOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="special_aroon_oscillator",
            display_name="Special Aroon Oscillator",
            description="Aroon Up/Down (how recently a window's extreme occurred) applied to a smoothed price series rather than raw high/low.",
            category="trend",
            default_params={"length": 28, "smooth": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, smooth, source = p["length"], p["smooth"], p["source"]

        src = out[source]
        alpha = 2 / (1 + smooth)
        ema_part = src.ewm(span=smooth, adjust=False, min_periods=smooth).mean()
        smoothed = ema_part * (1 - alpha) + src * alpha

        window = n + 1
        arr = smoothed.to_numpy()
        length = len(arr)
        up = np.full(length, np.nan)
        down = np.full(length, np.nan)
        for i in range(window - 1, length):
            segment = arr[i - window + 1 : i + 1]
            if np.isnan(segment).any():
                continue
            up[i] = 100 * np.argmax(segment) / n
            down[i] = 100 * np.argmin(segment) / n

        out[f"special_aroon_up_{n}_{smooth}"] = up
        out[f"special_aroon_down_{n}_{smooth}"] = down
        out[f"special_aroon_osc_{n}_{smooth}"] = up - down
        return out
