"""
NYSE trading calendar and session boundaries, in America/New_York.

Rules-based (no third-party calendar dependency) and covered by tests
against published NYSE holiday/early-close dates. All boundaries follow
America/New_York wall-clock time, so daylight-saving changes are handled
by zoneinfo -- never by a fixed UTC offset.

Sessions (configurable via thresholds.SESSION_CONFIG):
    PREMARKET    04:00 - open (09:30)
    RTH          09:30 - close (16:00, or 13:00 on early-close days)
    AFTER_HOURS  close - 20:00 (17:00 on early-close days)
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from functools import lru_cache
from zoneinfo import ZoneInfo

from app.strategy_engine.thresholds import SESSION_CONFIG

NY = ZoneInfo("America/New_York")

# One-off closures that no recurring rule produces.
SPECIAL_CLOSURES = {
    dt.date(2001, 9, 11), dt.date(2001, 9, 12), dt.date(2001, 9, 13), dt.date(2001, 9, 14),
    dt.date(2004, 6, 11),   # President Reagan's funeral
    dt.date(2007, 1, 2),    # President Ford's funeral
    dt.date(2012, 10, 29), dt.date(2012, 10, 30),  # Hurricane Sandy
    dt.date(2018, 12, 5),   # President G.H.W. Bush's funeral
    dt.date(2025, 1, 9),    # President Carter's funeral
}


def _easter(year: int) -> dt.date:
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month, day = divmod(h + l_ - 7 * m + 114, 31)
    return dt.date(year, month, day + 1)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> dt.date:
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_weekday(year: int, month: int, weekday: int) -> dt.date:
    nxt = dt.date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d: dt.date) -> dt.date:
    """Saturday holiday -> Friday; Sunday holiday -> Monday."""
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


@lru_cache(maxsize=64)
def holidays(year: int) -> frozenset[dt.date]:
    out = set()
    new_year = dt.date(year, 1, 1)
    if new_year.weekday() == 6:
        out.add(dt.date(year, 1, 2))
    elif new_year.weekday() != 5:          # NYSE does not observe a Saturday New Year on Dec 31
        out.add(new_year)
    out.add(_nth_weekday(year, 1, 0, 3))   # Martin Luther King Jr. Day
    out.add(_nth_weekday(year, 2, 0, 3))   # Washington's Birthday
    out.add(_easter(year) - dt.timedelta(days=2))  # Good Friday
    out.add(_last_weekday(year, 5, 0))     # Memorial Day
    if year >= 2022:
        out.add(_observed(dt.date(year, 6, 19)))   # Juneteenth
    out.add(_observed(dt.date(year, 7, 4)))        # Independence Day
    out.add(_nth_weekday(year, 9, 0, 1))   # Labor Day
    out.add(_nth_weekday(year, 11, 3, 4))  # Thanksgiving
    out.add(_observed(dt.date(year, 12, 25)))      # Christmas
    out |= {d for d in SPECIAL_CLOSURES if d.year == year}
    return frozenset(out)


def is_trading_day(d: dt.date) -> bool:
    return d.weekday() < 5 and d not in holidays(d.year)


def is_early_close(d: dt.date) -> bool:
    if not is_trading_day(d):
        return False
    if d.month == 7 and d.day == 3:
        return True                                   # day before Independence Day
    if d.month == 11 and d == _nth_weekday(d.year, 11, 3, 4) + dt.timedelta(days=1):
        return True                                   # day after Thanksgiving
    if d.month == 12 and d.day == 24:
        return True                                   # Christmas Eve
    return False


@dataclass(frozen=True)
class SessionBounds:
    """One trading day's session boundaries as tz-aware New York datetimes."""

    date: dt.date
    premarket_start: dt.datetime
    open: dt.datetime
    close: dt.datetime
    after_hours_end: dt.datetime
    early_close: bool


def _at(d: dt.date, hhmm: str) -> dt.datetime:
    h, m = (int(x) for x in hhmm.split(":"))
    return dt.datetime(d.year, d.month, d.day, h, m, tzinfo=NY)


def session_bounds(d: dt.date) -> SessionBounds | None:
    """None when the market is closed that day."""
    if not is_trading_day(d):
        return None
    early = is_early_close(d)
    cfg = SESSION_CONFIG
    return SessionBounds(
        date=d,
        premarket_start=_at(d, cfg["premarket_start"]),
        open=_at(d, cfg["rth_open"]),
        close=_at(d, cfg["early_close"] if early else cfg["rth_close"]),
        after_hours_end=_at(d, cfg["early_after_hours_end"] if early else cfg["after_hours_end"]),
        early_close=early,
    )


def trading_days(start: dt.date, end: dt.date) -> list[dt.date]:
    out, d = [], start
    while d <= end:
        if is_trading_day(d):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def previous_trading_day(d: dt.date) -> dt.date:
    d -= dt.timedelta(days=1)
    while not is_trading_day(d):
        d -= dt.timedelta(days=1)
    return d
