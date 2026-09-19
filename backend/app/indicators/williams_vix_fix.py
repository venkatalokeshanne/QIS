"""
Williams Vix Fix (Larry Williams).

A synthetic "VIX" built from ordinary price data: how far today's low
sits below the recent highest close, as a percentage -- spiking on
sharp sell-offs the same way the real VIX spikes on fear, without
needing an options market to derive it from. A capitulation signal
fires when that reading pushes above its own Bollinger upper band OR
above its own recent percentile-scaled high, both of which flag an
unusually extreme reading versus its own recent history.

The mirror-image reading (how far today's high sits ABOVE the recent
lowest close) captures the opposite extreme -- euphoric blow-off
spikes -- using the identical band/percentile-extreme logic, just
flipped. Both are exposed since they're two halves of the same
symmetric read, not separate indicators.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("williams_vix_fix")
class WilliamsVixFix(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="williams_vix_fix",
            display_name="Williams Vix Fix",
            description="A synthetic VIX-style fear gauge derived from price alone -- how far today's low sits below the recent highest close -- plus its mirror-image euphoria reading.",
            category="volatility",
            default_params={
                "high_close_period": 22,
                "bb_period": 20,
                "bb_multiplier": 2.0,
                "percentile_lookback": 50,
                "percentile_high": 0.85,
                "percentile_low": 1.01,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        bb_n, pct_n = p["bb_period"], p["percentile_lookback"]

        highest_close = out["close"].rolling(p["high_close_period"], min_periods=p["high_close_period"]).max()
        wvf = (highest_close - out["low"]) / highest_close * 100

        mid_line = wvf.rolling(bb_n, min_periods=bb_n).mean()
        std_dev = wvf.rolling(bb_n, min_periods=bb_n).std() * p["bb_multiplier"]
        upper_band = mid_line + std_dev
        range_high = wvf.rolling(pct_n, min_periods=pct_n).max() * p["percentile_high"]

        lowest_close = out["close"].rolling(p["high_close_period"], min_periods=p["high_close_period"]).min()
        inv_wvf = (out["high"] - lowest_close) / lowest_close * 100

        inv_mid_line = inv_wvf.rolling(bb_n, min_periods=bb_n).mean()
        inv_std_dev = inv_wvf.rolling(bb_n, min_periods=bb_n).std() * p["bb_multiplier"]
        inv_upper_band = inv_mid_line + inv_std_dev
        inv_range_high = inv_wvf.rolling(pct_n, min_periods=pct_n).max() * p["percentile_high"]

        out["wvf"] = wvf
        out["wvf_upper_band"] = upper_band
        out["wvf_range_high"] = range_high
        out["wvf_capitulation_signal"] = (wvf >= upper_band) | (wvf >= range_high)

        out["wvf_inverse"] = inv_wvf
        out["wvf_inverse_upper_band"] = inv_upper_band
        out["wvf_inverse_range_high"] = inv_range_high
        out["wvf_euphoria_signal"] = (inv_wvf >= inv_upper_band) | (inv_wvf >= inv_range_high)
        return out
