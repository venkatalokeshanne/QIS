"""Chop Detector — a smoothed wick-to-body ratio (5-bar centered weighted average), damped during breakouts (large body relative to recent wick size) so a real trend impulse doesn't get mistaken for chop."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("chop_detector")
class ChopDetector(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="chop_detector",
            display_name="Chop Detector",
            description="Smoothed wick/body ratio, damped during breakouts -- high values flag choppy/wicky conditions, low values flag clean directional bars.",
            category="volatility",
            default_params={
                "lookback": 20,
                "center_weight": 0.5,
                "near_weight": 0.25,
                "far_weight": 0.10,
                "breakout_damping": True,
                "w5": 0.7,
                "breakout_trigger": 1.0,
                "damping_strength": 0.5,
                "hold_bars": 4,
                "output_smoothing": 2,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["lookback"]
        w_center, w_near, w_far = p["center_weight"], p["near_weight"], p["far_weight"]
        use_damp, w5, brk_trig, brk_str, hold_bars, smooth_n = (
            p["breakout_damping"], p["w5"], p["breakout_trigger"], p["damping_strength"], p["hold_bars"], p["output_smoothing"]
        )

        wick = (out["high"] - out[["open", "close"]].max(axis=1)) + (out[["open", "close"]].min(axis=1) - out["low"])
        body = (out["close"] - out["open"]).abs()
        raw = wick.rolling(window=n, min_periods=n).mean() / body.rolling(window=n, min_periods=n).mean()

        # 5-tap centered weighted average of raw[t-4..t]: raw[t-2] gets w_center,
        # raw[t-1]/raw[t-3] get w_near, raw[t]/raw[t-4] get w_far.
        denom = w_center + 2 * w_near + 2 * w_far
        base = (
            raw.shift(2) * w_center
            + (raw.shift(1) + raw.shift(3)) * w_near
            + (raw + raw.shift(4)) * w_far
        ) / denom

        if use_damp:
            wick_ref = wick.rolling(window=5, min_periods=5).mean() * w5 + wick.rolling(window=10, min_periods=10).mean() * (1 - w5)
            brk = (body / wick_ref.replace(0, np.nan)).where(wick_ref > 0, 0.0)
            brk_now = (brk - brk_trig).clip(lower=0)
            brk_max = brk_now.rolling(window=hold_bars, min_periods=1).max()
            damp = 1 / (1 + brk_str * brk_max)
        else:
            damp = 1.0

        v = (base * damp).rolling(window=smooth_n, min_periods=smooth_n).mean()
        out[f"chop_detector_{n}"] = v
        return out
