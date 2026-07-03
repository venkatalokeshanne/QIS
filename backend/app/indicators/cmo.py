"""Chande Momentum Oscillator (Tushar Chande) — like RSI, but using raw (not Wilder-smoothed) sums and unbounded gain/loss symmetry, giving a -100..100 range."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("cmo")
class CMO(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="cmo",
            display_name="Chande Momentum Oscillator",
            description="(sum of gains - sum of losses) / (sum of gains + sum of losses) * 100, over a trailing window.",
            category="momentum",
            default_params={"period": 14, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["period"]
        delta = out[p["source"]].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        sum_gain = gain.rolling(window=n, min_periods=n).sum()
        sum_loss = loss.rolling(window=n, min_periods=n).sum()
        total = (sum_gain + sum_loss).replace(0, np.nan)

        out[f"cmo_{n}"] = 100 * (sum_gain - sum_loss) / total
        return out
