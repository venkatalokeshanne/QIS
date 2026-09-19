"""
Rolling Week High/Low.

A live-updating N-WEEK high/low band (52-week and 13-week/quarterly by
default) -- distinct from app.indicators.period_high_low, which only
tracks the CURRENT (single, still-forming) period. This combines the
current week's own still-forming high/low with the max/min of the
last N-1 already-COMPLETED weeks, so the band updates intrabar every
day without ever looking ahead into a week that hasn't happened yet.

The source fetches this via a weekly request.security(...,
lookahead_on) HTF call; this reduces it to same-timeframe math
instead, reusing the ISO-week-key pattern from
app.indicators.custom_anchor_vwap and the current-period-plus-
completed-periods combination pattern from app.indicators.atr_dtr_percent.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry


def _rolling_week_band(
    high: pd.Series, low: pd.Series, week_key: pd.Series, weeks: int
) -> tuple[pd.Series, pd.Series]:
    this_week_high = high.groupby(week_key).cummax()
    this_week_low = low.groupby(week_key).cummin()

    completed_weekly_high = high.groupby(week_key).max()
    completed_weekly_low = low.groupby(week_key).min()

    prior_completed_high = completed_weekly_high.rolling(weeks, min_periods=1).max().shift(1)
    prior_completed_low = completed_weekly_low.rolling(weeks, min_periods=1).min().shift(1)

    rolling_high = pd.concat([this_week_high, week_key.map(prior_completed_high)], axis=1).max(axis=1)
    rolling_low = pd.concat([this_week_low, week_key.map(prior_completed_low)], axis=1).min(axis=1)
    return rolling_high, rolling_low


@indicator_registry.register("rolling_week_high_low")
class RollingWeekHighLow(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="rolling_week_high_low",
            display_name="Rolling Week High/Low",
            description="Live-updating N-week high/low band (52-week and 13-week/quarterly by default): this week's developing high/low combined with the max/min of the prior N-1 completed weeks.",
            category="price_action",
            default_params={"long_window_weeks": 52, "short_window_weeks": 13},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("RollingWeekHighLow requires a DatetimeIndex.")
        out = df.copy()

        week_key = pd.Series(
            out.index.isocalendar().week.to_numpy() + out.index.isocalendar().year.to_numpy() * 100,
            index=out.index,
        )

        long_high, long_low = _rolling_week_band(out["high"], out["low"], week_key, p["long_window_weeks"])
        short_high, short_low = _rolling_week_band(out["high"], out["low"], week_key, p["short_window_weeks"])

        out["rolling_week_high_long"] = long_high
        out["rolling_week_low_long"] = long_low
        out["rolling_week_high_short"] = short_high
        out["rolling_week_low_short"] = short_low
        return out
