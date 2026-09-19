"""
Regime Classifier.

Classifies "what kind of day is this" for a ticker or a market-proxy
index, off DAILY bars only -- a once-a-day read, not an intraday
flip-flopping signal. This is a classification input for the Daily
Strategy Selector (app.services.calibration_service /
daily_selector_service); it never touches which interval a strategy
actually trades on.

Two independent axes, same convention as the platform's other
ADX/ATR-based readings (see app.strategies.execution's risk-management
ATR usage):
  - trend: "trending" (ADX > adx_threshold) vs "ranging" -- Wilder's
    own standard trending convention.
  - volatility: "high_vol" vs "low_vol" -- ATR as a percent of price,
    split against its own trailing EXPANDING median so it adapts per
    instrument instead of an absolute number that means different
    things for a $5 stock and a $500 one.

Both are trailing/causal by construction (ADX/ATR only look backward,
and the volatility reference is an expanding median, never a
whole-series one) -- so the full classification can be computed ONCE
across a historical range and read off day by day with no lookahead,
both for "today's regime" and for calibration's day-by-day bucketing.
"""

from dataclasses import dataclass

import pandas as pd

from app.indicators.adx import ADX
from app.indicators.atr import ATR


@dataclass(frozen=True)
class RegimeLabel:
    trend: str  # "trending" | "ranging"
    volatility: str  # "high_vol" | "low_vol"

    @property
    def key(self) -> str:
        return f"{self.trend}/{self.volatility}"


def classify_regime_series(
    daily_df: pd.DataFrame,
    period: int = 14,
    adx_threshold: float = 25.0,
    vol_lookback: int = 100,
) -> pd.Series:
    """
    Classify EVERY row of `daily_df` (expected: daily OHLC bars) into a
    RegimeLabel. Returns a pd.Series of RegimeLabel | None, indexed like
    daily_df -- None where ADX/ATR/the volatility reference haven't
    warmed up yet (not enough history), rather than guessing.
    """
    adx_col = f"adx_{period}"
    atr_col = f"atr_{period}"
    enriched = ADX().calculate(daily_df, {"period": period})
    enriched = ATR().calculate(enriched, {"period": period})

    adx = enriched[adx_col]
    atr_pct = enriched[atr_col] / enriched["close"]
    vol_reference = atr_pct.expanding(min_periods=vol_lookback).median()

    trending = adx > adx_threshold
    high_vol = atr_pct > vol_reference
    classifiable = adx.notna() & atr_pct.notna() & vol_reference.notna()

    labels = [
        RegimeLabel(
            trend="trending" if is_trending else "ranging",
            volatility="high_vol" if is_high_vol else "low_vol",
        )
        if is_classifiable
        else None
        for is_classifiable, is_trending, is_high_vol in zip(classifiable, trending, high_vol)
    ]
    return pd.Series(labels, index=daily_df.index, dtype=object)


def classify_regime(
    daily_df: pd.DataFrame,
    period: int = 14,
    adx_threshold: float = 25.0,
    vol_lookback: int = 100,
) -> RegimeLabel | None:
    """The regime as of the LAST bar in `daily_df` -- "what kind of day
    is today," given every daily bar up to and including today. None if
    there isn't enough history yet to classify."""
    if daily_df.empty:
        return None
    series = classify_regime_series(daily_df, period, adx_threshold, vol_lookback)
    return series.iloc[-1]


def combine_market_regime(labels: list[RegimeLabel | None]) -> RegimeLabel | None:
    """
    Combine multiple market-proxy regime reads (e.g. SPY + QQQ [+ SMH])
    into ONE market regime label via majority vote per axis, ignoring
    proxies that aren't classifiable yet. None if none of the proxies
    are classifiable.

    A tied vote (e.g. SPY trending, QQQ ranging) resolves to the less
    committal label ("ranging"/"low_vol") rather than picking a side
    arbitrarily -- with no majority, "conditions are unclear" is the
    more honest read than a coin flip.
    """
    present = [label for label in labels if label is not None]
    if not present:
        return None
    half = len(present) / 2
    trending_votes = sum(1 for label in present if label.trend == "trending")
    high_vol_votes = sum(1 for label in present if label.volatility == "high_vol")
    return RegimeLabel(
        trend="trending" if trending_votes > half else "ranging",
        volatility="high_vol" if high_vol_votes > half else "low_vol",
    )


def regime_bucket_key(ticker_regime: RegimeLabel, market_regime: RegimeLabel) -> str:
    """The combined bucket label calibration buckets trades by, and that
    a daily selection looks up its strategy by -- e.g.
    "ticker=trending/high_vol|market=ranging/low_vol"."""
    return f"ticker={ticker_regime.key}|market={market_regime.key}"
