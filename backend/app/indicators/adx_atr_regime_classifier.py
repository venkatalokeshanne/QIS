"""
ADX/ATR Regime Classifier.

Combines three already-independent reads -- ADX trend strength, ATR%
volatility vs. its own recent average, and fast/slow EMA direction --
into ONE categorical regime label per bar, rather than leaving a
caller to reconcile three separate series by hand:

- 2 = trending bull (ADX above threshold, fast EMA > slow EMA)
- 1 = trending bear (ADX above threshold, fast EMA < slow EMA)
- 0 = range (ADX below threshold, volatility normal)
- -1 = high volatility / caution (ATR% has spiked well above its own
  recent average, overriding the other two reads)
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import directional_movement, true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("adx_atr_regime_classifier")
class ADXATRRegimeClassifier(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="adx_atr_regime_classifier",
            display_name="ADX/ATR Regime Classifier",
            description="Combines ADX trend strength, ATR% volatility vs its own average, and EMA direction into one categorical regime label: trend bull/bear, range, or high volatility.",
            category="trend",
            default_params={
                "adx_period": 14,
                "adx_trend_threshold": 22.0,
                "vol_period": 20,
                "vol_multiplier": 1.5,
                "ema_fast_period": 50,
                "ema_slow_period": 200,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        dm = directional_movement(out, p["adx_period"])
        plus_di, minus_di = dm["plus_di"], dm["minus_di"]
        di_sum = (plus_di + minus_di).replace(0, np.nan)
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        adx = wilders_smooth(dx, p["adx_period"])

        atr = wilders_smooth(true_range(out), p["vol_period"])
        atr_pct = atr / out["close"] * 100
        atr_pct_avg = atr_pct.rolling(window=p["vol_period"] * 3, min_periods=p["vol_period"] * 3).mean()
        high_vol = atr_pct > atr_pct_avg * p["vol_multiplier"]

        fast = out["close"].ewm(span=p["ema_fast_period"], adjust=False, min_periods=p["ema_fast_period"]).mean()
        slow = out["close"].ewm(span=p["ema_slow_period"], adjust=False, min_periods=p["ema_slow_period"]).mean()
        bullish = fast > slow

        trending = adx > p["adx_trend_threshold"]
        regime = pd.Series(0.0, index=out.index)
        regime[trending & bullish] = 2.0
        regime[trending & ~bullish] = 1.0
        regime[high_vol] = -1.0
        regime[adx.isna() | atr_pct_avg.isna() | fast.isna() | slow.isna()] = np.nan

        out["adx_atr_regime_adx"] = adx
        out["adx_atr_regime_atr_pct"] = atr_pct
        out["adx_atr_regime"] = regime
        return out
