"""
Volatility Contraction Pattern Scan.

A classic VCP-style screen: a stock that made a fresh 52-week high
within the last `recent_high_lookback` bars, now resting in a tight,
still-narrowing range on shrinking volume, with its long-term trend
still healthy -- the setup traders watch for a low-risk continuation
entry once the range finally breaks. All conditions must agree:

- Volume dry-up: short-term average volume has fallen to
  <= volume_ratio_max of the long-term average.
- Range tight: the high-low range over `range_period` is
  <= range_max_pct of price, AND narrower than it was
  `range_compare_bars` bars ago.
- Recent 52-week high: a new 52-week high occurred within the last
  `recent_high_lookback` bars.
- Trend healthy: price above both the 50- and 200-period SMA, and the
  200-period SMA has been rising for the last 20 bars.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


@indicator_registry.register("volatility_contraction_pattern_scan")
class VolatilityContractionPatternScan(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="volatility_contraction_pattern_scan",
            display_name="Volatility Contraction Pattern Scan",
            description="Flags a fresh-52-week-high stock now resting in a tight, shrinking-volume, still-narrowing range with a healthy long-term uptrend -- a classic VCP setup.",
            category="volatility",
            default_params={
                "short_vol_period": 10,
                "long_vol_period": 50,
                "volume_ratio_max": 0.70,
                "range_period": 10,
                "range_max_pct": 10.0,
                "range_compare_bars": 20,
                "recent_high_lookback": 40,
                "year_bars": 252,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()

        short_vol = out["volume"].rolling(p["short_vol_period"], min_periods=p["short_vol_period"]).mean()
        long_vol = out["volume"].rolling(p["long_vol_period"], min_periods=p["long_vol_period"]).mean()
        vol_ratio = short_vol / long_vol.replace(0, pd.NA)
        volume_dry_up = vol_ratio <= p["volume_ratio_max"]

        range_high = out["high"].rolling(p["range_period"], min_periods=p["range_period"]).max()
        range_low = out["low"].rolling(p["range_period"], min_periods=p["range_period"]).min()
        range_pct = (range_high - range_low) / out["close"] * 100
        range_tight = range_pct <= p["range_max_pct"]
        range_contracting = range_pct < range_pct.shift(p["range_compare_bars"])

        prior_52w_high = out["high"].shift(1).rolling(p["year_bars"], min_periods=p["year_bars"]).max()
        new_high = out["high"] > prior_52w_high
        recent_new_high = new_high.rolling(p["recent_high_lookback"], min_periods=1).max().astype(bool)

        sma200 = out["close"].rolling(200, min_periods=200).mean()
        sma50 = out["close"].rolling(50, min_periods=50).mean()
        sma200_rising = (sma200 > sma200.shift(5)) & (sma200.shift(5) > sma200.shift(10)) & (
            sma200.shift(10) > sma200.shift(15)
        ) & (sma200.shift(15) > sma200.shift(20))
        above_50 = out["close"] > sma50
        above_200 = out["close"] > sma200

        out["vcp_volume_ratio"] = vol_ratio
        out["vcp_range_pct"] = range_pct
        out["vcp_scan_match"] = (
            volume_dry_up
            & range_tight
            & range_contracting
            & recent_new_high
            & sma200_rising
            & above_50
            & above_200
        )
        return out
