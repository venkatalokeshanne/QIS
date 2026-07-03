"""
Session Opening Range.

Unlike app.indicators.opening_range (which anchors to wherever each
day's first bar in the DATA happens to fall), this anchors to a FIXED
wall-clock session start -- New York (09:30), London (03:00), Asian
(19:00), or Globex (18:00), all in US/Eastern -- so opening-range
breakout logic runs consistently regardless of what hours a given
dataset covers, and correctly handles sessions that cross midnight
(Asian, Globex) by grouping their post-midnight bars back into the
session that started the evening before.

Assumes the DataFrame's DatetimeIndex is already in US/Eastern (or
whatever timezone these clock times should be read in) -- consistent
with how the rest of this platform treats timestamps; no timezone
conversion happens here or anywhere else in the codebase. If your data
isn't already in that timezone, session boundaries will be wrong.
"""

from typing import Any

import pandas as pd

from app.domain.interfaces.indicator import Indicator, IndicatorMetadata
from app.indicators.registry import indicator_registry

# (session_start_minute_of_day, session_end_minute_of_day) in US/Eastern.
# end <= start means the session crosses midnight.
_SESSIONS = {
    "new_york": (9 * 60 + 30, 16 * 60),
    "london": (3 * 60, 12 * 60),
    "asian": (19 * 60, 4 * 60),
    "globex": (18 * 60, 17 * 60),
}


@indicator_registry.register("session_opening_range")
class SessionOpeningRange(Indicator):
    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="session_opening_range",
            display_name="Session Opening Range",
            description=(
                "High/low of the first N minutes of a fixed-clock-time session "
                "(New York, London, Asian, or Globex), held for that session."
            ),
            category="price_action",
            default_params={"session": "new_york", "minutes": 15},
        )

    def calculate(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        p = self.validate_params(params)
        if p["session"] not in _SESSIONS:
            raise ValueError(f"Unknown session '{p['session']}'. Choose one of {list(_SESSIONS)}.")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("SessionOpeningRange requires a DatetimeIndex.")

        start_min, end_min = _SESSIONS[p["session"]]
        crosses_midnight = end_min <= start_min
        minutes_of_day = df.index.hour * 60 + df.index.minute

        if crosses_midnight:
            in_session = (minutes_of_day >= start_min) | (minutes_of_day < end_min)
        else:
            in_session = (minutes_of_day >= start_min) & (minutes_of_day < end_min)
        in_session = pd.Series(in_session, index=df.index)

        session_date = pd.Series(df.index.date, index=df.index)
        if crosses_midnight:
            after_midnight = pd.Series(minutes_of_day < end_min, index=df.index)
            prior_day = (pd.Series(df.index, index=df.index) - pd.Timedelta(days=1)).dt.date
            session_date = session_date.mask(after_midnight, prior_day)

        or_end_min = start_min + p["minutes"]
        if crosses_midnight and or_end_min > 24 * 60:
            or_end_min -= 24 * 60
            in_window = (minutes_of_day >= start_min) | (minutes_of_day < or_end_min)
        else:
            in_window = (minutes_of_day >= start_min) & (minutes_of_day < or_end_min)
        in_window = pd.Series(in_window, index=df.index)

        suffix = f"{p['session']}_{p['minutes']}"
        high_col, low_col = f"session_or_high_{suffix}", f"session_or_low_{suffix}"
        remaining_col = f"session_minutes_remaining_{suffix}"

        out = df.copy()
        masked_high = out["high"].where(in_window & in_session)
        masked_low = out["low"].where(in_window & in_session)

        or_high = masked_high.groupby(session_date).cummax().groupby(session_date).transform("max")
        or_low = masked_low.groupby(session_date).cummin().groupby(session_date).transform("min")

        out[high_col] = or_high.where(in_session)
        out[low_col] = or_low.where(in_session)

        if crosses_midnight:
            minutes_of_day_s = pd.Series(minutes_of_day, index=df.index)
            evening = minutes_of_day_s >= start_min
            remaining = pd.Series(index=df.index, dtype=float)
            remaining[evening] = (24 * 60 - minutes_of_day_s[evening]) + end_min
            remaining[~evening] = end_min - minutes_of_day_s[~evening]
        else:
            remaining = pd.Series(end_min - minutes_of_day, index=df.index).astype(float)
        out[remaining_col] = remaining.where(in_session)

        out[f"session_in_session_{suffix}"] = in_session
        out[f"session_date_{suffix}"] = session_date
        return out
