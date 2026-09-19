"""Minervini Trend Template — Mark Minervini's 8-stage-analysis trend-qualification checklist, scored as how many of its criteria the current bar satisfies.

Ported from a TrendSpider custom-indicator script that scored 10
criteria, the 10th being "Relative Performance (vs SPX) > 70" -- a
percentile RS rank computed across TrendSpider's whole equity
universe. That ranking has no equivalent here: this engine fetches and
scores one symbol's own OHLCV at a time (see Indicator's contract --
"a pure mathematical transformation over OHLCV data"), with no
cross-sectional universe to rank against. That criterion is NOT
ported; this indicator scores the remaining 9, all computable from a
single symbol's own price history.

Criteria (each worth one point toward `minervini_score`, 0-9):
  1. close > SMA(sma_short_period)
  2. close > SMA(sma_mid_period)
  3. close > SMA(sma_long_period)
  4. SMA(sma_short_period) > SMA(sma_mid_period)
  5. SMA(sma_short_period) > SMA(sma_long_period)
  6. SMA(sma_mid_period) > SMA(sma_long_period)
  7. close >= low_multiple x the trailing year_lookback-bar low
  8. close >= high_fraction x the trailing year_lookback-bar high
  9. SMA(sma_long_period) is higher than sma_long_slope_lookback bars ago

Intended for DAILY bars, matching Minervini's own methodology --
`year_lookback` defaults to 252 (trading days in a year) as the
single-timeframe stand-in for the source script's separate weekly
52-week-high/low fetch.

Never returns null criteria for a bar still warming up its longest
SMA -- exactly like the source script, an unmet/not-yet-computable
criterion just scores 0 rather than voiding the whole bar, so
`minervini_score` rises smoothly from 0 as more SMAs warm up.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("minervini_trend_template")
class MinerviniTrendTemplate(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="minervini_trend_template",
            display_name="Minervini Trend Template",
            description=(
                "9 of Mark Minervini's 10 trend-qualification criteria (the universe-wide RS-percentile "
                "criterion is omitted -- see module docstring), scored 0-9."
            ),
            category="trend",
            default_params={
                "sma_short_period": 50,
                "sma_mid_period": 150,
                "sma_long_period": 200,
                "year_lookback": 252,
                "low_multiple": 1.30,
                "high_fraction": 0.75,
                "sma_long_slope_lookback": 30,
                "qualifying_threshold": 9,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        close = out["close"]

        sma_short = close.rolling(window=p["sma_short_period"], min_periods=p["sma_short_period"]).mean()
        sma_mid = close.rolling(window=p["sma_mid_period"], min_periods=p["sma_mid_period"]).mean()
        sma_long = close.rolling(window=p["sma_long_period"], min_periods=p["sma_long_period"]).mean()

        year_low = out["low"].rolling(window=p["year_lookback"], min_periods=p["year_lookback"]).min()
        year_high = out["high"].rolling(window=p["year_lookback"], min_periods=p["year_lookback"]).max()

        sma_long_prior = sma_long.shift(p["sma_long_slope_lookback"])

        # Comparisons against a not-yet-warmed-up (NaN) series evaluate
        # to False rather than raising or propagating NaN, which is
        # exactly the "score 0 for that criterion, don't void the bar"
        # behavior the source script computed criterion-by-criterion.
        score = (
            (close > sma_short).astype(int)
            + (close > sma_mid).astype(int)
            + (close > sma_long).astype(int)
            + (sma_short > sma_mid).astype(int)
            + (sma_short > sma_long).astype(int)
            + (sma_mid > sma_long).astype(int)
            + (close >= p["low_multiple"] * year_low).astype(int)
            + (close >= p["high_fraction"] * year_high).astype(int)
            + (sma_long > sma_long_prior).astype(int)
        )

        out["minervini_score"] = score
        out["minervini_qualified"] = score >= p["qualifying_threshold"]
        return out
