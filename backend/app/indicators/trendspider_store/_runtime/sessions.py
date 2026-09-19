"""
Session/bar identification -- port of TrendSpider's Resolution.barAt().

bar_at(resolution, session, ms) returns the start (epoch ms) of the bar
of `resolution` that contains `ms` under `session`, or None when the time
falls outside the session / on a non-market day -- exactly the engine's
rules, including its quirks (the daily bar only covers session hours; the
intraday bar grid is anchored at the session start).
"""

from __future__ import annotations

import datetime as _dt
import math
from zoneinfo import ZoneInfo

from app.indicators.trendspider_store._runtime import js as J

DAY_MS = 86400000
_TABLE = {"D": 1440, "W": 10080, "M": 43200, "Q": 129600, "Y": 525600}


def _local(ms, tz):
    return _dt.datetime.fromtimestamp(ms / 1000, ZoneInfo(tz))


def _ms(d):
    return int(round(d.timestamp() * 1000))


def _at(d, hours, minutes):
    """moment.set({hours, minutes, seconds: 0, ms: 0}) in d's zone."""
    naive = d.replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    naive = naive + _dt.timedelta(hours=hours, minutes=minutes)
    return naive.replace(tzinfo=d.tzinfo)


def _js_day(d):
    return (d.weekday() + 1) % 7  # moment.day(): Sunday = 0


def bar_at(resolution, session, ms, precise_overnight=False, greedy_daily=False):
    text = J.to_str(resolution)
    tz = J.get(session, "timezone")
    start, end = J.get(session, "start"), J.get(session, "end")
    sh, sm = int(J.get(start, "hours")), int(J.get(start, "minutes"))
    eh, em = int(J.get(end, "hours")), int(J.get(end, "minutes"))
    market_days = [int(x) for x in J.iter_of(J.get(session, "marketDays"))]
    overnight = J.truthy(J.get(session, "overnight"))
    length = J.to_number(J.get(session, "lengthMinutes"))
    daily = text == "D" or text == "1440"
    intraday = not J.isNaN(text) and not daily
    if not (intraday or daily or text in ("W", "M", "Q", "Y")):
        raise J.JSError(J.make_error(f"Invalid resolution: {text}"))
    is_md = lambda day: day in market_days  # noqa: E731

    r = _local(ms, tz)
    if daily:
        a = _at(r, sh, sm)
        i = _at(a, eh, em)
        u = _at(a, 0, 0)
        d = a
        p = 60 * sh + sm
        if overnight:
            n = (ms - _ms(u)) / 60000 >= p
            if precise_overnight:
                t_next = is_md(_js_day(d + _dt.timedelta(days=1)))
                t_cur = is_md(_js_day(d))
                if ms >= _ms(i) and not t_next:
                    return None
                if n and t_next:
                    return _ms(a)
                if not n and t_cur:
                    return _ms(a - _dt.timedelta(days=1))
            elif n:
                d = d + _dt.timedelta(days=1)
                u = u + _dt.timedelta(days=1)
            return _ms(_at(u, sh, sm)) if is_md(_js_day(d)) else None
        if not is_md(_js_day(d)):
            return None
        if (_ms(r) < _ms(a) and not greedy_daily) or (_ms(r) >= _ms(i) and not greedy_daily):
            return None
        return _ms(a)

    if intraday:
        bar_ms = 60000 * J.to_number(text)
        o = _at(r, 0, 0)
        c = o
        t = _at(o, sh, sm)
        n_ms = _ms(t)
        if not overnight and (ms - n_ms) / 60000 >= length:
            return None
        if overnight and ms < n_ms:
            t = t - _dt.timedelta(days=1)
        t_ms = _ms(t)
        k = math.floor((ms - t_ms) / bar_ms)
        if k < 0:
            return None
        s = t_ms + k * bar_ms
        if overnight:
            u_ms = _ms(o)
            r0 = (n_ms - u_ms) / 60000
            i0 = (s - u_ms) / 60000
            if (ms - t_ms) / 60000 >= length:
                return None
            if i0 >= r0:
                c = c + _dt.timedelta(days=1)
        return s if is_md(_js_day(c)) else None

    if text == "W":
        if overnight:
            e = _at(r - _dt.timedelta(days=_js_day(r)), sh, sm)
            if r < e:
                e = e - _dt.timedelta(weeks=1)
            return _ms(e)
        return _ms(_at(r - _dt.timedelta(days=r.weekday()), sh, sm))
    if text == "M":
        t = _at(r.replace(day=1), sh, sm)
    elif text == "Q":
        t = _at(r.replace(month=(r.month - 1) // 3 * 3 + 1, day=1), sh, sm)
    else:
        t = _at(r.replace(month=1, day=1), sh, sm)
    if overnight:
        t = t - _dt.timedelta(days=1)
    return _ms(t)
