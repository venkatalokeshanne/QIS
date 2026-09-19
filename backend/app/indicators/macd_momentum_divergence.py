"""
MACD Momentum Divergence.

Compares confirmed swing pivots in PRICE against confirmed swing
pivots in the MACD HISTOGRAM (not the MACD line itself) to flag two
distinct patterns:

- Divergence: a new price swing high (>= the prior one) lines up with
  a lower histogram swing high -- momentum fading even as price still
  pushes up (mirrored for lows/bearish->bullish). A classic reversal
  warning.
- Continuation: a new histogram swing high/low that's still declining
  in the direction of the prevailing trend (via a simple SMA-slope
  filter) -- momentum still weakening WITH the trend, read as trend
  continuation rather than reversal.

Both price and histogram pivots are tracked independently as running
"current vs. previous confirmed pivot" state, so this is computed with
an explicit bar-by-bar loop rather than a vectorized expression -- the
same pattern used by app.indicators.market_structure.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.macd import MACD
from app.indicators.registry import indicator_registry


def _pivot_series(values: pd.Series, left: int, right: int) -> pd.Series:
    """The pivot's own value, placed at the CONFIRMATION bar (right
    bars after the actual pivot) rather than the pivot's own bar --
    non-repainting, since a rolling window ending at row k only ever
    uses data up to and including k.
    """
    window = left + right + 1

    def is_pivot_high(w: np.ndarray) -> bool:
        return w[left] == w.max() and (w == w[left]).sum() == 1

    mask = values.rolling(window=window, min_periods=window).apply(is_pivot_high, raw=True)
    mask = mask.fillna(0).astype(bool)
    return values.shift(right).where(mask)


@indicator_registry.register("macd_momentum_divergence")
class MACDMomentumDivergence(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="macd_momentum_divergence",
            display_name="MACD Momentum Divergence",
            description="Flags divergence (price swing extends while the MACD histogram's matching swing doesn't) and trend-aligned continuation, from confirmed histogram pivots.",
            category="momentum",
            default_params={
                "fast_period": 6,
                "slow_period": 20,
                "signal_period": 30,
                "pivot_range": 5,
                "trend_sma_period": 50,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = MACD().calculate(
            df, {"fast_period": p["fast_period"], "slow_period": p["slow_period"], "signal_period": p["signal_period"], "source": "close"}
        )
        hist_col = f"macd_hist_{p['fast_period']}_{p['slow_period']}_{p['signal_period']}"
        hc = out[hist_col]
        n = p["pivot_range"]

        price_high_pivot = _pivot_series(out["high"], n, n).to_numpy()
        price_low_pivot = _pivot_series(-out["low"], n, n).to_numpy()
        price_low_pivot = np.where(np.isnan(price_low_pivot), np.nan, -price_low_pivot)
        hist_high_pivot = _pivot_series(hc, n, n).to_numpy()
        hist_low_pivot = _pivot_series(-hc, n, n).to_numpy()
        hist_low_pivot = np.where(np.isnan(hist_low_pivot), np.nan, -hist_low_pivot)

        sma = out["close"].rolling(window=p["trend_sma_period"], min_periods=p["trend_sma_period"]).mean().to_numpy()
        slope = sma - np.concatenate([np.full(3, np.nan), sma[:-3]])
        up_trend = slope > 0
        down_trend = slope < 0

        length = len(out)
        bear_div = np.zeros(length, dtype=bool)
        bull_div = np.zeros(length, dtype=bool)
        bear_cont = np.zeros(length, dtype=bool)
        bull_cont = np.zeros(length, dtype=bool)

        ph1 = ph2 = np.nan
        pl1 = pl2 = np.nan
        mh1 = mh2 = np.nan
        ml1 = ml2 = np.nan

        for i in range(length):
            if not np.isnan(price_high_pivot[i]):
                ph2, ph1 = ph1, price_high_pivot[i]
            if not np.isnan(hist_high_pivot[i]):
                mh2, mh1 = mh1, hist_high_pivot[i]
            if not np.isnan(price_low_pivot[i]):
                pl2, pl1 = pl1, price_low_pivot[i]
            if not np.isnan(hist_low_pivot[i]):
                ml2, ml1 = ml1, hist_low_pivot[i]

            m_bear_rev = not np.isnan(mh2) and mh1 < mh2
            m_bull_rev = not np.isnan(ml2) and ml1 > ml2

            if not np.isnan(price_high_pivot[i]) and not np.isnan(mh2) and ph1 >= ph2 and m_bear_rev:
                bear_div[i] = True
            if not np.isnan(price_low_pivot[i]) and not np.isnan(ml2) and pl1 <= pl2 and m_bull_rev:
                bull_div[i] = True
            if not np.isnan(hist_high_pivot[i]) and not np.isnan(mh2) and mh1 < mh2 and down_trend[i]:
                bear_cont[i] = True
            if not np.isnan(hist_low_pivot[i]) and not np.isnan(ml2) and ml1 > ml2 and up_trend[i]:
                bull_cont[i] = True

        out["macd_momentum_bear_divergence"] = bear_div
        out["macd_momentum_bull_divergence"] = bull_div
        out["macd_momentum_bear_continuation"] = bear_cont
        out["macd_momentum_bull_continuation"] = bull_cont
        return out
