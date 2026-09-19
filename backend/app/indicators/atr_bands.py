"""ATR Bands — EMA(period) +/- 1x/2x/3x ATR(period), a widening envelope around a trend baseline.

The source script anchors both the EMA and ATR to the DAILY timeframe
regardless of the chart's own timeframe (via request.security), which
this platform's single-timeframe Indicator interface has no
equivalent for -- this is the same-timeframe version instead. At a
daily interval it's identical to the source; at an intraday interval
it's a same-timeframe analogue, not a literal port of the
daily-anchored multi-timeframe behavior.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("atr_bands")
class ATRBands(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="atr_bands",
            display_name="ATR Bands",
            description="EMA baseline +/- 1x/2x/3x ATR -- a widening envelope around a trend baseline.",
            category="volatility",
            default_params={"ema_period": 20, "atr_period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        ema_n, atr_n = p["ema_period"], p["atr_period"]

        base = out["close"].ewm(span=ema_n, adjust=False, min_periods=ema_n).mean()
        atr = wilders_smooth(true_range(out), atr_n)

        for mult in (1, 2, 3):
            out[f"atr_bands_upper_{mult}_{ema_n}_{atr_n}"] = base + atr * mult
            out[f"atr_bands_lower_{mult}_{ema_n}_{atr_n}"] = base - atr * mult
        return out
