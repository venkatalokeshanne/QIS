"""
Dynamic Volatility Bear Threshold.

A drawdown-from-rolling-high definition of "bear market" that scales
with the instrument's OWN realized volatility instead of using a
fixed percentage (the common "-20% = bear market" rule of thumb):
annualized volatility (stdev of returns, scaled by bars-per-year for
whatever timeframe this runs on) times a multiple sets how far below
the rolling high counts as "bear," clamped to a sane 5%-60% band so
the line never goes dead on either a very calm or a very violent
instrument. A long SMA then distinguishes a genuine bull recovery
from just "not yet in bear territory."

Three states per bar: bear (close below the dynamic threshold), bull
(above the threshold AND above the confirm SMA), recovering (above
the threshold but still below the confirm SMA).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _bars_per_year(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return 252.0
    inferred_minutes = (index[1] - index[0]).total_seconds() / 60.0
    if inferred_minutes <= 0:
        return 252.0
    if inferred_minutes < 60 * 24:
        return 252.0 * 390.0 / inferred_minutes
    return 252.0


@indicator_registry.register("dynamic_volatility_bear_threshold")
class DynamicVolatilityBearThreshold(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="dynamic_volatility_bear_threshold",
            display_name="Dynamic Volatility Bear Threshold",
            description="A rolling-high drawdown threshold scaled by the instrument's own annualized volatility (clamped 5%-60%), with a long SMA distinguishing bull recovery from still-in-range.",
            category="trend",
            default_params={
                "lookback": 252,
                "volatility_multiple": 1.2,
                "confirm_sma_period": 200,
                "min_drawdown_pct": 5.0,
                "max_drawdown_pct": 60.0,
            },
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        out = df.copy()
        lb = p["lookback"]

        bars_per_year = (
            _bars_per_year(out.index) if isinstance(out.index, pd.DatetimeIndex) else 252.0
        )

        returns = out["close"].pct_change()
        annualized_vol = returns.rolling(lb, min_periods=lb).std() * np.sqrt(bars_per_year)

        rolling_high = out["high"].rolling(lb, min_periods=lb).max()

        drawdown_threshold = annualized_vol * p["volatility_multiple"]
        drawdown_threshold = drawdown_threshold.clip(
            lower=p["min_drawdown_pct"] / 100.0, upper=p["max_drawdown_pct"] / 100.0
        )
        bear_level = rolling_high * (1 - drawdown_threshold)

        confirm_sma = out["close"].rolling(p["confirm_sma_period"], min_periods=p["confirm_sma_period"]).mean()

        in_bear = out["close"] < bear_level
        above_sma = out["close"] > confirm_sma
        in_bull = ~in_bear & above_sma
        state = pd.Series(
            np.select([in_bear, in_bull], ["bear", "bull"], default="recovering"), index=out.index
        )
        warmup = rolling_high.isna() | annualized_vol.isna() | confirm_sma.isna()
        state[warmup] = None

        out["dvbt_rolling_high"] = rolling_high
        out["dvbt_annualized_vol"] = annualized_vol
        out["dvbt_bear_level"] = bear_level
        out["dvbt_confirm_sma"] = confirm_sma
        out["dvbt_state"] = state
        return out
