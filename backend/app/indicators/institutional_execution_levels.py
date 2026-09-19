"""
Institutional Daily Execution Levels.

Prior-day pivot-based demand/supply zones, distinct from the standard
1/3-of-range S1/R1 in app.indicators.pivot_points: the entry zones sit
0.382 of the prior day's range off the pivot (a Fibonacci-flavored
variant), stops are cushioned by a fraction of the prior day's ATR
rather than sitting exactly at the prior high/low, and each zone
carries an explicit risk:reward target rather than a mirrored S/R
level. Held constant through the session -- computed once from the
PRIOR completed day, non-repainting.

The source fetches yesterday's H/L/C and ATR via an explicit daily
request.security call; this reduces the same series to same-timeframe
math instead, reusing the daily-resample-then-shift-then-map pattern
established in app.indicators.atr_dtr_percent.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("institutional_execution_levels")
class InstitutionalExecutionLevels(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="institutional_execution_levels",
            display_name="Institutional Daily Execution Levels",
            description="Prior-day pivot +/- 0.382 of the day's range as buy/sell entry zones, with ATR-cushioned stops and explicit risk:reward targets, held constant through the session.",
            category="price_action",
            default_params={"atr_period": 14, "risk_reward": 2.0},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("InstitutionalExecutionLevels requires a DatetimeIndex.")
        out = df.copy()
        n = p["atr_period"]
        rr = p["risk_reward"]

        session_date = pd.Series(out.index.date, index=out.index)
        daily_high = out["high"].groupby(session_date).max()
        daily_low = out["low"].groupby(session_date).min()
        daily_close = out["close"].groupby(session_date).last()
        daily_df = pd.DataFrame({"high": daily_high, "low": daily_low, "close": daily_close})
        daily_atr = wilders_smooth(true_range(daily_df), n)

        prior_high = session_date.map(daily_high.shift(1))
        prior_low = session_date.map(daily_low.shift(1))
        prior_close = session_date.map(daily_close.shift(1))
        prior_atr = session_date.map(daily_atr.shift(1))

        pivot = (prior_high + prior_low + prior_close) / 3
        day_range = prior_high - prior_low

        buy_entry = pivot - day_range * 0.382
        buy_stop = prior_low - prior_atr * 0.25
        buy_target = buy_entry + (buy_entry - buy_stop) * rr

        sell_entry = pivot + day_range * 0.382
        sell_stop = prior_high + prior_atr * 0.25
        sell_target = sell_entry - (sell_stop - sell_entry) * rr

        out["iel_buy_entry"] = buy_entry
        out["iel_buy_stop"] = buy_stop
        out["iel_buy_target"] = buy_target
        out["iel_sell_entry"] = sell_entry
        out["iel_sell_stop"] = sell_stop
        out["iel_sell_target"] = sell_target
        return out
