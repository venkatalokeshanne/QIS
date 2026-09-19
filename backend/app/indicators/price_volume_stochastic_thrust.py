"""
Price & Volume Stochastic Thrust.

A directional "thrust" bar: a new higher high (or lower low) on
above-average bar-over-bar volume, closing convincingly in that
direction, but only counted while the stochastic oscillator is
already sitting at an extreme (overbought or oversold) -- read as a
volume-confirmed push happening right where momentum was already
stretched, rather than a routine breakout in the middle of a range.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("price_volume_stochastic_thrust")
class PriceVolumeStochasticThrust(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="price_volume_stochastic_thrust",
            display_name="Price & Volume Stochastic Thrust",
            description="A new high/low on above-average volume with a decisive close, counted only while the stochastic oscillator is already at an overbought/oversold extreme.",
            category="momentum",
            default_params={
                "stoch_k_period": 14,
                "stoch_k_smoothing": 3,
                "overbought": 75.0,
                "oversold": 25.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        fast_k = 100 * (out["close"] - out["low"].rolling(p["stoch_k_period"], min_periods=p["stoch_k_period"]).min()) / (
            out["high"].rolling(p["stoch_k_period"], min_periods=p["stoch_k_period"]).max()
            - out["low"].rolling(p["stoch_k_period"], min_periods=p["stoch_k_period"]).min()
        )
        slow_k = fast_k.rolling(p["stoch_k_smoothing"], min_periods=p["stoch_k_smoothing"]).mean()
        stoch_extreme = (slow_k >= p["overbought"]) | (slow_k <= p["oversold"])

        higher_high = out["high"] > out["high"].shift(1)
        lower_low = out["low"] < out["low"].shift(1)
        higher_volume = out["volume"] > out["volume"].shift(1)
        bull_close = out["close"] > out["open"]
        bear_close = out["close"] < out["open"]

        out["pvst_bull_thrust"] = higher_high & higher_volume & bull_close & stoch_extreme
        out["pvst_bear_thrust"] = lower_low & higher_volume & bear_close & stoch_extreme
        return out
