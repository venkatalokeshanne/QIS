"""Hurst Exponent (multi-scale rescaled-range) — fits log(R/S) vs. log(window size) by OLS across a log-spaced ladder of window sizes to estimate H: >0.5 trending/persistent, <0.5 mean-reverting, ~0.5 a random walk."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("hurst_exponent")
class HurstExponent(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="hurst_exponent",
            display_name="Hurst Exponent (R/S)",
            description="Multi-scale rescaled-range Hurst exponent -- >0.5 trending, <0.5 mean-reverting, ~0.5 random walk.",
            category="statistics",
            default_params={"lookback": 256, "min_scale": 8, "num_scales": 10, "smooth_period": 4, "recalc_every": 1},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n_lookback, min_scale, num_scales, smooth_period, recalc_every = (
            p["lookback"], p["min_scale"], p["num_scales"], p["smooth_period"], p["recalc_every"]
        )

        close = out["close"].to_numpy()
        returns = np.full(len(close), np.nan)
        returns[1:] = (close[1:] - close[:-1]) / close[:-1]

        max_scale = max(min_scale * 2, n_lookback // 2)
        scales = _scale_ladder(min_scale, max_scale, num_scales)

        h = np.full(len(close), np.nan)
        prev_h = np.nan
        for i in range(n_lookback, len(close)):
            if recalc_every > 1 and i % recalc_every != 0:
                h[i] = prev_h
                continue
            # Newest-return-first, matching the source's retArr[k] = return k bars back.
            window = returns[i - n_lookback + 1 : i + 1][::-1]
            new_h = _hurst_from_returns(window, scales)
            if not np.isnan(new_h):
                prev_h = new_h
            h[i] = prev_h

        out["hurst_h"] = h
        out[f"hurst_h_smooth_{smooth_period}"] = (
            pd.Series(h, index=out.index).rolling(window=smooth_period, min_periods=smooth_period).mean()
        )
        return out


def _scale_ladder(min_scale: int, max_scale: int, num_scales: int) -> list[int]:
    log_min, log_max = np.log(min_scale), np.log(max_scale)
    scales: list[int] = []
    for i in range(num_scales):
        frac = 0.0 if num_scales == 1 else i / (num_scales - 1)
        s_raw = round(np.exp(log_min + frac * (log_max - log_min)))
        s_int = int(min(max_scale, max(min_scale, s_raw)))
        if not scales or scales[-1] != s_int:
            scales.append(s_int)
    return scales


def _hurst_from_returns(window: np.ndarray, scales: list[int]) -> float:
    """OLS slope of log(R/S(n)) vs log(n) across every usable scale."""
    n_total = len(window)
    xs, ys = [], []
    for n in scales:
        n_chunks = n_total // n
        if n_chunks < 1:
            continue
        usable = window[: n_chunks * n].reshape(n_chunks, n)
        dev = usable - usable.mean(axis=1, keepdims=True)
        cum = np.cumsum(dev, axis=1)
        # cmin/cmax track the running cumulative sum's range INCLUDING the
        # implicit starting point of 0 before any deviation is added.
        r = np.maximum(0.0, cum.max(axis=1)) - np.minimum(0.0, cum.min(axis=1))
        sd = np.sqrt((dev**2).mean(axis=1))
        valid = sd > 0
        if not valid.any():
            continue
        rs = float((r[valid] / sd[valid]).mean())
        if rs > 0:
            xs.append(np.log(n))
            ys.append(np.log(rs))

    if len(xs) < 2:
        return np.nan
    x_arr, y_arr = np.array(xs), np.array(ys)
    m = len(x_arr)
    sum_x, sum_y = x_arr.sum(), y_arr.sum()
    sum_xy, sum_xx = (x_arr * y_arr).sum(), (x_arr * x_arr).sum()
    denom = m * sum_xx - sum_x * sum_x
    if denom == 0:
        return np.nan
    return float((m * sum_xy - sum_x * sum_y) / denom)
