"""VWAP Cloud (Flow Bias) — a band formed by session VWAP-of-high and VWAP-of-low (not the usual close/hlc3-based VWAP), each volume-weighted-smoothed, with the cloud's midpoint slope (scaled by ATR) read as a bullish/bearish/neutral flow bias."""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("vwap_cloud")
class VWAPCloud(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vwap_cloud",
            display_name="VWAP Cloud (Flow Bias)",
            description="Band between session VWAP-of-high and VWAP-of-low, volume-weighted-smoothed, with an ATR-scaled slope read as bullish/bearish/neutral flow bias.",
            category="volume",
            default_params={"smooth_period": 5, "direction_lookback": 3, "neutral_zone_atr": 0.03, "atr_period": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("VWAPCloud requires a DatetimeIndex.")
        out = df.copy()
        smooth_n, dir_n, neutral_atr, atr_n = p["smooth_period"], p["direction_lookback"], p["neutral_zone_atr"], p["atr_period"]

        session_date = pd.Series(out.index.date, index=out.index)

        def _vwap(src: pd.Series) -> pd.Series:
            cum_pv = (src * out["volume"]).groupby(session_date).cumsum()
            cum_vol = out["volume"].groupby(session_date).cumsum().replace(0, np.nan)
            return cum_pv / cum_vol

        vwap_high = _vwap(out["high"])
        vwap_low = _vwap(out["low"])

        # VWMA: volume-weighted moving average over the trailing window.
        def _vwma(src: pd.Series) -> pd.Series:
            pv_sum = (src * out["volume"]).rolling(window=smooth_n, min_periods=smooth_n).sum()
            v_sum = out["volume"].rolling(window=smooth_n, min_periods=smooth_n).sum()
            return pv_sum / v_sum.replace(0, np.nan)

        smooth_high = _vwma(vwap_high)
        smooth_low = _vwma(vwap_low)
        cloud_mid = (smooth_high + smooth_low) / 2

        slope = cloud_mid - cloud_mid.shift(dir_n)
        atr = wilders_smooth(true_range(out), atr_n)
        neutral_zone = atr * neutral_atr

        bullish = slope > neutral_zone
        bearish = slope < -neutral_zone

        out["vwap_cloud_upper"] = smooth_high
        out["vwap_cloud_lower"] = smooth_low
        out["vwap_cloud_mid"] = cloud_mid
        out["vwap_cloud_bullish"] = bullish
        out["vwap_cloud_bearish"] = bearish
        return out
