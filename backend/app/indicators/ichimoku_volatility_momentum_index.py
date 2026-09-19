"""
Ichimoku Volatility & Momentum Index.

Repurposes two Ichimoku building blocks as a standalone volatility/
momentum oscillator, independent of the cloud's usual overlay role:

- Cloud Width Index (CWI): |Span A - Span B|, how far apart the two
  cloud-forming averages are. A widening cloud reads as expanding
  volatility/conviction; a narrowing one reads as compression.
- TK Distance: |Tenkan-sen - Kijun-sen|, the gap between the fast and
  slow Ichimoku lines -- a short-term momentum/divergence proxy.

Both use the standard fixed Ichimoku lookbacks (9/26/52); only the
smoothing applied to CWI is configurable. ATR is included alongside
as a conventional volatility cross-check.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry

_MA_FUNCS = {
    "sma": lambda s, n: s.rolling(window=n, min_periods=n).mean(),
    "ema": lambda s, n: s.ewm(span=n, adjust=False, min_periods=n).mean(),
    "wma": lambda s, n: s.rolling(window=n, min_periods=n).apply(
        lambda w: (w * range(1, len(w) + 1)).sum() / (len(w) * (len(w) + 1) / 2), raw=True
    ),
    "rma": wilders_smooth,
}


@indicator_registry.register("ichimoku_volatility_momentum_index")
class IchimokuVolatilityMomentumIndex(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ichimoku_volatility_momentum_index",
            display_name="Ichimoku Volatility & Momentum Index",
            description="Cloud Width Index (Span A vs Span B gap) and TK Distance (Tenkan vs Kijun gap), repurposing Ichimoku's building blocks as a standalone volatility/momentum oscillator, plus ATR for cross-check.",
            category="volatility",
            default_params={"ma_length": 9, "ma_type": "sma", "atr_length": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        tenkan = (out["high"].rolling(9, min_periods=9).max() + out["low"].rolling(9, min_periods=9).min()) / 2
        kijun = (out["high"].rolling(26, min_periods=26).max() + out["low"].rolling(26, min_periods=26).min()) / 2
        span_a = (tenkan + kijun) / 2
        span_b = (out["high"].rolling(52, min_periods=52).max() + out["low"].rolling(52, min_periods=52).min()) / 2

        cwi = (span_a - span_b).abs()
        tk_distance = (tenkan - kijun).abs()

        ma_func = _MA_FUNCS[p["ma_type"]]
        cwi_ma = ma_func(cwi, p["ma_length"])

        out["ichimoku_vmi_cwi"] = cwi
        out["ichimoku_vmi_cwi_ma"] = cwi_ma
        out["ichimoku_vmi_tk_distance"] = tk_distance
        out[f"ichimoku_vmi_atr_{p['atr_length']}"] = wilders_smooth(true_range(out), p["atr_length"])
        return out
