"""
Candlestick Reversal Patterns.

Flags the classic single/two-bar Japanese candlestick reversal
patterns -- centuries-old, public-domain rice-trading chart reading,
not any platform's proprietary formula:

- Hammer: a small body near the top of the bar's range with a lower
  wick at least `wick_body_ratio` times the body -- a rejection of
  lower prices, bullish after a decline.
- Shooting Star: the mirror of a hammer (small body near the bottom,
  long upper wick) -- bearish after an advance.
- Bullish/Bearish Engulfing: a two-bar pattern where the current bar's
  body fully contains the prior bar's body and closes the opposite
  direction from it.
- Doji: a bar whose body is at most `doji_body_ratio` of its own range
  (open ~= close) -- read as a reversal only in the context of a
  preceding directional move over `trend_lookback` bars, since a doji
  in isolation signals indecision, not direction.
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("candlestick_reversal")
class CandlestickReversal(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="candlestick_reversal",
            display_name="Candlestick Reversal Patterns",
            description="Flags hammer/shooting-star, bullish/bearish engulfing, and trend-context doji reversal patterns.",
            category="price_action",
            default_params={"wick_body_ratio": 2.0, "doji_body_ratio": 0.1, "trend_lookback": 5},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        o, h, l, c = out["open"], out["high"], out["low"], out["close"]
        body = (c - o).abs()
        rng = (h - l).replace(0, np.nan)
        upper_wick = h - pd.concat([o, c], axis=1).max(axis=1)
        lower_wick = pd.concat([o, c], axis=1).min(axis=1) - l

        hammer = (lower_wick >= p["wick_body_ratio"] * body) & (upper_wick <= body) & (body > 0)
        shooting_star = (upper_wick >= p["wick_body_ratio"] * body) & (lower_wick <= body) & (body > 0)

        prev_o, prev_c = o.shift(1), c.shift(1)
        prior_bearish = prev_c < prev_o
        prior_bullish = prev_c > prev_o
        bullish_engulfing = prior_bearish & (c > o) & (o <= prev_c) & (c >= prev_o)
        bearish_engulfing = prior_bullish & (c < o) & (o >= prev_c) & (c <= prev_o)

        is_doji = body <= p["doji_body_ratio"] * rng
        prior_trend = c.shift(1) - c.shift(1 + p["trend_lookback"])
        doji_after_decline = is_doji & (prior_trend < 0)
        doji_after_advance = is_doji & (prior_trend > 0)

        out["bullish_reversal_candle"] = hammer | bullish_engulfing | doji_after_decline
        out["bearish_reversal_candle"] = shooting_star | bearish_engulfing | doji_after_advance
        return out
