"""
Volatility Regime Trend Ribbon.

An adaptive trend line whose own smoothing speed changes with the
market's CURRENT volatility regime rather than staying fixed: ATR is
ranked against its own trailing history (a percentile, not a raw
threshold, so it's self-relative per instrument -- same idea as
app.indicators.ema_distance_percentile_rank), bucketed into
low/normal/high volatility, and that bucket picks both a smoothing
length (faster in low vol, slower in high vol) and a confidence-band
width scale for an ATR-offset envelope around the trend line.

Distinct from app.indicators.kama (which adapts continuously via an
efficiency ratio) and app.indicators.adx_atr_regime_classifier (which
outputs a categorical trend/range/high-vol label from ADX+ATR+EMA,
not a smoothing-adaptive trend line with bands): this indicator's
regime read is volatility-percentile-only, and it manifests as a
live trend line + envelope rather than a label.

Both the smoothing alpha (which changes bar-to-bar with the regime)
and the confirmed direction (persists across bars until price closes
through a band edge) are recursive/stateful, so this is computed with
an explicit bar-by-bar loop rather than a vectorized pandas expression.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


def _percent_rank(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period + 1, min_periods=period + 1).apply(
        lambda w: (w[:-1] < w[-1]).sum() / period * 100, raw=True
    )


@indicator_registry.register("volatility_regime_trend_ribbon")
class VolatilityRegimeTrendRibbon(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volatility_regime_trend_ribbon",
            display_name="Volatility Regime Trend Ribbon",
            description="An adaptive trend line + ATR-offset confidence band whose smoothing speed and band width switch with the current ATR-percentile volatility regime (low/normal/high).",
            category="trend",
            default_params={
                "atr_period": 14,
                "percentile_lookback": 100,
                "low_threshold": 33.0,
                "high_threshold": 67.0,
                "low_vol_length": 18,
                "normal_vol_length": 28,
                "high_vol_length": 42,
                "band_multiple": 1.0,
                "low_vol_band_scale": 0.75,
                "normal_vol_band_scale": 1.0,
                "high_vol_band_scale": 1.35,
                "source": "hlc3",
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        src = (
            (out["high"] + out["low"] + out["close"]) / 3
            if p["source"] == "hlc3"
            else out[p["source"]]
        )

        atr = wilders_smooth(true_range(out), p["atr_period"])
        atr_percentile = _percent_rank(atr, p["percentile_lookback"])

        low_thr, high_thr = p["low_threshold"], p["high_threshold"]
        regime = np.where(atr_percentile <= low_thr, 0, np.where(atr_percentile >= high_thr, 2, 1))
        regime = regime.astype(float)
        regime[atr_percentile.isna().to_numpy()] = np.nan

        length_by_regime = {0: p["low_vol_length"], 1: p["normal_vol_length"], 2: p["high_vol_length"]}
        scale_by_regime = {0: p["low_vol_band_scale"], 1: p["normal_vol_band_scale"], 2: p["high_vol_band_scale"]}

        src_arr = src.to_numpy()
        atr_arr = atr.to_numpy()
        n = len(out)

        trend = np.full(n, np.nan)
        upper = np.full(n, np.nan)
        lower = np.full(n, np.nan)
        direction = np.zeros(n, dtype=np.int64)

        prev_trend = np.nan
        prev_direction = 0
        for i in range(n):
            r = regime[i]
            if np.isnan(r):
                direction[i] = prev_direction
                continue

            adaptive_length = length_by_regime[int(r)]
            alpha = 2.0 / (adaptive_length + 1.0)
            cur_src = src_arr[i]

            if np.isnan(prev_trend):
                cur_trend = cur_src
            else:
                cur_trend = prev_trend + alpha * (cur_src - prev_trend)
            trend[i] = cur_trend
            prev_trend = cur_trend

            cur_atr = atr_arr[i]
            if np.isnan(cur_atr):
                direction[i] = prev_direction
                continue

            band_width = cur_atr * p["band_multiple"] * scale_by_regime[int(r)]
            up, lo = cur_trend + band_width, cur_trend - band_width
            upper[i] = up
            lower[i] = lo

            close_price = out["close"].iloc[i]
            if close_price > up:
                cur_direction = 1
            elif close_price < lo:
                cur_direction = -1
            else:
                cur_direction = prev_direction
            direction[i] = cur_direction
            prev_direction = cur_direction

        direction_series = pd.Series(direction, index=out.index)
        prev_direction_series = direction_series.shift(1).fillna(0)
        bullish_switch = (direction_series == 1) & (prev_direction_series != 1)
        bearish_switch = (direction_series == -1) & (prev_direction_series != -1)

        out["vrtr_regime"] = regime
        out["vrtr_trend"] = trend
        out["vrtr_upper"] = upper
        out["vrtr_lower"] = lower
        out["vrtr_direction"] = direction_series
        out["vrtr_bullish_switch"] = bullish_switch
        out["vrtr_bearish_switch"] = bearish_switch
        return out
