"""
ATR/DTR Percent.

Compares the current session's DEVELOPING range (today's running
high-minus-low, still building as the day goes on) against
YESTERDAY'S already-completed ATR -- a fixed benchmark held constant
through the whole session, rather than a moving ATR that changes
underneath you intrabar. Answers "how much of a typical day's range
has today already used up."

The source script fetches both series from an explicit higher
timeframe via request.security; this computes the same two same-
timeframe reductions instead: the developing range reuses
app.indicators.period_high_low's "current period so far" pattern, and
the prior-day ATR is the last confirmed ATR reading before today's
first bar, held constant through the session (a one-session-lag
reduction of the source's `[1]`-offset HTF fetch).
"""

from typing import Any

import numpy as np
import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators._shared import true_range, wilders_smooth
from app.indicators.registry import indicator_registry


@indicator_registry.register("atr_dtr_percent")
class ATRDTRPercent(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="atr_dtr_percent",
            display_name="ATR/DTR Percent",
            description="Today's developing range so far, as a percentage of yesterday's already-completed ATR -- a fixed intraday benchmark.",
            category="volatility",
            default_params={"atr_length": 14},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("ATRDTRPercent requires a DatetimeIndex.")
        out = df.copy()
        n = p["atr_length"]

        session_date = pd.Series(out.index.date, index=out.index)
        dtr = out["high"].groupby(session_date).cummax() - out["low"].groupby(session_date).cummin()

        daily_close = out["close"].groupby(session_date).last()
        daily_high = out["high"].groupby(session_date).max()
        daily_low = out["low"].groupby(session_date).min()
        daily_df = pd.DataFrame({"high": daily_high, "low": daily_low, "close": daily_close})
        daily_atr = wilders_smooth(true_range(daily_df), n)
        prior_daily_atr = daily_atr.shift(1)

        atr_by_day = session_date.map(prior_daily_atr)
        out["dtr"] = dtr
        out["prior_day_atr"] = atr_by_day
        out["atr_dtr_percent"] = np.where(atr_by_day > 0, dtr / atr_by_day * 100, np.nan)
        return out
