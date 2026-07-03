"""Variable Index Dynamic Average (Tushar Chande) — an EMA whose smoothing constant scales with a volatility ratio (CMO magnitude), so it adapts to how choppy vs. trending the market currently is."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vidya")
class VIDYA(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vidya",
            display_name="Variable Index Dynamic Average",
            description="An EMA whose smoothing speed scales with a CMO-based volatility ratio -- adapts to trending vs. choppy conditions.",
            category="overlap",
            default_params={"period": 14, "cmo_period": 9, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n, cmo_n = p["period"], p["cmo_period"]
        src = out[p["source"]]

        delta = src.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        sum_gain = gain.rolling(window=cmo_n, min_periods=cmo_n).sum()
        sum_loss = loss.rolling(window=cmo_n, min_periods=cmo_n).sum()
        total = (sum_gain + sum_loss).replace(0, np.nan)
        volatility_ratio = ((sum_gain - sum_loss) / total).abs()

        alpha = 2 / (n + 1)
        values = src.to_numpy()
        vr = volatility_ratio.to_numpy()
        vidya = np.full(len(out), np.nan)

        started = False
        for i in range(len(out)):
            if np.isnan(vr[i]):
                continue
            if not started:
                vidya[i] = values[i]
                started = True
            else:
                vidya[i] = alpha * vr[i] * values[i] + (1 - alpha * vr[i]) * vidya[i - 1]

        out[f"vidya_{n}"] = vidya
        return out
