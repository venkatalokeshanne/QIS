"""Bars Since Band Touch — a mean-reversion timer: counts consecutive bars price has stayed entirely outside an MA +/- ATR band, resetting to 0 every time price touches back into it. A high count flags a stretch that's gone unusually long without reverting toward the average -- a candidate for "statistically due."

ma_type supports ema/sma/rma (the source also offers wma/vwma, dropped
here for simplicity since ema -- the source's own default -- already
covers the primary use case)."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry

_MA_FUNCS = {
    "ema": lambda src, n: src.ewm(span=n, adjust=False, min_periods=n).mean(),
    "sma": lambda src, n: src.rolling(window=n, min_periods=n).mean(),
    "rma": wilders_smooth,
}


@indicator_registry.register("bars_since_band_touch")
class BarsSinceBandTouch(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="bars_since_band_touch",
            display_name="Bars Since Band Touch",
            description="Consecutive bars price has stayed entirely outside an MA +/- ATR band, resetting on every touch back into it.",
            category="statistics",
            default_params={"ma_period": 120, "ma_type": "ema", "atr_period": 14, "atr_multiple": 1.0, "target_bars": 100},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        ma_n, ma_type, atr_n, atr_mult, target = p["ma_period"], p["ma_type"], p["atr_period"], p["atr_multiple"], p["target_bars"]

        ma_func = _MA_FUNCS[ma_type]
        ma = ma_func(out["close"], ma_n)
        atr = wilders_smooth(true_range(out), atr_n)

        upper = ma + atr * atr_mult
        lower = ma - atr * atr_mult
        touches_zone = (out["low"] <= upper) & (out["high"] >= lower)

        touched = touches_zone.to_numpy()
        length = len(out)
        bar_count = np.zeros(length, dtype=int)
        count = 0
        for i in range(length):
            count = 0 if touched[i] else count + 1
            bar_count[i] = count

        out[f"bars_since_band_touch_{ma_n}_{atr_n}"] = bar_count
        out[f"bars_since_band_touch_{ma_n}_{atr_n}_at_target"] = bar_count == target
        return out
