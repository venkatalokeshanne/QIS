"""
TrendSpider's script-level built-ins (engine module "builtinFunctions").

TrendSpider implements these in its own scripting API (they receive the
API object as `this`), so each port below calls the same API functions
in the same order as the engine does.
"""

from __future__ import annotations

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.js import JSArray, JSObject, undefined


def _assert(cond, msg):
    if not cond:
        raise J.JSError(J.make_error(msg))


def install(F, indicators):
    arr = lambda v: isinstance(v, list)  # noqa: E731

    def mfi(e=undefined, t=undefined, n=undefined, *_):
        _assert(arr(e), "'price' must be an array")
        _assert(arr(t), "'volume' must be an array")
        _assert(not J.isNaN(n) and J.gt(n, 1), "'length' must be a positive number")
        o, c = F["series_of"](0), F["series_of"](0)
        for k in range(1, len(e)):
            if J.gt(e[k], e[k - 1]):
                J.set(o, k, J.mul(e[k], J.get(t, k)))
            if J.lt(e[k], e[k - 1]):
                J.set(c, k, J.mul(J.neg(e[k]), J.get(t, k)))
        return J.a_map(F["div"](F["sum"](o, n), F["sum"](c, n)), lambda v, *_: J.sub(100, J.div(100, J.sub(1, v))))

    def stochastic_rsi(e=undefined, t=undefined, n=undefined, *_):
        _assert(not J.isNaN(t) and J.gt(t, 1), "'length' must be a positive number")
        _assert(not J.isNaN(n) and J.gt(n, 1), "'smooth' must be a positive number")
        _assert(arr(e), "'price' must be an array")
        o = F["rsi"](e, t)
        return F["sma"](F["stochastic"](o, o, o, t), n)

    def supertrend(e=14, t=3, n=True, *_):
        e = 14 if e is undefined else e
        t = 3 if t is undefined else t
        n = True if n is undefined else n
        _assert(not J.isNaN(e) or J.gt(e, 1), "length must be a positive number")
        _assert(not J.isNaN(t) or J.gt(t, 1), "multiplier must be a positive number")
        _assert(isinstance(n, bool), "useWicks must be a boolean")
        s, o, c = F["close"], F["high"], F["low"]
        out = F["series_of"](None)
        u = F["atr"](e)
        d = p = 0
        h = 1
        r = e
        while J.lt(r, len(s)):
            mid = J.div(J.add(J.get(o, r), J.get(c, r)), 2)
            lo = J.sub(mid, J.mul(t, J.get(u, r)))
            up = J.add(mid, J.mul(t, J.get(u, r)))
            i, M, f = lo, up, h
            m = b = J.get(s, r)
            _ = g = J.get(s, J.sub(r, 1))
            if J.truthy(n):
                _, g, m, b = J.get(c, J.sub(r, 1)), J.get(o, J.sub(r, 1)), J.get(c, r), J.get(o, r)
            if J.gt(_, d):
                i = J._max(lo, d)
            if J.lt(g, p):
                M = J._min(up, p)
            f = 1 if (h == -1 and J.gt(b, p)) else (-1 if (h == 1 and J.lt(m, d)) else h)
            J.set(out, r, i if f == 1 else M)
            p, d, h = M, i, f
            r = J.add(r, 1)
        return out

    def tema(e=undefined, t=14, *_):
        t = 14 if t is undefined else t
        s = F["ema"](e, t)
        o = F["ema"](s, t)
        c = F["ema"](o, t)
        return F["add"](F["mult"](s, 3), F["mult"](o, -3), c)

    def tsi(e=undefined, t=undefined, n=undefined, *_):
        _assert(arr(e), "'price' must be an array")
        _assert(not J.isNaN(t) and J.gt(t, 1), "'long' must be a positive number")
        _assert(not J.isNaN(n) and J.gt(n, 1), "'short' must be a positive number")
        c = lambda v: F["ema"](F["ema"](v, t), n)  # noqa: E731
        l = F["momentum"](e, 2)
        u = J.a_map(l, lambda v, *_: J.Math["abs"](v))
        return F["mult"](F["div"](c(l), c(u)), 100)

    def twap(e=undefined, t=undefined, n=undefined, *_):
        l = e if J.truthy(e) else F["close"]
        u = t if J.truthy(t) else F["time"]
        cur = F["current"]
        d = n if J.truthy(n) else cur["session"]
        _assert(arr(l), "'price' must be a series")
        _assert(arr(u), "'timeSeries' must be a series")
        _assert(isinstance(d, dict), "session must be an object")
        p = F["series_of"](None)
        h = 1
        M = J.get(l, 0)
        f = [J.get(F["bar_at"](x, cur["resolution"], d), "session") for x in u]
        m = 0
        for k in range(1, len(l)):
            if J.ne(f[k], f[k - 1]):
                h, M, m = 1, l[k], m + 1
            else:
                h += 1
                M = J.add(M, l[k])
            if m > 0:
                J.set(p, k, J.div(M, h))
        return p

    def will_r(*e):
        o, c, l, u = 14, F["high"], F["low"], F["close"]
        _assert(len(e) in (0, 1, 4), "the arguments must be 0 (default length), 1 (length) or 5 (open, high, low, close, length)")
        if len(e) == 1:
            o = e[0]
        elif len(e) == 4:
            c, l, u, o = e[0], e[1], e[2], e[3]
        return F["add"](F["stochastic"](u, c, l, o), -100)

    def bop(*e):
        _assert(len(e) in (1, 5), "the arguments must be 1 (length) or 5 (open, high, low, close, length)")
        d, p, h, M = F["open"], F["high"], F["low"], F["close"]
        if len(e) == 1:
            _assert(J.is_number(e[0]) and e[0] > 0, "'length' must be a positive number")
            u = e[0]
        else:
            d, p, h, M, u = e
        return F["sma"](F["div"](F["sub"](M, d), F["sub"](p, h)), u)

    def cci(e=undefined, t=undefined, *_):
        _assert(not J.isNaN(t) and J.gt(t, 1), "'length' must be a positive number")
        _assert(arr(e), "'price' must be an array")
        dev = J.a_map(F["absdev"](e, t), lambda v, *_: v if J.sne(0, v) else 1e-9)
        return F["mult"](F["div"](F["sub"](e, F["sma"](e, t)), dev), 66.66)

    def correlation(e=undefined, t=undefined, n=undefined, *_):
        _assert(arr(e), "'series1' must be an array")
        _assert(arr(t), "'series2' must be an array")
        _assert(not J.isNaN(n) and J.gt(n, 1), "'length' must be a positive number")
        l, u = F["variance"](e, n), F["variance"](t, n)
        d, p = F["sma"](e, n), F["sma"](t, n)
        den = J.a_map(F["mult"](l, u), lambda v, *_: J.Math["sqrt"](v))
        return F["div"](F["sub"](F["sma"](F["mult"](e, t), n), F["mult"](d, p)), den)

    def color_cloud(e=undefined, t=undefined, n=undefined, a=undefined, i="Up", s="Down", o=0.33, *_):
        i = "Up" if i is undefined else i
        s = "Down" if s is undefined else s
        o = 0.33 if o is undefined else o
        _assert(arr(e), "first argument must be a series")
        _assert(arr(t), "second argument must be a series")
        _assert(len(e) == len(t), "series length mismatch")
        _assert(isinstance(n, str), "color1 must be a string")
        _assert(isinstance(a, str), "color2 must be a string")
        _assert(isinstance(i, str), "name1 must be a string")
        _assert(isinstance(s, str), "name2 must be a string")
        _assert(not J.isNaN(o), "opacity must be a number")
        c, l, u, d = (F["series_of"](None) for _ in range(4))
        for k in range(1, len(e)):
            if e[k] is not None and t[k] is not None:
                if J.gt(e[k], t[k]):
                    if J.lt(e[k - 1], t[k - 1]):
                        c[k - 1], l[k - 1] = e[k - 1], t[k - 1]
                    c[k], l[k] = e[k], t[k]
                else:
                    if J.gt(e[k - 1], t[k - 1]):
                        u[k - 1], d[k - 1] = t[k - 1], e[k - 1]
                    u[k], d[k] = t[k], e[k]
        F["fill"](F["paint"](c, JSObject(hidden=True)), F["paint"](l, JSObject(hidden=True)), n, o, i)
        F["fill"](F["paint"](u, JSObject(hidden=True)), F["paint"](d, JSObject(hidden=True)), a, o, s)
        return undefined

    def compute_band(e=undefined, t="St.Dev.", n=1, a=2, i=undefined, *_):
        t = "St.Dev." if t is undefined else t
        n = 1 if n is undefined else n
        a = 2 if a is undefined else a
        _assert(arr(e), "first argument must be a series")
        _assert(isinstance(t, str), "bandType must be a string")
        _assert(not J.isNaN(n), "multiplier must be a number")
        _assert(not J.isNaN(a) and J.gt(a, 1), "length must be a number greater than 1")
        _assert(i is undefined or isinstance(i, dict), "params must be an object")
        s = undefined if i is undefined else J.get(i, "percentageBasis")
        _assert(s is undefined or arr(s), "percentageBasis must be a series")
        if t == "St.Dev.":
            _assert(J.ge(a, 2), "length must be greater than 2 for a St.Dev. band")
            M = F["stdev"](F["close"], a)
        elif t == "Constant":
            M = F["series_of"](1)
        elif t == "ATR":
            M = F["atr"](a)
        elif t == "Percentage":
            M = F["mult"](s if J.truthy(s) else e, 0.01)
        else:
            raise J.JSError(J.make_error("unknown_band_type"))
        return JSObject(upper=F["add"](e, F["mult"](M, n)), lower=F["sub"](e, F["mult"](M, n)))

    def adx(e=14, t="wildma", *_):
        e = 14 if e is undefined else e
        t = "wildma" if t is undefined else t
        p = indicators[t]
        a, i = F["high"], F["low"]
        h = F["for_every"](a, F["shift"](a, 1), lambda x, y, *_: J.sub(x, y))
        M = F["for_every"](i, F["shift"](i, 1), lambda x, y, *_: J.sub(y, x))
        f = F["atr"](1)
        f[0] = None
        m = p(f, e)
        b = p(F["for_every"](h, M, lambda x, y, *_: x if (J.gt(x, y) and J.gt(x, 0)) else 0), e)
        _ = p(F["for_every"](h, M, lambda x, y, *_: y if (J.lt(x, y) and J.gt(y, 0)) else 0), e)
        g = F["mult"](F["div"](b, m), 100)
        A = F["mult"](F["div"](_, m), 100)

        def dx(x, y, *_):
            s = J.add(x, y)
            r = J.Math["abs"](J.sub(x, y))
            return J.div(J.mul(100, J.Math["abs"](r)), s)

        return JSObject(adx=F["sma"](F["for_every"](g, A, dx), e), dmiPlus=g, dmiMinus=A)

    def zigzag_points(e=20, t=1, n=2, a=undefined, i=undefined, *_):
        e = 20 if e is undefined else e
        t = 1 if t is undefined else t
        n = 2 if n is undefined else n
        _assert(not J.isNaN(e) and J.ge(e, 1), "zigzag_points(): invalid depth")
        _assert(not J.isNaN(t) and J.ge(t, 0.001), "zigzag_points(): invalid deviation")
        _assert(not J.isNaN(n) and J.ge(n, 1), "zigzag_points(): invalid backstep")
        s = a if J.truthy(a) else F["high"]
        o = i if J.truthy(i) else F["low"]
        _assert(arr(s), "highValues must be a series")
        _assert(arr(o), "lowValues must be a series")
        L = len(s)
        low_ext, high_ext = [None] * L, [None] * L
        c = l = u = None
        depth, backstep = int(e), int(n)
        for k in range(depth, L):
            d = J.Math["max"](*[v for v in s[k - depth + 1 : k + 1] if v is not None])
            p = J.Math["min"](*[v for v in o[k - depth + 1 : k + 1] if v is not None])
            if J.eq(p, l):
                p = None
            elif J.lt(J.Math["abs"](J.div(J.mul(100, J.sub(c, p)), p)), t):
                p = None
            else:
                for m in range(k - backstep, k):
                    if low_ext[m] is not None and J.gt(low_ext[m], p):
                        low_ext[m] = None
            if J.eq(J.get(o, k), p):
                l, low_ext[k], u = p, p, k
            else:
                low_ext[k] = None
            p = d
            if J.eq(p, c):
                p = None
            elif J.lt(J.Math["abs"](J.div(J.mul(100, J.sub(p, l)), p)), t):
                p = None
            else:
                for m in range(k - backstep, k):
                    if high_ext[m] is not None and J.lt(high_ext[m], p):
                        high_ext[m] = None
            if J.eq(J.get(s, k), p):
                c, high_ext[k], u = p, p, k
            else:
                high_ext[k] = None
        M = u
        highs, lows = [], []
        if J.get(JSArray(low_ext), M) is not None:
            mode, f, m_ = "high", J.get(o, M), None
            lows.append(M)
        else:
            mode, m_, f = "low", J.get(s, M), None
            highs.append(M)
        for k in range((M if M is not None else 0) - 1, -1, -1):
            tl = low_ext[k] is not None
            th = high_ext[k] is not None
            if mode == "high":
                if tl and J.lt(low_ext[k], f) and not th:
                    f = low_ext[k]
                    lows[-1] = k
                if th and not tl:
                    m_ = s[k]
                    highs.append(k)
                    mode = "low"
            else:
                if th and J.gt(high_ext[k], m_) and not tl:
                    m_ = high_ext[k]
                    highs[-1] = k
                if tl and not th:
                    f = o[k]
                    lows.append(k)
                    mode = "high"
        return JSObject(highIndexes=JSArray(reversed(highs)), lowIndexes=JSArray(reversed(lows)))

    def pattern_finder(name):
        def f(*_):
            raise J.Unsupported(f"{name}() (chart-pattern recognition) is not ported")

        return f

    F.update(mfi=mfi, stochastic_rsi=stochastic_rsi, supertrend=supertrend, tsi=tsi, twap=twap, will_r=will_r, bop=bop,
             cci=cci, correlation=correlation, color_cloud=color_cloud, compute_band=compute_band,
             zigzag_points=zigzag_points)
    for name in ("find_trends", "find_triangle", "find_wedge", "find_broadening", "find_channel",
                 "find_double_peak_formation", "find_head_and_shoulders", "find_cup_and_handle"):
        F[name] = pattern_finder(name)
    indicators["tema"] = tema
    indicators["adx"] = adx
