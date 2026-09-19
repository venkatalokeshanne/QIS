"""
VWAP Structure Momentum Bias.

A composite bias score combining three independent reads into one
number rather than leaving a caller to reconcile them by hand:

1. VWAP position -- session VWAP plus volume-weighted standard-
   deviation bands (same math as app.indicators.vwap_stdev_bands).
2. Market structure -- the last two confirmed swing highs and the
   last two confirmed swing lows: higher-high-and-higher-low reads
   bullish, lower-high-and-lower-low reads bearish, anything else is
   neutral.
3. Momentum -- the rate-of-change of price's own distance from VWAP
   (in standard-deviation units), so it's measuring whether the
   stretch from fair value is accelerating or fading, not raw price
   momentum.

Each of structure and momentum contributes -1/0/+1; the bias score is
their sum (-2..+2). Distinct from app.indicators.vwap_slope_trend
(which reads VWAP's own slope, not price's distance from it) and from
app.indicators.market_structure (which doesn't combine with VWAP or
momentum at all).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("vwap_structure_momentum_bias")
class VWAPStructureMomentumBias(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="vwap_structure_momentum_bias",
            display_name="VWAP Structure Momentum Bias",
            description="Composite -2..+2 bias combining session VWAP position, swing-high/low market structure, and the momentum of price's own distance from VWAP.",
            category="trend",
            default_params={"swing_length": 5, "momentum_length": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("VWAPStructureMomentumBias requires a DatetimeIndex.")
        out = df.copy()

        session_date = pd.Series(out.index.date, index=out.index)
        typical_price = (out["high"] + out["low"] + out["close"]) / 3
        pv = typical_price * out["volume"]
        p2v = typical_price * typical_price * out["volume"]

        cum_vol = out["volume"].groupby(session_date).cumsum().replace(0, np.nan)
        cum_pv = pv.groupby(session_date).cumsum()
        cum_p2v = p2v.groupby(session_date).cumsum()

        vwap = cum_pv / cum_vol
        variance = (cum_p2v / cum_vol - vwap * vwap).clip(lower=0)
        stdev = np.sqrt(variance)

        left = right = p["swing_length"]
        window = left + right + 1

        def is_pivot_high(w: np.ndarray) -> bool:
            return w[left] == w.max() and (w == w[left]).sum() == 1

        def is_pivot_low(w: np.ndarray) -> bool:
            return w[left] == w.min() and (w == w[left]).sum() == 1

        high_mask = (
            out["high"].rolling(window, min_periods=window).apply(is_pivot_high, raw=True).fillna(0).astype(bool)
        )
        low_mask = (
            out["low"].rolling(window, min_periods=window).apply(is_pivot_low, raw=True).fillna(0).astype(bool)
        )

        pivot_high_value = out["high"].shift(right).where(high_mask)
        pivot_low_value = out["low"].shift(right).where(low_mask)

        def _last_and_prev(pivot_value: pd.Series) -> tuple[pd.Series, pd.Series]:
            last = pivot_value.ffill()
            events = pivot_value.dropna()
            prev_at_event = events.shift(1)
            prev = pd.Series(np.nan, index=pivot_value.index)
            prev.loc[prev_at_event.index] = prev_at_event.to_numpy()
            return last, prev.ffill()

        last_ph, prev_ph = _last_and_prev(pivot_high_value)
        last_pl, prev_pl = _last_and_prev(pivot_low_value)

        have_all_four = last_ph.notna() & prev_ph.notna() & last_pl.notna() & prev_pl.notna()
        bull_struct = have_all_four & (last_ph > prev_ph) & (last_pl > prev_pl)
        bear_struct = have_all_four & (last_ph < prev_ph) & (last_pl < prev_pl)
        struct_dir = pd.Series(np.select([bull_struct, bear_struct], [1, -1], default=0), index=out.index)

        distance = ((out["close"] - vwap) / stdev.replace(0, np.nan)).fillna(0.0)
        momentum = distance - distance.shift(p["momentum_length"])
        mom_dir = pd.Series(np.select([momentum > 0, momentum < 0], [1, -1], default=0), index=out.index)

        bias = struct_dir + mom_dir

        out["vsmb_vwap"] = vwap
        out["vsmb_stdev"] = stdev
        out["vsmb_structure_direction"] = struct_dir
        out["vsmb_momentum"] = momentum
        out["vsmb_momentum_direction"] = mom_dir
        out["vsmb_bias"] = bias
        return out
