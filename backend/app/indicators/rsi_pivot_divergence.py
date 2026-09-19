"""
RSI Pivot Divergence.

Confirmed regular divergence between price and RSI, using RSI's own
swing pivots (not a fixed lookback compare): a bullish divergence
confirms when a new RSI swing low is higher than the PRIOR RSI swing
low while price's low at that same pivot is lower than the prior
one -- selling losing steam even as price still pushes to a new low.
Bearish divergence mirrors this on swing highs. Pivots more than
`max_bars_between_pivots` apart are not compared (too stale to be a
meaningful pair). Distinct from
app.indicators.macd_momentum_divergence (pivots on the MACD
histogram, not on RSI itself).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _pivot_mask(values: pd.Series, left: int, right: int, is_high: bool) -> np.ndarray:
    """True at the CONFIRMATION bar (right bars after the actual pivot),
    non-repainting -- a rolling window ending at row k only ever uses
    data up to and including k, so this never claims to know about a
    pivot before it's actually confirmable. The pivot's own value sits
    `right` bars before wherever this is True (which is exactly the
    offset the calling loop below reads).
    """
    window = left + right + 1

    def check(w: np.ndarray) -> bool:
        target = w.max() if is_high else w.min()
        return w[left] == target and (w == w[left]).sum() == 1

    mask = values.rolling(window=window, min_periods=window).apply(check, raw=True)
    return mask.fillna(0).astype(bool).to_numpy()


@indicator_registry.register("rsi_pivot_divergence")
class RSIPivotDivergence(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rsi_pivot_divergence",
            display_name="RSI Pivot Divergence",
            description="Confirmed regular bullish/bearish divergence between price and RSI, using RSI's own swing pivots rather than a fixed lookback.",
            category="momentum",
            default_params={"rsi_period": 14, "pivot_range": 5, "max_bars_between_pivots": 60},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        n = p["rsi_period"]

        delta = out["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        avg_loss = loss.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        left = right = p["pivot_range"]
        rsi_high_mask = _pivot_mask(rsi, left, right, is_high=True)
        rsi_low_mask = _pivot_mask(rsi, left, right, is_high=False)
        rsi_arr = rsi.to_numpy()
        high_arr, low_arr = out["high"].to_numpy(), out["low"].to_numpy()

        length = len(out)
        bull_div = np.zeros(length, dtype=bool)
        bear_div = np.zeros(length, dtype=bool)

        prev_pl_rsi = prev_pl_price = prev_pl_bar = np.nan
        prev_ph_rsi = prev_ph_price = prev_ph_bar = np.nan
        max_gap = p["max_bars_between_pivots"]

        for i in range(length):
            if rsi_low_mask[i]:
                pl_rsi, pl_price, pl_bar = rsi_arr[i - right], low_arr[i - right], i - right
                if not np.isnan(prev_pl_rsi) and (pl_bar - prev_pl_bar) <= max_gap:
                    if pl_price < prev_pl_price and pl_rsi > prev_pl_rsi:
                        bull_div[i] = True
                prev_pl_rsi, prev_pl_price, prev_pl_bar = pl_rsi, pl_price, pl_bar

            if rsi_high_mask[i]:
                ph_rsi, ph_price, ph_bar = rsi_arr[i - right], high_arr[i - right], i - right
                if not np.isnan(prev_ph_rsi) and (ph_bar - prev_ph_bar) <= max_gap:
                    if ph_price > prev_ph_price and ph_rsi < prev_ph_rsi:
                        bear_div[i] = True
                prev_ph_rsi, prev_ph_price, prev_ph_bar = ph_rsi, ph_price, ph_bar

        out[f"rsi_{n}"] = rsi
        out["rsi_bullish_divergence"] = bull_div
        out["rsi_bearish_divergence"] = bear_div
        return out
