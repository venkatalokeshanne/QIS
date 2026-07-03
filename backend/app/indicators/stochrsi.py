"""StochRSI (Tushar Chande & Stanley Kroll) — the Stochastic formula applied to RSI instead of price, more sensitive than RSI alone."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("stochrsi")
class StochRSI(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="stochrsi",
            display_name="Stochastic RSI",
            description="The Stochastic formula applied to RSI instead of price -- more sensitive than RSI alone.",
            category="momentum",
            default_params={"rsi_period": 14, "stoch_period": 14, "k_period": 3, "d_period": 3, "source": "close"},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        delta = out[p["source"]].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = wilders_smooth(gain, p["rsi_period"])
        avg_loss = wilders_smooth(loss, p["rsi_period"])
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        n = p["stoch_period"]
        lowest_rsi = rsi.rolling(window=n, min_periods=n).min()
        highest_rsi = rsi.rolling(window=n, min_periods=n).max()
        rng = (highest_rsi - lowest_rsi).replace(0, np.nan)
        stoch_rsi = 100 * (rsi - lowest_rsi) / rng

        k = stoch_rsi.rolling(window=p["k_period"], min_periods=p["k_period"]).mean()
        d = k.rolling(window=p["d_period"], min_periods=p["d_period"]).mean()

        suffix = f"{p['rsi_period']}_{n}"
        out[f"stochrsi_k_{suffix}"] = k
        out[f"stochrsi_d_{suffix}"] = d
        return out
