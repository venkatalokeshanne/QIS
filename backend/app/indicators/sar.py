"""Parabolic SAR (J. Welles Wilder) — a trailing stop-and-reverse level that accelerates as a trend extends, flipping sides when price crosses it."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("sar")
class ParabolicSAR(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="sar",
            display_name="Parabolic SAR",
            description="A trailing stop-and-reverse level that accelerates as a trend extends.",
            category="overlap",
            default_params={"af_start": 0.02, "af_increment": 0.02, "af_max": 0.2},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        high, low = out["high"].to_numpy(), out["low"].to_numpy()
        n = len(out)
        sar = np.full(n, np.nan)

        if n < 2:
            out["sar"] = sar
            return out

        is_uptrend = True
        af = p["af_start"]
        ep = high[0]
        sar[0] = low[0]

        for i in range(1, n):
            prev_sar = sar[i - 1]
            candidate = prev_sar + af * (ep - prev_sar)

            if is_uptrend:
                candidate = min(candidate, low[i - 1], low[i - 2] if i >= 2 else low[i - 1])
                if low[i] < candidate:
                    is_uptrend = False
                    sar[i] = ep
                    ep = low[i]
                    af = p["af_start"]
                else:
                    sar[i] = candidate
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + p["af_increment"], p["af_max"])
            else:
                candidate = max(candidate, high[i - 1], high[i - 2] if i >= 2 else high[i - 1])
                if high[i] > candidate:
                    is_uptrend = True
                    sar[i] = ep
                    ep = high[i]
                    af = p["af_start"]
                else:
                    sar[i] = candidate
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + p["af_increment"], p["af_max"])

        out["sar"] = sar
        return out
