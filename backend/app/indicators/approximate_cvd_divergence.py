"""
Approximate CVD Divergence.

Estimates cumulative volume delta (buy vs. sell pressure) from
ordinary OHLCV bars alone, without needing tick-level bid/ask data:
each bar's volume is split by how efficiently it closed relative to
its own range (a wide bar that closes near its high is read as mostly
buy-side, near its low mostly sell-side), signed by candle direction,
accumulated since a periodic reset, and smoothed with a signal MA.
Confirmed price/CVD divergence is flagged from swing pivots on both
series. Distinct from an exact CVD built from tick or lower-timeframe
data (which this platform's OHLCV bars can't reconstruct) -- this is
a same-bar approximation, most useful as a directional-pressure proxy
rather than a literal buy/sell volume count.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("approximate_cvd_divergence")
class ApproximateCVDDivergence(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="approximate_cvd_divergence",
            display_name="Approximate CVD Divergence",
            description="A same-bar approximation of cumulative volume delta from OHLCV alone (no tick data), reset periodically, with confirmed price/CVD swing divergence.",
            category="volume",
            default_params={"reset_period": "D", "signal_ma_period": 21, "pivot_range": 5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("ApproximateCVDDivergence requires a DatetimeIndex.")
        out = df.copy()

        hl_range = out["high"] - out["low"]
        efficiency = np.where(hl_range == 0, 0.0, (out["close"] - out["open"]) / hl_range.replace(0, np.nan))
        efficiency = np.nan_to_num(efficiency, nan=0.0)
        volume_weight = out["volume"] * np.abs(efficiency)

        delta = np.where(
            out["close"] > out["open"],
            volume_weight + out["volume"] * 0.1,
            np.where(
                out["close"] < out["open"],
                -volume_weight - out["volume"] * 0.1,
                np.where(hl_range == 0, 0.0, out["volume"] * ((out["close"] - out["low"]) / hl_range.replace(0, np.nan) - 0.5)),
            ),
        )
        delta = pd.Series(np.nan_to_num(delta, nan=0.0), index=out.index)

        if p["reset_period"] == "D":
            period_key = pd.Series(out.index.date, index=out.index)
        else:
            period_key = pd.Series(out.index.to_period(p["reset_period"]), index=out.index)
        cvd = delta.groupby(period_key).cumsum()

        signal_ma = cvd.ewm(span=p["signal_ma_period"], adjust=False, min_periods=p["signal_ma_period"]).mean()

        left = right = p["pivot_range"]
        window = left + right + 1

        def pivot_mask(values: pd.Series, is_high: bool) -> np.ndarray:
            def check(w: np.ndarray) -> bool:
                target = w.max() if is_high else w.min()
                return w[left] == target and (w == w[left]).sum() == 1

            mask = values.rolling(window=window, min_periods=window).apply(check, raw=True)
            return mask.fillna(0).astype(bool).to_numpy()

        price_high_mask = pivot_mask(out["high"], is_high=True)
        price_low_mask = pivot_mask(out["low"], is_high=False)
        high_arr, low_arr, cvd_arr = out["high"].to_numpy(), out["low"].to_numpy(), cvd.to_numpy()

        length = len(out)
        bull_div = np.zeros(length, dtype=bool)
        bear_div = np.zeros(length, dtype=bool)
        prev_high_price = prev_high_cvd = np.nan
        prev_low_price = prev_low_cvd = np.nan

        for i in range(length):
            if price_high_mask[i]:
                hp, hc = high_arr[i - right], cvd_arr[i - right]
                if not np.isnan(prev_high_price) and hp > prev_high_price and hc < prev_high_cvd:
                    bear_div[i] = True
                prev_high_price, prev_high_cvd = hp, hc
            if price_low_mask[i]:
                lp, lc = low_arr[i - right], cvd_arr[i - right]
                if not np.isnan(prev_low_price) and lp < prev_low_price and lc > prev_low_cvd:
                    bull_div[i] = True
                prev_low_price, prev_low_cvd = lp, lc

        out["approx_cvd"] = cvd
        out["approx_cvd_signal"] = signal_ma
        out["approx_cvd_bull_divergence"] = bull_div
        out["approx_cvd_bear_divergence"] = bear_div
        return out
