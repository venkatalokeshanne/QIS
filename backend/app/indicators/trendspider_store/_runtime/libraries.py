"""
The whitelisted npm libraries TrendSpider scripts load via library(name),
re-implemented for the subset the store scripts use:
moment-timezone, binary-search-bounds, tinycolor2 and jStat.

moment() without an explicit zone uses the *local* zone, which on
TrendSpider is the viewer's browser zone. The runtime pins it to
America/New_York (LOCAL_TZ) -- the oracle runs Node with TZ set to the
same zone -- so results are deterministic.
"""

from __future__ import annotations

import calendar
import datetime as _dt
import math
import re
from zoneinfo import ZoneInfo

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.js import JSArray, JSObject, undefined

LOCAL_TZ = "America/New_York"

# ----------------------------------------------------------------------------
# binary-search-bounds
# ----------------------------------------------------------------------------


def _bsb(kind):
    def search(arr, y, cmp=undefined, lo=undefined, hi=undefined, *_):
        if not callable(cmp):
            cmp, lo, hi = undefined, cmp, lo
        l = 0 if lo is undefined else J.to_int32(lo)
        h = len(arr) - 1 if hi is undefined else J.to_int32(hi)

        def c(v):
            return J.to_number(cmp(v, y)) if cmp is not undefined else J.sub(v, y)

        if kind == "ge" or kind == "gt":
            i = h + 1
            while l <= h:
                m = (l + h) >> 1
                r = c(J.get(arr, m))
                if (r >= 0) if kind == "ge" else (r > 0):
                    i, h = m, m - 1
                else:
                    l = m + 1
            return i
        if kind == "lt" or kind == "le":
            i = l - 1
            while l <= h:
                m = (l + h) >> 1
                r = c(J.get(arr, m))
                if (r < 0) if kind == "lt" else (r <= 0):
                    i, l = m, m + 1
                else:
                    h = m - 1
            return i
        while l <= h:
            m = (l + h) >> 1
            r = c(J.get(arr, m))
            if r == 0:
                return m
            if r <= 0:
                l = m + 1
            else:
                h = m - 1
        return -1

    return search


BSB = {k: _bsb(k) for k in ("ge", "gt", "lt", "le", "eq")}

# ----------------------------------------------------------------------------
# moment / moment-timezone
# ----------------------------------------------------------------------------

_UNITS = {
    "y": "year", "year": "year", "years": "year",
    "Q": "quarter", "quarter": "quarter", "quarters": "quarter",
    "M": "month", "month": "month", "months": "month",
    "w": "week", "week": "week", "weeks": "week",
    "isoWeek": "isoWeek", "isoWeeks": "isoWeek", "W": "isoWeek",
    "d": "day", "day": "day", "days": "day",
    "date": "date", "dates": "date", "D": "date",
    "h": "hour", "hour": "hour", "hours": "hour",
    "m": "minute", "minute": "minute", "minutes": "minute",
    "s": "second", "second": "second", "seconds": "second",
    "ms": "millisecond", "millisecond": "millisecond", "milliseconds": "millisecond",
}

_FMT_TOKENS = re.compile(r"\[[^\]]*\]|YYYY|YY|MMMM|MMM|MM|M|Do|DD|D|dddd|ddd|dd|d|HH|H|hh|h|mm|m|ss|s|SSS|A|a|ZZ|Z|X|x|Q|E|W{1,2}|w{1,2}")
_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


class Moment(J.Moment):
    """Immutable-ish moment: mutators modify in place and return self, like moment.js."""

    def __init__(self, ms, tz=LOCAL_TZ, valid=True):
        self.ms = ms
        self.tz_name = tz
        self.valid = valid and ms == ms

    # -- construction --------------------------------------------------------
    @classmethod
    def make(cls, v=undefined, fmt=undefined, tz=LOCAL_TZ):
        if v is undefined:
            return cls(J.Date["now"](), tz)
        if isinstance(v, Moment):
            return cls(v.ms, tz)
        if isinstance(v, J.JSDate):
            return cls(v.ms, tz)
        if J.is_number(v):
            return cls(v, tz)
        if isinstance(v, str):
            return cls._parse(v, fmt, tz)
        if v is None:
            return cls(math.nan, tz, valid=False)
        return cls(math.nan, tz, valid=False)

    @classmethod
    def _parse(cls, s, fmt, tz):
        z = ZoneInfo(tz)
        if fmt is not undefined and isinstance(fmt, str):
            pyfmt = (fmt.replace("YYYY", "%Y").replace("YY", "%y").replace("MM", "%m").replace("DD", "%d")
                     .replace("HH", "%H").replace("mm", "%M").replace("ss", "%S"))
            try:
                d = _dt.datetime.strptime(s, pyfmt).replace(tzinfo=z)
                return cls(int(d.timestamp() * 1000), tz)
            except ValueError:
                return cls(math.nan, tz, valid=False)
        try:
            d = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return cls(math.nan, tz, valid=False)
        if d.tzinfo is None:
            d = d.replace(tzinfo=z)
        return cls(int(d.timestamp() * 1000), tz)

    @classmethod
    def tz(cls, v=undefined, a=undefined, b=undefined, *_):
        # moment.tz(value, zone) or moment.tz(value, format, zone)
        if b is not undefined:
            return cls.make(v, a, tz=b) if isinstance(v, str) else cls.make(v, tz=b)
        zone = a if isinstance(a, str) else LOCAL_TZ
        if isinstance(v, str):
            return cls._parse(v, undefined, zone)
        return cls.make(v, tz=zone)

    # -- helpers -------------------------------------------------------------------
    def _dt(self):
        return _dt.datetime.fromtimestamp(self.ms / 1000, ZoneInfo(self.tz_name))

    def _set_dt(self, d):
        self.ms = int(round(d.timestamp() * 1000))
        return self

    def value_of(self):
        return self.ms if self.valid else math.nan

    def _getset(self, field):
        def f(v=undefined, *_):
            d = self._dt()
            if v is undefined:
                return {
                    "year": d.year, "month": d.month - 1, "date": d.day, "hour": d.hour, "minute": d.minute,
                    "second": d.second, "millisecond": int(self.ms % 1000), "day": (d.weekday() + 1) % 7,
                    "isoWeekday": d.isoweekday(), "dayOfYear": d.timetuple().tm_yday, "isoWeek": d.isocalendar()[1],
                    "week": int(d.strftime("%U")) + (1 if _dt.date(d.year, 1, 1).weekday() != 6 else 0),
                    "quarter": (d.month - 1) // 3 + 1,
                }[field]
            v = int(J.to_number(v))
            if field == "year":
                d = d.replace(year=v)
            elif field == "month":
                return self.add(v - (d.month - 1), "months")
            elif field == "date":
                return self.add(v - d.day, "days")
            elif field == "day":
                return self.add(v - (d.weekday() + 1) % 7, "days")
            elif field == "isoWeekday":
                return self.add(v - d.isoweekday(), "days")
            elif field in ("hour", "minute", "second"):
                d = d.replace(**{field: 0}) + _dt.timedelta(**{field + "s": v})
                d = _dt.datetime.fromtimestamp(d.timestamp(), ZoneInfo(self.tz_name))
            elif field == "millisecond":
                self.ms = self.ms - (self.ms % 1000) + v
                return self
            return self._set_dt(d)

        return f

    def add(self, amount=undefined, unit="ms", sign=1):
        if isinstance(amount, dict):
            for k, v in amount.items():
                self.add(v, k, sign)
            return self
        amount = J.to_number(amount) * sign
        u = _UNITS.get(J.to_str(unit), "millisecond")
        d = self._dt()
        if u in ("year", "quarter", "month"):
            months = amount * (12 if u == "year" else 3 if u == "quarter" else 1)
            months = int(months)
            y, m = divmod(d.month - 1 + months, 12)
            y += d.year
            day = min(d.day, calendar.monthrange(y, m + 1)[1])
            nd = d.replace(year=y, month=m + 1, day=day)
            return self._set_dt(_dt.datetime.combine(nd.date(), nd.time(), ZoneInfo(self.tz_name)))
        if u in ("week", "isoWeek", "day", "date"):
            days = amount * (7 if u in ("week", "isoWeek") else 1)
            nd = (d.replace(tzinfo=None) + _dt.timedelta(days=days))
            return self._set_dt(nd.replace(tzinfo=ZoneInfo(self.tz_name)))
        mult = {"hour": 3600000, "minute": 60000, "second": 1000, "millisecond": 1}[u]
        self.ms += amount * mult
        return self

    def subtract(self, amount=undefined, unit="ms", *_):
        return self.add(amount, unit, -1)

    def start_of(self, unit=undefined, *_):
        u = _UNITS.get(J.to_str(unit))
        d = self._dt().replace(tzinfo=None)
        if u == "year":
            d = d.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif u == "quarter":
            d = d.replace(month=(d.month - 1) // 3 * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif u == "month":
            d = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif u == "week":
            d = (d - _dt.timedelta(days=(d.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif u == "isoWeek":
            d = (d - _dt.timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif u in ("day", "date"):
            d = d.replace(hour=0, minute=0, second=0, microsecond=0)
        elif u == "hour":
            d = d.replace(minute=0, second=0, microsecond=0)
        elif u == "minute":
            d = d.replace(second=0, microsecond=0)
        elif u == "second":
            d = d.replace(microsecond=0)
        return self._set_dt(d.replace(tzinfo=ZoneInfo(self.tz_name)))

    def end_of(self, unit=undefined, *_):
        self.start_of(unit)
        self.add(1, {"year": "years", "quarter": "quarters", "month": "months", "week": "weeks", "isoWeek": "weeks",
                     "day": "days", "date": "days"}.get(_UNITS.get(J.to_str(unit)), J.to_str(unit)))
        self.ms -= 1
        return self

    def format(self, fmt=undefined, *_):
        if not self.valid:
            return "Invalid date"
        if fmt is undefined:
            fmt = "YYYY-MM-DDTHH:mm:ssZ"
        d = self._dt()
        off = d.utcoffset().total_seconds() / 60
        sign = "+" if off >= 0 else "-"
        oh, om = divmod(int(abs(off)), 60)

        def tok(m):
            t = m.group(0)
            if t.startswith("["):
                return t[1:-1]
            h12 = d.hour % 12 or 12
            return {
                "YYYY": f"{d.year:04d}", "YY": f"{d.year % 100:02d}", "MMMM": _MONTHS[d.month - 1],
                "MMM": _MONTHS[d.month - 1][:3], "MM": f"{d.month:02d}", "M": str(d.month), "Do": _ordinal(d.day),
                "DD": f"{d.day:02d}", "D": str(d.day), "dddd": _DAYS[(d.weekday() + 1) % 7],
                "ddd": _DAYS[(d.weekday() + 1) % 7][:3], "dd": _DAYS[(d.weekday() + 1) % 7][:2],
                "d": str((d.weekday() + 1) % 7), "HH": f"{d.hour:02d}", "H": str(d.hour), "hh": f"{h12:02d}",
                "h": str(h12), "mm": f"{d.minute:02d}", "m": str(d.minute), "ss": f"{d.second:02d}", "s": str(d.second),
                "SSS": f"{int(self.ms % 1000):03d}", "A": "AM" if d.hour < 12 else "PM", "a": "am" if d.hour < 12 else "pm",
                "Z": f"{sign}{oh:02d}:{om:02d}", "ZZ": f"{sign}{oh:02d}{om:02d}", "X": str(int(self.ms // 1000)),
                "x": str(int(self.ms)), "Q": str((d.month - 1) // 3 + 1), "E": str(d.isoweekday()),
                "W": str(d.isocalendar()[1]), "WW": f"{d.isocalendar()[1]:02d}",
                "w": str(self._getset("week")()), "ww": f"{self._getset('week')():02d}",
            }[t]

        return _FMT_TOKENS.sub(tok, fmt)

    def diff(self, other=undefined, unit="ms", precise=False, *_):
        o = other if isinstance(other, Moment) else Moment.make(other)
        u = _UNITS.get(J.to_str(unit), "millisecond")
        delta = self.ms - o.ms
        if u in ("year", "quarter", "month"):
            a, b = self._dt(), o._dt()
            months = (a.year - b.year) * 12 + (a.month - b.month)
            anchor = Moment(o.ms, o.tz_name).add(months, "months")
            if (delta > 0 and anchor.ms > self.ms) or (delta < 0 and anchor.ms < self.ms):
                months -= 1 if delta > 0 else -1
            val = months / (12 if u == "year" else 3 if u == "quarter" else 1)
            return val if J.truthy(precise) else math.trunc(val)
        div = {"week": 604800000, "isoWeek": 604800000, "day": 86400000, "date": 86400000, "hour": 3600000,
               "minute": 60000, "second": 1000, "millisecond": 1}[u]
        val = delta / div
        return val if J.truthy(precise) else math.trunc(val)

    def js_get(self, k):
        simple = {
            "valueOf": lambda *_: self.value_of(), "unix": lambda *_: math.floor(self.ms / 1000),
            "format": self.format, "startOf": self.start_of, "endOf": self.end_of, "add": self.add,
            "subtract": self.subtract, "clone": lambda *_: Moment(self.ms, self.tz_name, self.valid),
            "tz": self._tz, "utc": lambda *_: self._tz("UTC"), "local": lambda *_: self._tz(LOCAL_TZ),
            "isValid": lambda *_: self.valid, "diff": self.diff,
            "toDate": lambda *_: J.JSDate(self.ms), "toISOString": lambda *_: J.JSDate(self.ms).to_iso(),
            "isBefore": lambda o=undefined, *_: self.ms < Moment.make(o).ms,
            "isAfter": lambda o=undefined, *_: self.ms > Moment.make(o).ms,
            "isSame": lambda o=undefined, *_: self.ms == Moment.make(o).ms,
            "isSameOrAfter": lambda o=undefined, *_: self.ms >= Moment.make(o).ms,
            "isSameOrBefore": lambda o=undefined, *_: self.ms <= Moment.make(o).ms,
            "isBetween": lambda a=undefined, b=undefined, *_: Moment.make(a).ms < self.ms < Moment.make(b).ms,
            "utcOffset": lambda *_: int(self._dt().utcoffset().total_seconds() // 60),
            "set": self._set, "get": lambda u=undefined, *_: self._getset(_UNITS.get(J.to_str(u), "millisecond"))(),
        }
        if k in simple:
            return simple[k]
        aliases = {
            "year": "year", "years": "year", "month": "month", "months": "month", "date": "date", "dates": "date",
            "day": "day", "days": "day", "hour": "hour", "hours": "hour", "minute": "minute", "minutes": "minute",
            "second": "second", "seconds": "second", "millisecond": "millisecond", "milliseconds": "millisecond",
            "isoWeekday": "isoWeekday", "dayOfYear": "dayOfYear", "isoWeek": "isoWeek", "isoWeeks": "isoWeek",
            "week": "week", "weeks": "week", "quarter": "quarter", "quarters": "quarter", "weekday": "day",
        }
        if k in aliases:
            return self._getset(aliases[k])
        return undefined

    def _tz(self, zone=undefined, *_):
        if zone is undefined:
            return self.tz_name
        self.tz_name = J.to_str(zone)
        return self

    def _set(self, what=undefined, val=undefined, *_):
        if isinstance(what, dict):
            for k, v in what.items():
                self._getset(_UNITS.get(k, k))(v)
            return self
        return self._getset(_UNITS.get(J.to_str(what), J.to_str(what)))(val)


def duration_breakdown(ms):
    def r2(x):
        return J.to_number(J.n_toFixed(x, 2))

    days = ms / 86400000
    months = days * 4800 / 146097 / 1  # moment's daysToMonths
    return JSObject(seconds=r2(ms / 1000), minutes=r2(ms / 60000), hours=r2(ms / 3600000), days=r2(days),
                    weeks=r2(days / 7), months=r2(days * 4800 / 146097), years=r2(days * 400 / 146097))


def _moment_fn():
    f = J._Callable(lambda v=undefined, fmt=undefined, *_: Moment.make(v, fmt))
    f["tz"] = lambda *a: Moment.tz(*a)
    f["unix"] = lambda s=undefined, *_: Moment.make(J.mul(s, 1000))
    f["utc"] = lambda v=undefined, *_: Moment.make(v, tz="UTC")
    f["duration"] = lambda v=undefined, *_: JSObject(asMinutes=lambda *_: J.to_number(v) / 60000)
    return f


# ----------------------------------------------------------------------------
# tinycolor2 (setAlpha / toRgbString / toHexString subset)
# ----------------------------------------------------------------------------

_NAMED = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0), "green": (0, 128, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "orange": (255, 165, 0), "purple": (128, 0, 128), "gray": (128, 128, 128),
    "grey": (128, 128, 128), "teal": (0, 128, 128), "maroon": (128, 0, 0), "fuchsia": (255, 0, 255),
    "lime": (0, 255, 0), "cyan": (0, 255, 255), "aqua": (0, 255, 255), "magenta": (255, 0, 255),
    "navy": (0, 0, 128), "olive": (128, 128, 0), "silver": (192, 192, 192), "pink": (255, 192, 203),
    "brown": (165, 42, 42), "gold": (255, 215, 0), "darkgreen": (0, 100, 0), "darkred": (139, 0, 0),
    "lightgray": (211, 211, 211), "lightgrey": (211, 211, 211), "darkgray": (169, 169, 169),
}


class TinyColor:
    def __init__(self, v):
        self.r = self.g = self.b = 0
        self.a = 1.0
        self.ok = True
        s = J.to_str(v).strip().lower() if not isinstance(v, TinyColor) else None
        if isinstance(v, TinyColor):
            self.r, self.g, self.b, self.a = v.r, v.g, v.b, v.a
        elif s in _NAMED:
            self.r, self.g, self.b = _NAMED[s]
        elif s.startswith("#") and len(s) in (4, 5, 7, 9):
            h = s[1:]
            if len(h) in (3, 4):
                h = "".join(c * 2 for c in h)
            self.r, self.g, self.b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            if len(h) == 8:
                self.a = round(int(h[6:8], 16) / 255, 2)
        else:
            m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+))?\s*\)", s)
            if m:
                self.r, self.g, self.b = (float(m.group(i)) for i in (1, 2, 3))
                if m.group(4):
                    self.a = float(m.group(4))
            else:
                self.ok = False

    def js_get(self, k):
        def set_alpha(v=undefined, *_):
            x = J.to_number(v)
            self.a = 1.0 if (x != x or x < 0 or x > 1) else x
            return self

        def rgb_string(*_):
            r, g, b = (int(J.js_round(c)) for c in (self.r, self.g, self.b))
            if self.a == 1:
                return f"rgb({r}, {g}, {b})"
            a = J.js_round(self.a * 100) / 100
            return f"rgba({r}, {g}, {b}, {J.to_str(a)})"

        def hex_string(*_):
            return "#%02x%02x%02x" % tuple(int(J.js_round(c)) for c in (self.r, self.g, self.b))

        return {
            "setAlpha": set_alpha, "toRgbString": rgb_string, "toHexString": hex_string, "toString": rgb_string,
            "getAlpha": lambda *_: self.a, "isValid": lambda *_: self.ok,
        }.get(k, undefined)


# ----------------------------------------------------------------------------
# jStat (vector statistics subset)
# ----------------------------------------------------------------------------


def _nums(a):
    return [J.to_number(x) for x in J.iter_of(a)]


def _percentile(arr=undefined, k=undefined, exclusive=False, *_):
    # jStat.percentile, verbatim semantics (index arithmetic can land on
    # undefined, which JS turns into NaN)
    a = JSArray(sorted(_nums(arr)))
    n = len(a)
    ex = J.truthy(exclusive)
    real = J.add(J.mul(k, n + (1 if ex else -1)), 0 if ex else 1)
    index = J.parseInt(real)
    frac = J.sub(real, index)
    if J.lt(J.add(index, 1), n):
        lo = J.get(a, J.sub(index, 1))
        return J.add(lo, J.mul(frac, J.sub(J.get(a, index), lo)))
    return J.get(a, J.sub(index, 1))


def _median(arr=undefined, *_):
    a = sorted(_nums(arr))
    n = len(a)
    return (a[n // 2 - 1] + a[n // 2]) / 2 if n % 2 == 0 else a[n // 2]


JSTAT = JSObject(
    max=lambda arr=undefined, *_: J._max(*_nums(arr)),
    min=lambda arr=undefined, *_: J._min(*_nums(arr)),
    mean=lambda arr=undefined, *_: J.div(sum(_nums(arr)), len(_nums(arr))),
    median=_median,
    percentile=_percentile,
    sum=lambda arr=undefined, *_: sum(_nums(arr)),
)


def get_library(name=undefined):
    base = J.to_str(name).split("@")[0]
    if base == "moment-timezone":
        return _moment_fn()
    if base == "binary-search-bounds":
        return JSObject(BSB)
    if base == "tinycolor2":
        return J._Callable(lambda v=undefined, *_: TinyColor(v))
    if base == "jstat":
        return JSTAT
    raise J.Unsupported(f'library("{J.to_str(name)}") is not ported')
