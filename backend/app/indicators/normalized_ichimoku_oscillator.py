"""
Normalized Ichimoku Oscillator.

Each of the four Ichimoku reference lines (Tenkan, Kijun, Span A, Span
B) is reframed as an ATR-normalized distance from price instead of an
absolute overlay level -- putting all four on one comparable oscillator
scale regardless of the instrument's price magnitude, and making "how
stretched is price from this line, in volatility-adjusted terms"
directly readable. Distinct from
app.indicators.ichimoku_volatility_momentum_index (cloud width and
Tenkan-Kijun gap, not per-line ATR-normalized price deviation) and
from app.indicators.ema_distance_percentile_rank (a single EMA, not
the four Ichimoku reference lines).
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("normalized_ichimoku_oscillator")
class NormalizedIchimokuOscillator(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="normalized_ichimoku_oscillator",
            display_name="Normalized Ichimoku Oscillator",
            description="ATR-normalized distance of price from each Ichimoku reference line (Tenkan, Kijun, Span A, Span B), putting them all on one comparable oscillator scale.",
            category="momentum",
            default_params={"tenkan_period": 9, "kijun_period": 26, "span_b_period": 52, "atr_period": 14, "kijun_ma_period": 10},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        def donchian_mid(n: int) -> pd.Series:
            return (out["high"].rolling(n, min_periods=n).max() + out["low"].rolling(n, min_periods=n).min()) / 2

        tenkan = donchian_mid(p["tenkan_period"])
        kijun = donchian_mid(p["kijun_period"])
        span_a = (tenkan + kijun) / 2
        span_b = donchian_mid(p["span_b_period"])
        atr = wilders_smooth(true_range(out), p["atr_period"]).replace(0, pd.NA)

        osc_tenkan = (out["close"] - tenkan) / atr
        osc_kijun = (out["close"] - kijun) / atr
        osc_span_a = (out["close"] - span_a) / atr
        osc_span_b = (out["close"] - span_b) / atr
        kijun_ma = osc_kijun.ewm(span=p["kijun_ma_period"], adjust=False, min_periods=p["kijun_ma_period"]).mean()

        out["nio_tenkan_dev"] = osc_tenkan
        out["nio_kijun_dev"] = osc_kijun
        out["nio_span_a_dev"] = osc_span_a
        out["nio_span_b_dev"] = osc_span_b
        out["nio_kijun_dev_ma"] = kijun_ma
        return out
