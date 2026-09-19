"""
TrendSpider custom-scripting API, ported from TrendSpider's own engine.

Every function here reproduces the implementation TrendSpider's chart
runs (its custom-scripting web worker), including its unusual
conventions -- ema() seeds from the first window's last value rather than
an SMA, atr() starts its Wilder smoothing from 0, wildma() seeds from a
single value, stochastic() rounds to 3 decimals, a series operand that is
`null` stays `null` in add/sub/mult/div. Matching those conventions is
what makes the *_TS indicators produce TrendSpider's numbers; the
oracle harness (tools/ts_store/oracle) runs the original scripts through
TrendSpider's engine and requires identical output.

`build_api(ctx)` returns the global namespace a translated script sees.
"""

from __future__ import annotations

import datetime as _dt
import math
import re
from zoneinfo import ZoneInfo

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.js import JSArray, JSObject, undefined

MAX_OUT_SERIES = 70


def script_assert(cond, message=None):
    if not cond:
        raise J.JSError(J.make_error(message or "Assertion failed"))


def id_from_humanized(s):
    # JS /\W/g works on UTF-16 code units: a non-BMP character (emoji) is
    # two units and becomes two underscores.
    t = "".join(c if re.match(r"[A-Za-z0-9_]", c) else ("__" if ord(c) > 0xFFFF else "_") for c in s).lower()
    return "proto" if t == "__proto__" else t


def _is_arr(v):
    return isinstance(v, list)


def _py(v):
    """JS value -> plain Python (for handing arguments to a data provider)."""
    if isinstance(v, dict):
        return {k: _py(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_py(x) for x in v]
    if v is undefined:
        return None
    return v


OPTION_METRICS = "l,b,a,bs,as,oi,oic,dvol,iv,gd,gg,gv,gt,gr,chg,chgp".split(",")


def _valid_yymmdd(s):
    try:
        _dt.datetime.strptime(s, "%y%m%d")
        return True
    except ValueError:
        return False


def _nan(v):
    return J.isNaN(v)


def _series(v):
    return v if isinstance(v, JSArray) else JSArray(v)


# ----------------------------------------------------------------------------
# indicator math (engine module "calculateIndicator")
# ----------------------------------------------------------------------------


def _valid_point(v, allowed_strings=False):
    return (J.truthy(v) or (J.is_number(v) and v == 0)) and (allowed_strings or not J.isNaN(v))


def _first_valid(arr):
    for i, v in enumerate(arr):
        if _valid_point(v):
            return i
    return -1


class _CalcError(Exception):
    pass


def _talib_ok(result, dont_expect_all=False):
    keys = [k for k in result if not k.lower().startswith("cloud")]
    idxs = [_first_valid(result[k]) for k in keys]
    if dont_expect_all:
        pos = [i for i in idxs if i >= 0]
        a = min(pos) if pos else math.inf
    else:
        a = max(idxs) if idxs else -math.inf
    if a < 0:
        return {"error": {"error": "not_enough_candles"}}
    if a == math.inf:
        return {"data": {"result": {k: JSArray() for k in result}, "begIndex": a}}
    return {"data": {"result": {k: JSArray(v[a:]) for k, v in result.items()}, "begIndex": a}}


def _sliding(allow_nulls, fn, series, period):
    """Engine's slidingWindowFunction."""
    script_assert(not _nan(period) and J.ge(period, 1), "window size is invalid")
    a = _int_len(period)
    n = len(series)
    out = [None] * n
    prev = None
    any_ = False
    for r in range(a - 1, n):
        w = JSArray(series[r - (a - 1) : r + 1])
        if not allow_nulls and any(v is None or J.isNaN(v) for v in w):
            continue
        out[r] = fn(w, a, prev)
        prev = out[r]
        any_ = True
    if any_:
        return {"begIndex": a - 1, "result": {"outReal": JSArray(out[a - 1 :])}}
    return {"begIndex": n - 1, "isEmpty": True, "result": {"outReal": JSArray(out)}}


def _int_len(v):
    v = J.to_number(v)
    if v != v or v in (math.inf, -math.inf):
        raise J.Unsupported(f"non-finite window length {v}")
    if not float(v).is_integer():
        # JS would index arrays with fractional keys here; no store script
        # relies on that, so refuse rather than guess.
        raise J.Unsupported(f"fractional window length {v}")
    return int(v)


def _w_sum(w):
    s = 0
    for v in w:
        s = J.add(s, v)
    return s


def _ema_step(w, t, prev):
    r = 2 / (1 + t)
    if prev is None:
        if w[-1] is None:
            return None
        prev = w[-1]
    return J.add(J.mul(1 - r, prev), J.mul(w[-1], r))


def _stdev(w, t):
    n = J.div(_w_sum(w), t)
    return J.Math["sqrt"](J.div(_w_sum([J.pow_(J.sub(e, n), 2) for e in w]), t))


def _absdev(w, t):
    n = J.div(_w_sum(w), t)
    return J.div(_w_sum([J.Math["abs"](J.sub(e, n)) for e in w]), t)


def _variance(w, t):
    n = J.div(_w_sum(w), t)
    return J.div(_w_sum([J.pow_(J.sub(e, n), 2) for e in w]), t)


def _linreg(w, *_):
    t = n = r = a = 0
    for i, v in enumerate(w):
        t = t + i
        n = J.add(n, v)
        r = J.add(r, J.mul(i, v))
        a = a + i * i
    i = len(w)
    s = J.div(J.sub(J.mul(i, r), J.mul(t, n)), J.sub(i * a, t * t))
    return J.add(J.div(J.sub(n, J.mul(s, t)), i), J.mul(s, i - 1))


def _fractal_merge(fn, series, params):
    t = params["optInTimePeriod"]
    script_assert(not _nan(t) and J.gt(t, 1), "window size is invalid")
    a = _int_len(t)
    i = [None] * len(series)
    s = a - 1
    for o in range(s, len(series)):
        c = fn(JSArray(series[o - s : o + 1]), params)
        script_assert(len(c) == a, "internal error 43")
        l = i[o - s : o + 1]
        i[o - s : o + 1] = [(e if J.truthy(e) else c[k]) for k, e in enumerate(l)]
    return {"begIndex": a - 1, "result": {"outReal": JSArray(i[a - 1 :])}}


def _fractal(high, e, params):
    t = params["optInTimePeriod"]
    n = params.get("peakIndex", undefined)
    if J.nullish(n):
        script_assert(J.mod(t, 2) == 1, f"fractal_{'high' if high else 'low'}: length can not be even")
        script_assert(J.ge(t, 3), f"fractal_{'high' if high else 'low'}: length should be >= 3")
        n = (t - 1) / 2
    else:
        script_assert(J.ge(t, 2), f"fractal_{'high' if high else 'low'}: length should be >= 2")
        script_assert(J.gt(t, n), f"fractal_{'high' if high else 'low'}: peakIndex should be smaller than length")
    n = _int_len(n)
    a = J.get(e, n)
    for k in range(len(e)):
        ek = e[k]
        if high:
            hit = (k < n and J.le(e[n], ek)) or (k > n and J.lt(e[n], ek))
        else:
            hit = (k < n and J.ge(e[n], ek)) or (k > n and J.gt(e[n], ek))
        if hit:
            a = None
    t = _int_len(t)
    return JSArray([None] * n + [a] + [None] * (t - n - 1))


def _price_from_table(e, i, source=undefined):
    source = "close" if source is undefined else source
    g = lambda k: J.get(J.get(e, k), i)  # noqa: E731
    if source == "oc2":
        return J.div(J.add(g("open"), g("close")), 2)
    if source == "hl2":
        return J.div(J.add(g("high"), g("low")), 2)
    if source == "hlc3":
        return J.div(J.add(J.add(g("high"), g("low")), g("close")), 3)
    if source == "ohlc4":
        return J.div(J.add(J.add(J.add(g("open"), g("high")), g("low")), g("close")), 4)
    script_assert(J.truthy(J.get(e, source)), f'Illegal data source value "{source}"')
    return g(source)


# -- the table-based ("talib") indicators -------------------------------------


def _calc_wildma(e, t):
    length = t.get("length", undefined)
    script_assert(not _nan(length) and J.ge(length, 1), "'length' is invalid")
    close = e["close"]
    n = [_price_from_table(e, a, t.get("priceSource", undefined)) for a in range(len(close))]
    out = [None] * len(n)
    o = None
    start = J.sub(length, 1)
    k = int(math.ceil(start)) if not float(start).is_integer() else int(start)
    for i in range(max(k, 0), len(n)):
        r = n[i]
        if o is None:
            o = r
        a = None if r is None else J.add(o, J.div(J.sub(r, o), length))
        o = a
        out[i] = a
    return _talib_ok({"outReal": out}, dont_expect_all=True)


def _calc_vwma(e, t):
    vol = e.get("volume")
    if not vol or not any(J.truthy(v) for v in vol):
        return {"error": {"error": "First argument must contain 'volume' field"}}
    L = t.get("length", undefined)
    out = []
    Li = _int_len(L)
    for r in range(len(e["time"])):
        if r + 1 >= Li:
            a = _w_sum(vol[r - Li + 1 : r + 1])
            s = 0
            for i in range(r - Li + 1, r + 1):
                s = J.add(s, J.mul(_price_from_table(e, i, t.get("priceSource", undefined)), vol[i]))
            out.append(J.div(s, a) if J.truthy(a) else None)
        else:
            out.append(None)
    return _talib_ok({"outReal": out})


def _calc_alma(e, t):
    window, sigma, offs = t.get("window", undefined), t.get("sigma", undefined), t.get("offs", undefined)
    script_assert(not _nan(window) and J.gt(window, 1), "'length' is invalid")
    script_assert(not _nan(offs), "'smooth' is invalid")
    script_assert(not _nan(sigma), "'sigma' is invalid")
    W = _int_len(window)
    n = []
    exp_, pow_, floor_ = J.Math["exp"], J.Math["pow"], J.Math["floor"]
    for a in range(len(e["time"]) - W + 1, 0, -1):
        i = s = 0
        for k in range(W):
            o = exp_(J.div(J.mul(-1, pow_(J.sub(k, floor_(J.mul(offs, W - 1))), 2)), J.mul(2, pow_(J.div(W, sigma), 2))))
            i = J.add(i, o)
            s = J.add(s, J.mul(_price_from_table(e, a + k - 1, t.get("priceSource", undefined)), o))
        n.append(J.div(s, i))
    n.reverse()
    return _talib_ok({"ALMA": [None] * (W - 1) + n})


def _calc_vortex(e, t):
    i = t.get("optInTimePeriod", undefined)
    if not J.is_number(i):
        return {"error": {"error": "Period must be a number"}}
    if i % 1 != 0:
        return {"error": {"error": "Period must be an integer"}}
    if i > 250:
        return {"error": {"error": "Maximum period is 250"}}
    if i <= 0:
        return {"error": {"error": "Period must be greater than 0"}}
    c = len(e["time"])
    pos, neg = [None] * c, [None] * c
    d, p, h = [], [], []
    H, Lo, C = e["high"], e["low"], e["close"]
    for k in range(1, c):
        r, a, s = C[k - 1], H[k - 1], Lo[k - 1]
        o, cc = H[k], Lo[k]
        M = J.Math["max"](J.sub(o, cc), J.Math["abs"](J.sub(o, r)), J.Math["abs"](J.sub(cc, r)))
        h.append(M)
        d.append(J.Math["abs"](J.sub(o, s)))
        p.append(J.Math["abs"](J.sub(cc, a)))
        if len(d) == i:
            den = _w_sum(h)
            pos[k] = J.div(_w_sum(d), den)
            neg[k] = J.div(_w_sum(p), den)
            d.pop(0), p.pop(0), h.pop(0)
    return _talib_ok({"positive": pos, "negative": neg})


def _calc_kama(e, t):
    src = t.get("priceSource", undefined)
    ER, fast, slow = t.get("ERLength", undefined), t.get("fastPeriod", undefined), t.get("slowPeriod", undefined)
    i = [_price_from_table(e, a, src) for a in range(len(e["time"]))]
    s = J.div(2, J.add(fast, 1))
    o = J.div(2, J.add(slow, 1))
    ERi = _int_len(ER)
    out = []
    c = None
    for a in range(0, len(i) - ERi):
        l = ERi + a
        acc, last = 0, 0
        for r, v in enumerate(i[a : l + 1]):
            acc = J.add(acc, 0 if r == 0 else J.Math["abs"](J.sub(v, last)))
            last = v
        d = J.div(J.Math["abs"](J.sub(i[l], i[a])), acc)
        p = J.Math["pow"](J.add(J.mul(d, J.sub(s, o)), o), 2)
        h = _price_from_table(e, l, src)
        if c is None:
            c = _price_from_table(e, l - 1, src)
            out.append(c)
        M = J.add(c, J.mul(p, J.sub(h, c)))
        c = M
        out.append(M)
    return _talib_ok({"outReal": [None] * (ERi - 1) + out})


def _calc_psar(e, t):
    n = t.get("optInMaximum", undefined)
    a = J.Math["min"](t.get("optInAcceleration", undefined), n)
    st = t.get("optInStart", undefined)
    i = J.Math["min"](st if J.truthy(st) else a, n)
    ch, cl = t.get("customHigh", undefined), t.get("customLow", undefined)
    S = {"high": ch if J.truthy(ch) else e["high"], "low": cl if J.truthy(cl) else e["low"]}
    state = {"o": i, "c": 0, "l": False, "u": 0}

    def d(kind, k):
        f = J.Math["max"] if kind == "high" else J.Math["min"]
        v = f(state["u"], J.get(S[kind], k - 1))
        if k > 2:
            v = f(v, J.get(S[kind], k - 2))
        return v

    out = []
    for k in range(len(S["high"])):
        if k < 1:
            out.append(None)
            continue
        r = J.get(S["low"], k)
        p = J.get(S["high"], k)
        if k == 1:
            eh = J.get(S["high"], 0)
            nl = J.get(S["low"], 0)
            aa = J.Math["min"](J.get(S["low"], 0), r)
            ii = J.Math["max"](J.get(S["high"], 0), p)
            if J.lt(J.sub(p, eh), J.sub(nl, r)):
                state.update(l=True, c=aa, u=ii)
            else:
                state.update(l=False, c=ii, u=aa)
        o, c, l, u = state["o"], state["c"], state["l"], state["u"]
        u = J.add(u, J.mul(o, J.sub(c, u))) if l else J.sub(u, J.mul(o, J.sub(u, c)))
        state["u"] = u
        if l:
            u = d("high", k)
            state["u"] = u
            if J.lt(r, c):
                c = r
                o = J.Math["min"](J.add(o, a), n)
            if J.le(u, p):
                u, c, l, o = c, p, False, i
        else:
            u = d("low", k)
            state["u"] = u
            if J.gt(p, c):
                c = p
                o = J.Math["min"](J.add(o, a), n)
            if J.ge(u, r):
                u, c, l, o = c, r, True, i
        state.update(o=o, c=c, l=l, u=u)
        out.append(u)
    return _talib_ok({"outReal": out})


_TABLE_INDICATORS = {
    "wildma": _calc_wildma,
    "vwma": _calc_vwma,
    "alma": _calc_alma,
    "vortex": _calc_vortex,
    "kama": _calc_kama,
    "psar": _calc_psar,
}


# -- the series indicators -------------------------------------------------------


def _ind_sma(e, params):
    t = params.get("optInTimePeriod", undefined)
    script_assert(_is_arr(e), "sma(): first argument must be a series")
    is_arr = _is_arr(t)
    if is_arr:
        script_assert(len(t) == len(e), "sma(): the length array must have the same size with the source")
    else:
        script_assert(J.ge(t, 1), "sma(): invalid length")
    a = [None] * len(e)
    i = next((k for k, v in enumerate(e) if v is not None), -1)
    for r in range(i, len(e)) if i >= 0 else ():
        s = J.Math["ceil"](t[r]) if is_arr else t
        if J.lt(J.add(J.sub(r, s), 1), i):
            a[r] = None
        else:
            lo = J.add(J.sub(r, s), 1)
            w = J.get(e, "slice")(lo, r + 1)
            a[r] = J.div(_w_sum(w), s)
    return JSArray(a)


def _ind_wma(e, params):
    t = params.get("length", undefined)
    if t is undefined:
        t = 14
    script_assert(_is_arr(e), "wma(): first argument must be a series")
    is_arr = _is_arr(t)
    if is_arr:
        script_assert(len(t) == len(e), "wma(): the length array must have the same size with the source")
    else:
        script_assert(J.ge(t, 1), "wma(): invalid length")
    a = [None] * len(e)
    i = next((k for k, v in enumerate(e) if v is not None), -1)
    for r in range(i, len(e)) if i >= 0 else ():
        s = J.Math["ceil"](t[r]) if is_arr else t
        if J.lt(J.add(J.sub(r, s), 1), i):
            a[r] = None
        else:
            w = J.get(e, "slice")(J.add(J.sub(r, s), 1), r + 1)
            acc = 0
            for n, v in enumerate(w):
                acc = J.add(acc, J.mul(v, n + 1))
            a[r] = J.div(acc, J.div(J.mul(s, J.add(s, 1)), 2))
    return JSArray(a)


def _ind_custwma(e, params):
    t = params.get("weights", undefined)
    if t is undefined:
        t = JSArray([0.16, 0.33, 0.33, 0.16])
    script_assert(_is_arr(e), "custwma(): first argument must be a series")
    script_assert(_is_arr(t), "custwma(): 'weights' must be a series")
    n = [None] * len(e)
    a = _w_sum(t)
    k = len(t)
    for r in range(0, len(e) - k + 1):
        s = 0
        for m in range(r, r + k):
            s = J.add(s, J.mul(e[m], t[m - r]))
        n[r + k - 1] = J.div(s, a)
    return JSArray(n)


def _ind_rsi(e, params):
    t = params.get("length", undefined)
    if t is undefined:
        t = 14
    script_assert(_is_arr(e), "rsi(): first argument must be a series")
    script_assert(J.ge(t, 1), "rsi(): invalid length")
    n = len(e)
    gains = [None] * n
    losses = [None] * n
    for k in range(1, n):
        if e[k] is not None and e[k - 1] is not None:
            d = J.sub(e[k], e[k - 1])
            gains[k] = J.Math["max"](d, 0)
            losses[k] = J.Math["max"](J.neg(d), 0)
        else:
            gains[k] = losses[k] = None
    s = calculate_indicator("wildma", "wildma", ["length"], JSObject(close=JSArray(gains)), t)
    script_assert(len(s) == n, "rsi(): internal error 1")
    o = calculate_indicator("wildma", "wildma", ["length"], JSObject(close=JSArray(losses)), t)
    script_assert(len(o) == n, "rsi(): internal error 1")
    return JSArray(
        (J.sub(100, J.div(100, J.add(1, J.div(s[k], J.add(o[k], 1e-9))))) if (s[k] is not None and o[k] is not None) else None)
        for k in range(n)
    )


def _ind_hullma(e, params):
    t = params.get("length", undefined)
    if t is undefined:
        t = 14
    script_assert(_is_arr(e), "hullma(): first argument must be a series")
    script_assert(J.ge(t, 1), "hullma(): invalid length")
    n = calculate_indicator("wma", "wma", ["length"], e, J.Math["floor"](J.div(t, 2)))
    script_assert(len(n) == len(e), "hullma(): internal error 1")
    a = calculate_indicator("wma", "wma", ["length"], e, t)
    script_assert(len(a) == len(e), "hullma(): internal error 2")
    mid = JSArray((None if (v is None or a[k] is None) else J.sub(J.mul(2, v), a[k])) for k, v in enumerate(n))
    return calculate_indicator("wma", "wma", ["length"], mid, J.Math["floor"](J.Math["sqrt"](t)))


def _ind_cmo(e, params):
    t = params.get("length", undefined)
    if t is undefined:
        t = 9
    script_assert(_is_arr(e), "cmo(): first argument must be a series")
    script_assert(J.ge(t, 1), "cmo(): invalid length")
    n = len(e)
    a, i, s = [None] * n, [None] * n, [None] * n
    for k in range(1, n):
        if e[k] is not None and e[k - 1] is not None:
            d = J.sub(e[k], e[k - 1])
            a[k] = J.Math["max"](d, 0)
            i[k] = J.Math["max"](J.neg(d), 0)
        else:
            a[k] = i[k] = None
        if J.gt(k, t) and a[k] is not None and i[k] is not None:
            up = dn = 0
            m = J.add(J.sub(k, t), 1)
            while J.le(m, k):
                up = J.add(up, J.get(a, m))
                dn = J.add(dn, J.get(i, m))
                m = J.add(m, 1)
            s[k] = J.div(J.sub(up, dn), J.add(up, dn))
    return JSArray(s)


def _ind_roc(e, params):
    t = params.get("length", undefined)
    script_assert(_is_arr(e), "rox(): first argument must be a series")
    script_assert(J.ge(t, 1), "roc(): invalid length")
    n = [None] * len(e)
    r = t
    while J.lt(r, len(e)):
        prev = J.get(e, J.sub(r, t))
        J_set_idx(n, r, J.div(J.mul(100, J.sub(J.get(e, r), prev)), prev))
        r = J.add(r, 1)
    return JSArray(n)


def J_set_idx(lst, i, v):
    i = J._index(i)
    if i is not None and 0 <= i < len(lst):
        lst[i] = v


def _ind_atr(e, params):
    t, n, o, c = (params.get(k, undefined) for k in ("param1", "param2", "param3", "param4"))
    if _is_arr(t):
        script_assert(_is_arr(n), "atr(): if the first argument is a series, then the second one must also be a series")
        script_assert(_is_arr(o), "atr(): if the first argument is a series, then the third one must also be a series")
        d, p, h, u = t, n, o, c
    else:
        u = t
        d = [cd[2] for cd in e]
        p = [cd[3] for cd in e]
        h = [cd[4] for cd in e]
    L = len(d)
    f = [None] * L
    mx, mn = J.Math["max"], J.Math["min"]
    for k in range(1, L):
        f[k] = J.sub(mx(J.get(d, k), J.get(h, k - 1)), mn(J.get(p, k), J.get(h, k - 1)))
    m = [None] * L
    um1 = J.sub(u, 1)
    for k in range(L):
        prev = m[k - 1] if k >= 1 else undefined
        prev = prev if J.truthy(prev) else 0
        m[k] = J.div(J.add(J.mul(prev, um1), f[k]), u)
    b = _int_len(um1)
    return {"begIndex": b, "result": {"outReal": JSArray(m[b:])}}


def _ind_vwap(e, params):
    t, n, a, i = (params.get(k, undefined) for k in ("param1", "param2", "param3", "param4"))
    script_assert(_is_arr(e))
    if _is_arr(t):
        script_assert(_is_arr(n), "vwap(): if the first argument is a series, then the second one must also be a series")
        u, d = t, n
        s = a if J.truthy(a) else 0
        l = i if J.truthy(i) else None
    else:
        s = t if J.truthy(t) else 0
        l = n if J.truthy(n) else None
        u = [(cd[1] + cd[4] + cd[2] + cd[3]) / 4 for cd in e]
        d = [cd[5] for cd in e]
    script_assert(not J.isNaN(s) and J.ge(s, 0), 'vwap(): "fromIndex" is invalid')
    if l is not None:
        script_assert(not J.isNaN(l) and J.ge(l, 0), 'vwap(): "toIndex" is invalid')
        script_assert(J.gt(l, s), 'vwap(): "toIndex" must be greater than "fromIndex"')
    p = [None] * len(u)
    h = l if J.truthy(l) else len(u) - 1
    si, hi = _int_len(s), _int_len(h)
    # Running sums reproduce the engine's per-point re-summation exactly:
    # each partial sum is built from the same additions in the same order.
    tt = nn = 0
    for k in range(si, hi + 1):
        vol = J.get(d, k)
        tt = J.add(tt, J.mul(vol, J.get(u, k)))
        nn = J.add(nn, vol)
        val = J.get(u, k) if (J.seq(tt, 0) and J.seq(nn, 0)) else J.div(tt, nn)
        if k < len(p):
            p[k] = val
        else:
            p.extend([undefined] * (k - len(p)))
            p.append(val)
    return {"begIndex": si, "result": {"outReal": JSArray(p[si:])}}


def _ind_stochastic(e, params):
    t, n, a, i = (params.get(k, undefined) for k in ("close", "high", "low", "length"))
    t = None if t is undefined else t
    n = None if n is undefined else n
    a = None if a is undefined else a
    script_assert(_is_arr(t), 'stochastic(): "close" must be a series')
    script_assert(_is_arr(n), 'stochastic(): "high" must be a series')
    script_assert(_is_arr(a), 'stochastic(): "low" must be a series')
    script_assert(len(t) == len(n) == len(a), "stochastic(): input series length mismatch")
    script_assert(not J.isNaN(i) and J.ge(i, 1), 'stochastic(): "length" is invalid')
    ii = _int_len(i)
    s = [None] * len(t)
    for k in range(ii, len(t)):
        r = t[k]
        lo = J.Math["min"](*a[k - ii + 1 : k + 1])
        hi = J.Math["max"](*n[k - ii + 1 : k + 1])
        v = J.mul(J.div(J.sub(r, lo), J.add(J.sub(hi, lo), 1e-9)), 100)
        s[k] = J.to_number(J.n_toFixed(v, 3))
    return {"begIndex": ii, "result": {"outReal": JSArray(s[ii:])}}


def _seqcount(e, t):
    # TD Sequential (engine module "SEQUENTIAL_COUNT"). Rarely used by
    # store scripts; ported for completeness.
    if t.get("chartType") == "line":
        return {"error": {"error": "not_applicable_to_given_chart_type"}}
    n = {
        "high": t.get("customHigh") if J.truthy(t.get("customHigh", undefined)) else e["high"],
        "low": t.get("customLow") if J.truthy(t.get("customLow", undefined)) else e["low"],
        "close": t.get("customClose") if J.truthy(t.get("customClose", undefined)) else e["close"],
    }
    raise J.Unsupported("seqcount() is not ported")


_SERIES_INDICATORS = {
    "sma": _ind_sma,
    "wma": _ind_wma,
    "custwma": _ind_custwma,
    "rsi": _ind_rsi,
    "hullma": _ind_hullma,
    "cmo": _ind_cmo,
    "roc": _ind_roc,
    "atr": _ind_atr,
    "vwap": _ind_vwap,
    "stochastic": _ind_stochastic,
    "ema": lambda e, p: _sliding(False, _ema_step, e, p["optInTimePeriod"]),
    "max": lambda e, p: _sliding(True, lambda w, *_: J.Math["max"](*[v for v in w if v is not None]), e, p["optInTimePeriod"]),
    "min": lambda e, p: _sliding(True, lambda w, *_: J.Math["min"](*[v for v in w if v is not None]), e, p["optInTimePeriod"]),
    "sum": lambda e, p: _sliding(True, lambda w, *_: _w_sum(w), e, p["optInTimePeriod"]),
    "momentum": lambda e, p: _sliding(True, lambda w, *_: J.sub(w[-1], w[0]), e, p["optInTimePeriod"]),
    "stdev": lambda e, p: _sliding(False, lambda w, t, _p: _stdev(w, t), e, p["optInTimePeriod"]),
    "absdev": lambda e, p: _sliding(False, lambda w, t, _p: _absdev(w, t), e, p["optInTimePeriod"]),
    "variance": lambda e, p: _sliding(False, lambda w, t, _p: _variance(w, t), e, p["optInTimePeriod"]),
    "linreg": lambda e, p: _sliding(False, _linreg, e, p["optInTimePeriod"]),
    "fractal_high": lambda e, p: _fractal_merge(lambda w, pp: _fractal(True, w, pp), e, p),
    "fractal_low": lambda e, p: _fractal_merge(lambda w, pp: _fractal(False, w, pp), e, p),
}


def _table_wrapper(fn):
    def run(table, params):
        script_assert(_is_arr(table.get("close")))
        a = fn(table, params)
        if isinstance(a, dict) and "error" in a and isinstance(a["error"], dict) and a["error"].get("error"):
            return a["error"]
        return a.get("data", a) if isinstance(a, dict) else a

    return run


for _k, _f in _TABLE_INDICATORS.items():
    _SERIES_INDICATORS[_k] = _table_wrapper(_f)


def calculate_indicator(name, type_, param_names, data, *args):
    """Engine's calculateIndicator (M): runs a named indicator on a series
    or a table and re-pads the result to the input's length."""
    if param_names is None:
        raise J.JSError(J.make_error(f'Error calculating "{name}": Cannot read properties of undefined (reading \'forEach\')'))
    s = 0
    if isinstance(data, dict) and J.truthy(data.get("close")):
        script_assert(_is_arr(data["close"]), f"{name}(): input data seems to be a table but misses .close")
        mode, payload = "raw", data
    else:
        script_assert(_is_arr(data), f"{name}(): input data must be a series")
        mode = "simple"
        s = next((k for k, v in enumerate(data) if v is not None), -1)
        if s == -1:
            return data
        payload = JSArray(data[s:])
    params = {}
    for k, pn in enumerate(param_names):
        params[pn] = args[k] if k < len(args) else undefined
    fn = _SERIES_INDICATORS.get(type_)
    try:
        if fn is None:
            raise J.JSError(J.make_error(f'Indicator "{type_}" does not exist'))
        res = fn(payload, params)
        if isinstance(res, dict) and "error" in res and not isinstance(res.get("error"), dict):
            raise _CalcError(res["error"])
        if isinstance(res, list):
            return JSArray([None] * s + list(res))
        result = res["result"]
        keys = list(result.keys())
        if res.get("isEmpty"):
            out = {k: JSArray([None] * len(data)) for k in keys}
        else:
            b = s + res["begIndex"]
            if b == math.inf:
                raise J.JSError(J.make_error("Invalid array length", "RangeError"))
            out = {k: JSArray([None] * int(b) + list(result[k])) for k in keys}
        return out[keys[0]] if len(keys) == 1 else JSObject(out)
    except _CalcError as exc:
        raise J.JSError(J.make_error(f'Error calculating "{name}": {exc.args[0]}'))
    except J.JSError as exc:
        msg = J.to_str(J.get(exc.value, "message")) if isinstance(exc.value, dict) else J.to_str(exc.value)
        raise J.JSError(J.make_error(f'Error calculating "{name}": {msg}'))


# ----------------------------------------------------------------------------
# the script-facing API
# ----------------------------------------------------------------------------

PRICE_SOURCE_OPTIONS = ["open", "high", "low", "close", "hl2", "oc2", "hlc3", "ohlc4", "wclose"]
TIME_FRAMES = ["1", "2", "3", "4", "5", "6", "10", "12", "15", "30", "45", "60", "65", "90", "120", "240", "1440", "D", "W", "M", "Q", "Y"]
MA_TYPES = ["ema", "sma", "wildma", "vwma", "wma", "hullma", "kama", "alma", "twap"]
BANNED = [
    "fetch", "XMLHttpRequest", "WebSocket", "Request", "Worker", "BackgroundFetchManager", "EventSource",
    "addEventListener", "postMessage", "dispatchEvent", "removeEventListener", "eval", "importScripts", "require",
]
ICONS = {
    "arrow_up": "↑", "arrow_up_diagonal": "↗", "arrow_down": "↓", "arrow_down_diagonal": "↘",
    "triangle_up": "▲", "triangle_down": "▼", "diamond": "◆", "circle": "⬤", "square": "◼",
    "star": "★", "sun": "☀", "flag": "⚑",
}
STYLE_RENDER = {
    "histogram": "bars", "column": "bars", "stacked_histogram": "stacked_bars", "stacked_column": "stacked_bars",
    "dotted": "dotted", "ladder": "ladder", "labels_above": "OVER_CANDLES", "labels_below": "OVER_CANDLES",
    "coloredline": "coloredline", "horizontal_bars": "horizontal_bars", "area": "area", "arearange": "arearange",
    "columnrange": "columnrange", "candles": "candles", "boxplot": "boxplot", "bubble": "bubble", "line": "default",
    "pie": "pie",
}


class ScriptContext:
    """Everything one script run needs: bars, user inputs, symbol info and
    the data provider for request.*()."""

    def __init__(self, bars, inputs=None, ticker="AAPL", resolution="D", session=None, ext_session=None,
                 provider=None, symbol_info=None, now=None):
        self.bars = bars  # dict: time (unix s), open, high, low, close, volume
        self.inputs = dict(inputs or {})
        self.ticker = ticker
        self.resolution = str(resolution)
        self.session = session or REGULAR_SESSION
        self.ext_session = ext_session or EXTENDED_SESSION
        self.provider = provider
        self.symbol_info = symbol_info or {}
        self.now = now


REGULAR_SESSION = JSObject(identifier="us_regular", timezone="America/New_York",
                           start=JSObject(hours=9, minutes=30), end=JSObject(hours=16, minutes=0),
                           lengthMinutes=390, marketDays=JSArray([1, 2, 3, 4, 5]))
EXTENDED_SESSION = JSObject(identifier="us_extended", timezone="America/New_York",
                            start=JSObject(hours=4, minutes=0), end=JSObject(hours=20, minutes=0),
                            lengthMinutes=960, marketDays=JSArray([1, 2, 3, 4, 5]))
PRE_SESSION = JSObject(identifier="us_pre", timezone="America/New_York",
                       start=JSObject(hours=4, minutes=0), end=JSObject(hours=9, minutes=30),
                       lengthMinutes=330, marketDays=JSArray([1, 2, 3, 4, 5]))
POST_SESSION = JSObject(identifier="us_post", timezone="America/New_York",
                        start=JSObject(hours=16, minutes=0), end=JSObject(hours=20, minutes=0),
                        lengthMinutes=240, marketDays=JSArray([1, 2, 3, 4, 5]))


class ScriptResult:
    def __init__(self):
        self.meta = JSObject(forceNoColorThemeSupport=True, platform="custom-scripting@1.0",
                             inputs=JSArray(), appearance=JSObject())
        self.out = {}  # id -> list (per-candle values)
        self.logs = []


def build_api(ctx: ScriptContext, res: ScriptResult):
    from app.indicators.trendspider_store._runtime import libraries

    bars = ctx.bars
    n = len(bars["time"])
    S, W = res.meta, res.out
    F = {}

    def Y():
        script_assert(len(W) < MAX_OUT_SERIES, "Max amount of out series exceeded (70)")

    palette = ["#000", "blue", "red", "green", "orange", "teal", "maroon", "fuchsia"]
    color_i = [0]

    def next_color():
        c = palette[color_i[0]]
        color_i[0] = (color_i[0] + 1) % len(palette)
        return c

    # ---- data -----------------------------------------------------------------
    T = JSArray(int(t) if float(t).is_integer() else t for t in bars["time"])
    O, H, Lo, C, V = (JSArray(bars[k]) for k in ("open", "high", "low", "close", "volume"))
    candles = JSArray(JSArray([T[i] * 1000, O[i], H[i], Lo[i], C[i], V[i]]) for i in range(n))
    F["candles"] = candles
    F["candlesAsObjects"] = JSArray(JSObject(index=i, time=T[i] * 1000, open=O[i], high=H[i], low=Lo[i], close=C[i]) for i in range(n))
    F["time"], F["open"], F["high"], F["low"], F["close"], F["volume"] = T, O, H, Lo, C, V
    F["hl2"] = JSArray((H[i] + Lo[i]) / 2 for i in range(n))
    F["oc2"] = JSArray((O[i] + C[i]) / 2 for i in range(n))
    F["hlc3"] = JSArray((H[i] + Lo[i] + C[i]) / 3 for i in range(n))
    F["ohlc4"] = JSArray((O[i] + H[i] + Lo[i] + C[i]) / 4 for i in range(n))
    F["wclose"] = JSArray((H[i] + Lo[i] + 2 * C[i]) / 4 for i in range(n))
    F["body_top"] = JSArray(J._max(O[i], C[i]) for i in range(n))
    F["body_bottom"] = JSArray(J._min(O[i], C[i]) for i in range(n))
    prices = JSObject(open=O, high=H, low=Lo, close=C, hl2=F["hl2"], oc2=F["oc2"], hlc3=F["hlc3"],
                      ohlc4=F["ohlc4"], wclose=F["wclose"], body_top=F["body_top"], body_bottom=F["body_bottom"],
                      time=T, volume=V)
    F["prices"] = prices
    F["market"] = prices

    # ---- indicator bindings (engine table C) ------------------------------------
    def bound(name, type_, pnames, data=None):
        def f(*args):
            if data is None:
                if not args:
                    raise J.type_error("Cannot read properties of undefined")
                return calculate_indicator(name, type_, pnames, args[0], *args[1:])
            return calculate_indicator(name, type_, pnames, data, *args)

        return f

    def psar(*e):
        e = list(e)
        if not (e and _is_arr(e[0])):
            e[0:0] = [undefined, undefined]
        return calculate_indicator("psar", "psar", ["customHigh", "customLow", "optInMaximum", "optInAcceleration", "optInStart"], prices, *e)

    def wildma(e=undefined, *t):
        script_assert(_is_arr(e), "wildma(): first argument must be a series")
        return calculate_indicator("wildma", "wildma", ["length"], JSObject(close=e, time=T), *t)

    def vwma(e=undefined, *t):
        script_assert(_is_arr(e), "vwma(): first argument must be a series")
        script_assert(_is_arr(V), "vwma(): this symbol has no volume data")
        return calculate_indicator("vwma", "vwma", ["length"], JSObject(close=e, volume=V, time=T), *t)

    def alma(e=undefined, *t):
        script_assert(_is_arr(e), "alma(): first argument must be a series")
        return calculate_indicator("alma", "alma", ["window", "sigma", "offs"], JSObject(close=e, time=T), *t)

    def kama(e=undefined, *t):
        script_assert(_is_arr(e), "kama(): first argument must be a series")
        return calculate_indicator("kama", "kama", ["ERLength", "fastPeriod", "slowPeriod"], JSObject(close=e, time=T), *t)

    def seqcount(*e):
        raise J.Unsupported("seqcount() (TD Sequential) is not ported")

    C_ = {
        "sma": bound("sma", "sma", ["optInTimePeriod"]),
        "avg": bound("avg", "avg", None),
        "ema": bound("ema", "ema", ["optInTimePeriod"]),
        "highest": bound("highest", "max", ["optInTimePeriod"]),
        "lowest": bound("lowest", "min", ["optInTimePeriod"]),
        "sum": bound("sum", "sum", ["optInTimePeriod"]),
        "momentum": bound("momentum", "momentum", ["optInTimePeriod"]),
        "stdev": bound("stdev", "stdev", ["optInTimePeriod"]),
        "absdev": bound("absdev", "absdev", ["optInTimePeriod"]),
        "variance": bound("variance", "variance", ["optInTimePeriod"]),
        "fractal_high": bound("fractal_high", "fractal_high", ["optInTimePeriod", "peakIndex"]),
        "fractal_low": bound("fractal_low", "fractal_low", ["optInTimePeriod", "peakIndex"]),
        "vwap": bound("vwap", "vwap", ["param1", "param2", "param3", "param4"], candles),
        "atr": bound("atr", "atr", ["param1", "param2", "param3", "param4"], candles),
        "stochastic": bound("stochastic", "stochastic", ["close", "high", "low", "length"], candles),
        "psar": psar,
        "wildma": wildma,
        "vwma": vwma,
        "alma": alma,
        "vortex": lambda *e: calculate_indicator("vortex", "vortex", ["optInTimePeriod"], prices, *e),
        "kama": kama,
        "rsi": bound("rsi", "rsi", ["length"]),
        "wma": bound("wma", "wma", ["length"]),
        "custwma": bound("custwma", "custwma", ["weights"]),
        "hullma": bound("hullma", "hullma", ["length"]),
        "seqcount": seqcount,
        "cmo": bound("cmo", "cmo", ["length"]),
        "linreg": bound("linreg", "linreg", ["optInTimePeriod"]),
        "roc": bound("roc", "roc", ["length"]),
    }

    # ---- arithmetic helpers (engine j / I) ---------------------------------------
    def pairwise(fn, t, other):
        script_assert(_is_arr(t), "first argument is not a series")
        script_assert(_is_arr(other) or not J.isNaN(other), "invalid second argument")
        scalar = not J.isNaN(other)
        if not scalar:
            script_assert(len(t) == len(other), f"series length mismatch ({len(t)} vs {len(other)})")
        out = JSArray()
        for r, v in enumerate(t):
            if v is None:
                out.append(None)
            elif scalar or J.get(other, r) is not None:
                out.append(fn(v, other if scalar else J.get(other, r)))
            else:
                out.append(None)
        return out

    def fold(fn):
        def f(*t):
            script_assert(len(t) >= 2, "at least 2 arguments expected")
            script_assert(all(_is_arr(x) or not J.isNaN(x) for x in t), "only time series or numbers are accepted as arguments")
            acc = t[0]
            for x in t[1:]:
                acc = pairwise(fn, acc, x)
            return acc

        return f

    def horizontal_line(e=undefined, t=0, a=math.inf, *_):
        script_assert(not J.isNaN(e), "horizontal_line(): invalid value")
        t = 0 if t is undefined else t
        a = math.inf if a is undefined else a
        return JSArray((J.pos(e) if (J.ge(r, t) and J.le(r, a) and e is not None) else None) for r in range(n))

    def series_of(e=undefined, *_):
        return JSArray([e] * n)

    def sliding_window_function(e=undefined, t=undefined, cb=undefined, *_):
        script_assert(_is_arr(e), "first argument is not a series")
        script_assert(not J.isNaN(t) and J.gt(t, 0), "windowSize must be a positive integer")
        a = _sliding(False, lambda w, per, prev: cb(w, per, prev), e, t)
        return JSArray([None] * a["begIndex"] + list(a["result"]["outReal"]))

    def shift(e=undefined, t=undefined, *_):
        script_assert(_is_arr(e), "first argument is not a series")
        script_assert(not J.isNaN(t), "invalid offset")
        if J.gt(t, 0):
            return JSArray([None] * _int_len(t) + list(J.a_slice(e, 0, J.sub(len(e), t))))
        if J.lt(t, 0):
            return JSArray(list(J.a_slice(e, J.neg(t))) + [None] * _int_len(J.neg(t)))
        return e

    def for_every(*e):
        script_assert(len(e) >= 2, "for_every(): At least 2 arguments expected")
        cb = e[-1]
        script_assert(callable(cb), "for_every(): Last argument must be a callback")
        ser = e[:-1]
        script_assert(all(_is_arr(x) for x in ser), "for_every(): All argumens except of the last one must be time series")
        lens = {len(x) for x in ser}
        script_assert(len(lens) == 1, "for_every(): All series must have equal length")
        m = lens.pop()
        out = JSArray([None] * m)
        o = None
        started = False
        for k in range(m):
            vals = [J.get(x, k) for x in ser]
            if not started and any(v is None for v in vals):
                continue
            started = True
            o = cb(*vals, o, k)
            out[k] = o
        return out

    def describe_indicator(e=undefined, t="price", opts=undefined, *_):
        if not isinstance(e, str):
            e = J.to_str(e)
        if t is undefined:
            t = "price"
        opts = JSObject() if opts is undefined else opts
        if isinstance(t, dict):
            opts, t = t, "price"
        S["name"] = e[:60]
        S["lower"] = t == "lower"
        if J.truthy(J.get(opts, "isAnchored")):
            opts["autoAnchoredByDefault"] = True
        if J.truthy(J.get(opts, "warmup")):
            S["inputs"].append(JSObject(id="warmup", title="Warmup", hidden=True, value=opts["warmup"]))
            del opts["warmup"]
        for k in list(opts.keys()):
            script_assert(isinstance(opts[k], str) or J.is_number(opts[k]),
                          f'describe_indicator(): only primitive types can go in metainfo, "{k}" contains illegal type')
            if k in ("helpArticle", "category", "extendedSearchString", "appearance", "inputs", "bands",
                     "approvedForProduction", "scriptingDisabledForPurpose", "author"):
                del opts[k]
        if "decimals" in opts and J.is_number(opts["decimals"]):
            opts["decimals"] = min(max(0, opts["decimals"]), 12)
        S.update(opts)
        return undefined

    def P(e, t=undefined, a=undefined, i="line", s=1, o=False, c=False, l=None):
        l = JSObject() if l is None else l
        if not J.truthy(t):
            t = f"Line {len(S['appearance']) + 1}"
        if not J.truthy(a):
            a = next_color()
        script_assert(_is_arr(e), "paint(): first argument is not an array")
        if i is undefined:
            i = "line"
        if s is undefined:
            s = 1
        u = id_from_humanized(J.to_str(t))
        script_assert(u not in S["appearance"], f'paint(): out series "{J.to_str(t)}" already exists')
        script_assert(u not in W, f'paint(): out series named "{J.to_str(t)}" already exists')
        script_assert(not J.isNaN(s) and J.gt(s, 0), f'paint(): "{J.to_str(t)}" thickness is invalid')
        S["appearance"][u] = JSObject(title=t, lineWidth=s, ignoreWhenScaling=c)
        M = S["appearance"][u]
        for key in ("editorHidden", "hideInLegend", "hideInScriptEditor", "canHaveOnlyOne", "enableMouseTracking",
                    "isProjection", "lastValueLineEnabled", "lastValueLabelEnabled", "forceUsePriceAxis"):
            if isinstance(l, dict) and key in l:
                M[key] = J.truthy(l[key])
        if isinstance(l, dict) and J.truthy(l.get("invisibleByDefault", undefined)):
            M["isVisible"] = False
        if _is_arr(a):
            script_assert(len(a) == len(e), "paint(): color series length mismatch")
            M.update(color="#777", colorOfPoint="BY_COLOR_SERIES_AS_IS")
            cid = f"{u}_color"
            P(a, cid)
            nn = S["appearance"][cid]
            nn.update(hasNoRealSeries=True, hideInLegend=True, hideInScriptEditor=True)
            nn.pop("color", None)
            nn.pop("lineWidth", None)
            if i == "line":
                i = "coloredline"
        else:
            script_assert(J.truthy(a) and len(J.to_str(a)) <= 25, f'paint(): invalid color for "{J.to_str(t)}"')
            M["color"] = a
            if J.truthy(o):
                M.update(hasNoRealSeries=True, hideInLegend=True, hideInScriptEditor=True, editorHidden=True)
        f = STYLE_RENDER.get(i) if isinstance(i, str) else None
        script_assert(f, f'paint(): out series "{J.to_str(t)}" has unknown style "{J.to_str(i)}"')
        if f != "default":
            M["renderAs"] = f
        script_assert(len(e) == n, f"paint(): output series length mismatch. {len(e)} data points provided, but only {n} candles exist")
        W[u] = list(e)
        Y()
        return u

    def R(e=undefined, *t):
        if not t or not J.truthy(t[0]) or isinstance(t[0], str):
            return P(e, *t)
        script_assert(isinstance(t[0], dict), "paint(): second argument is invalid")
        d = t[0]
        g = lambda k: d.get(k, undefined)  # noqa: E731
        return P(e, g("name"), g("color"), g("style") if g("style") is not undefined else "line",
                 g("thickness") if g("thickness") is not undefined else 1,
                 g("hidden") if g("hidden") is not undefined else False,
                 g("ignoreWhenScaling") if g("ignoreWhenScaling") is not undefined else False, d)

    def paint(*e):
        return R(*e)

    def color_candles(e=undefined, *_):
        script_assert(_is_arr(e), "color_candles(): first argument must be a series")
        cnt = len([v for v in S["appearance"].values() if v.get("renderAs") == "colored_candles"])
        t = f"Cdl{cnt or ''}"
        a = id_from_humanized(t)
        script_assert(a not in S["appearance"], f'color_candles(): series named "{t}" already exists')
        script_assert(a not in W, f'color_candles(): series named "{t}" already exists')
        S["timeFramesAllowed"] = JSObject(primary=1)
        S["canHaveOnlyOne"] = True
        S["appearance"][a] = JSObject(title=t, hideInLegend=True, hideInScriptEditor=True, color="#777", lineWidth=1,
                                      renderAs="coloredcandles", rendererType="coloredcandles", colorOfPoint="BY_OWN_VALUE")
        W[a] = list(e)[:n] + [None] * max(0, n - len(e)) if len(e) != n else list(e)
        Y()
        return undefined

    def fill(e=undefined, t=undefined, c=undefined, a=0.33, i="Fill", *_):
        if not J.truthy(c):
            c = "red"
        a = 0.33 if a is undefined else a
        i = "Fill" if i is undefined else i
        script_assert(isinstance(e, str), "first argument must be a reference to a painted series")
        script_assert(isinstance(t, str), "second argument must be a reference to a painted series")
        script_assert(isinstance(c, str), "color must be a string")
        script_assert(e in S["appearance"], f'"{e}" must have a corresponding paint() call')
        script_assert(t in S["appearance"], f'"{t}" must have a corresponding paint() call')
        had = J.truthy(S.get("bands", undefined))
        if not had:
            S["bands"] = JSArray()
        o = f"band_{e}_{t}"
        cid = o if had else "band"
        script_assert(cid not in S["appearance"], "you can't fill the same area more than once")
        S["bands"].append(JSObject(**{"from": e, "to": t, "id": o if had else "body"}))
        S["appearance"][cid] = JSObject(title=i, hideInLegend=True, hideInScriptEditor=True, opacity=a, color=c)
        return undefined

    def paint_label_at_line(e=undefined, t=undefined, text=undefined, a=undefined, *_):
        a = JSObject() if a is undefined else a
        script_assert(isinstance(e, str) and e in W and e != "__proto__",
                      "paint_label_at_line(): first argument must be a reference to a painted series")
        script_assert(J.is_number(t), "paint_label_at_line(): second argument must be a number indicating the index of a point to put your label to")
        script_assert(isinstance(text, str), 'paint_label_at_line(): "labelText" must be a string')
        script_assert(1 <= len(text) <= 300, 'paint_label_at_line(): "labelText" must contain from 1 to 300 characters')
        script_assert(isinstance(a, dict), 'paint_label_at_line(): "attributes" must be an object')
        ti = J._index(t)
        if t < 0 or t >= len(W[e]) or ti is None or W[e][ti] is None or W[e][ti] is undefined:
            return undefined
        ap = S["appearance"][e]
        script_assert(ap.get("renderAs") != "OVER_CANDLES", "paint_label_at_line(): Can't paint a label on that type of a line.")
        allowed = ["color", "border_radius", "border_width", "border_color", "background_color", "vertical_align", "halo"]
        for k in a:
            script_assert(k in allowed, f'paint_label_at_line(): "{k}" is not supported')
        idx = ti
        if J.truthy(ap.get("isProjection", undefined)):
            idx += len(F["close"]) - 100
        cur = W[e][idx]
        y = cur.get("y") if isinstance(cur, dict) and "y" in cur else cur
        W[e][idx] = JSObject(y=y, label=text)
        return undefined

    def paint_overlay(e=undefined, t=undefined, a=undefined, *_):
        script_assert(isinstance(e, str), 'paint_overlay(): "name" must be a string')
        script_assert(isinstance(t, dict), 'paint_overlay(): "params" must be an object')
        script_assert(isinstance(a, dict), 'paint_overlay(): "definition" must be an object')
        i = id_from_humanized(e)
        script_assert(i not in S["appearance"], f'paint_overlay(): out series "{e}" already exists')
        script_assert(i not in W, f'paint_overlay(): out series named "{e}" already exists')
        t["position"] = t.get("position") if J.truthy(t.get("position", undefined)) else "top_right"
        script_assert(t["position"] in ("top_left", "center_left", "bottom_left", "top_right", "center_right", "bottom_right"),
                      "paint_overlay(): invalid position value")
        t["parent"] = t.get("parent") if J.truthy(t.get("parent", undefined)) else "parent"
        script_assert(t["parent"] in ("chart", "parent"), "paint_overlay(): invalid parent value")
        t["order"] = t.get("order") if J.truthy(t.get("order", undefined)) else "below_all"
        script_assert(t["order"] in ("below_all", "above_all"), "paint_overlay(): invalid order value")
        S["appearance"][i] = JSObject(title=e, rendererType="visualGrid", position=t["position"])
        S["timeFramesAllowed"] = JSObject(primary=1)
        W[i] = [None] * n
        if n:
            W[i][-1] = J._parse(J._stringify(a))
        Y()
        return undefined

    def paint_projection(*e):
        script_assert(isinstance(e[0], str) or _is_arr(e[0]) if e else False,
                      "paint_projection(): first argument must be a string (paintedLineId) or an array (values)")
        t = min(n, 100)
        if _is_arr(e[0]):
            vals = e[0]
            opts = JSObject(hideInScriptEditor=True)
            if len(e) > 1 and isinstance(e[1], dict):
                opts.update(e[1])
            opts["isProjection"] = True
        else:
            script_assert(e[0] in W, "paint_projection(): first argument must be a reference to a painted series")
            script_assert(_is_arr(e[1]), "paint_projection(): second argument must be an array")
            vals = e[1]
            opts = JSObject(hideInScriptEditor=True)
            opts.update(S["appearance"][e[0]])
            opts["isProjection"] = True
            ra = opts.get("renderAs", undefined)
            opts["style"] = "histogram" if ra == "bars" else ("stacked_histogram" if ra == "stacked_bars" else ra)
            opts["thickness"] = opts.get("lineWidth", undefined)
            opts["name"] = f"{opts['title']} proj."
        series = [None] * (n - t) + list(vals[:t]) + [None] * max(0, n - (n - t + len(vals)))
        series = series[:n] + [None] * max(0, n - len(series))
        sid = R(JSArray(series), opts)
        S["inputs"].append(JSObject(id=f"{sid}__offset", type="number", hidden=True, hideInLegend=True, value=t - 1,
                                    hideInScriptEditor=True))
        return sid

    def register_signal(e=undefined, t=undefined, *_):
        script_assert(_is_arr(e), "register_signal(): first argument must be a series")
        script_assert(isinstance(t, str) and bool(t.strip()), "register_signal(): invalid signal name")
        u = id_from_humanized(t)
        script_assert(u not in S["appearance"], f'register_signal(): signal "{t}" already exists')
        script_assert(u not in W, f'register_signal(): signal "{t}" already exists')
        R(e, JSObject(name=t))
        S["appearance"][u].update(hideInLegend=True, editorHidden=True, isSignalSeries=True)
        S["appearance"][u].pop("lineWidth", None)
        S["appearance"][u].pop("color", None)
        S.setdefault("signals", JSArray()).append(u)
        return undefined

    def interpolate_sparse_series(e=undefined, t="linear", *_):
        if t is undefined:
            t = "linear"
        script_assert(_is_arr(e), "first argument must be a series")
        script_assert(t in ("linear", "constant"), 'invalid "mode" value')
        first = next((k for k, v in enumerate(e) if v is not None), -1)
        if first < 0:
            return e
        a = first
        out = [None] * a
        for k in range(a + 1, len(e)):
            r = e[k]
            if r is None:
                continue
            s = k - a
            o = e[a]
            if t == "linear":
                step = J.div(J.sub(r, o), s)
                out.extend(J.add(o, J.mul(step, m)) for m in range(s))
            else:
                out.extend([o] * s)
            a = k
        out.append(e[a])
        tail = None if t == "linear" else e[a]
        out.extend([tail] * (len(e) - a - 1))
        script_assert(len(out) == len(e), "internal error 44")
        return JSArray(out)

    def indexed_points_of(e=undefined, *_):
        script_assert(_is_arr(e), "first argument must be a series")
        return JSArray(JSObject(value=v, candleIndex=k) for k, v in enumerate(e) if v is not None)

    def land_points_onto_series(e=undefined, t=undefined, tgt=undefined, a="eq", merge=None, *_):
        if a is undefined:
            a = "eq"
        if merge is undefined:
            merge = None
        script_assert(_is_arr(e), "first argument must be a series")
        script_assert(_is_arr(t), "second argument must be a series")
        script_assert(_is_arr(tgt), "third argument must be a series")
        script_assert(a in ("eq", "gt", "ge", "lt", "le"), "invalid method value")
        s = list(range(len(e)))
        J.a_sort(JSArray(s), lambda x, y: J.sub(J.get(e, x), J.get(e, y)))  # stable, like V8
        s = J.a_sort(JSArray(range(len(e))), lambda x, y: J.sub(J.get(e, x), J.get(e, y)))
        o = [J.get(t, k) for k in s]
        c = [J.get(e, k) for k in s]
        l = J.get(tgt, 0)
        u = next((k for k, v in enumerate(c) if J.ge(v, l)), -1)
        if u < 0:
            return JSArray([None] * len(tgt))
        if a in ("gt", "ge") and u > 0:
            u -= 1
        d = c[u:]
        p = libraries.BSB[a]
        cmp = lambda x, y: J.sub(x, y)  # noqa: E731
        M = [None] * len(tgt)
        for k, v in enumerate(d):
            idx = p(tgt, v, cmp)
            if 0 <= idx < len(tgt):
                src = u + k
                if M[idx] is not None and J.truthy(merge):
                    M[idx] = merge(M[idx], o[src])
                else:
                    M[idx] = o[src]
        return JSArray(M)

    def cut_series(e=undefined, t=0, a=None, *_):
        if t is undefined:
            t = 0
        if a is undefined:
            a = None
        script_assert(_is_arr(e), "first argument must be a series")
        if J.lt(t, 0):
            t = J.add(t, n)
        script_assert(not J.isNaN(t) and J.ge(t, 0), "from_index is invalid")
        if J.truthy(a):
            if J.lt(a, 0):
                a = J.add(a, n)
        else:
            a = n
        script_assert(not J.isNaN(a) and J.ge(a, 0), "to_index is invalid")
        out = JSArray(e)
        k = t
        while J.lt(k, a):
            J.set(out, k, None)
            k = J.add(k, 1)
        return out

    def line(e=undefined, t=undefined, a=undefined, i=undefined, s=True, *_):
        if s is undefined:
            s = True
        script_assert(not J.isNaN(e) and J.ge(e, 0) and J.lt(e, n), "from_index is invalid")
        script_assert(not J.isNaN(a) and J.ge(a, 0) and J.lt(a, n), "to_index is invalid")
        script_assert(J.gt(a, e), "to_index must be greater than from_index")
        script_assert(not J.isNaN(t), "from_price is invalid")
        script_assert(not J.isNaN(i), "to_price is invalid")
        o = J.div(J.sub(i, t), J.sub(a, e))
        out = JSArray([None] * n)
        last = n - 1 if J.truthy(s) else a
        k = e
        while J.le(k, last):
            J.set(out, k, J.add(t, J.mul(o, J.sub(k, e))))
            k = J.add(k, 1)
        return out

    tzname = J.get(ctx.session, "timezone")

    def time_of(e=undefined, *_):
        script_assert(not J.isNaN(e) and J.ge(e, 0), "invalid time stamp")
        d = _dt.datetime.fromtimestamp(J.to_number(e), ZoneInfo(tzname))
        iso = d.isocalendar()
        return JSObject(minutes=d.minute, hours=d.hour, dayOfMonth=d.day, dayOfWeek=iso[2],
                        dayOfYear=d.timetuple().tm_yday, weekOfYear=iso[1], month=d.month - 1,
                        quarter=(d.month - 1) // 3 + 1, year=d.year)

    def session_of(e=undefined, t="D", sess=None, fmt="DD/MM/YYYY", *_):
        from app.indicators.trendspider_store._runtime import sessions

        script_assert(not J.isNaN(e) and J.ge(e, 0), "invalid time stamp")
        t = "D" if t is undefined else t
        fmt = "DD/MM/YYYY" if fmt is undefined else fmt
        # engine: new Resolution(t, session || extendedSession || session)
        sess = sess if J.truthy(sess) else ctx.ext_session
        start_ms = sessions.bar_at(J.to_str(t), sess, J.to_number(e) * 1000)
        if start_ms is None:
            return JSObject(session="unknown", sessionStartsAt=0)
        m = libraries.Moment.tz(start_ms, J.get(sess, "timezone"))
        return JSObject(session=m.format(fmt), sessionStartsAt=start_ms / 1000)

    def time_difference(e=undefined, t=undefined, *_):
        script_assert(not J.isNaN(e) and J.ge(e, 0) and J.lt(e, 1e12), "the first time stamp is invalid")
        script_assert(not J.isNaN(t) and J.ge(t, 0) and J.lt(t, 1e12), "the second time stamp is invalid")
        script_assert(J.gt(t, e), "toTimestamp must be greater than fromTimestamp")
        return libraries.duration_breakdown((J.to_number(t) - J.to_number(e)) * 1000)

    # ---- inputs -----------------------------------------------------------------
    user = ctx.inputs

    def _new_input(spec):
        script_assert(not any(x.get("id") == spec["id"] for x in S["inputs"]),
                      f'input(): Input parameter named "{spec["title"]}" already exists')
        S["inputs"].append(spec)

    def make_input_api(prefix):
        """input.* functions; inside input.group()/tab()/row() ids are prefixed
        "<container id>__<input id>", as TrendSpider does."""

        def pid(i):
            return f"{prefix}__{i}" if prefix else i

        def input_(e=undefined, t=0, opts=None, *_):
            if t is undefined:
                t = 0
            if opts is undefined:
                opts = None
            script_assert(isinstance(e, str) and e.strip(), "input(): input name is missing or incorrect")
            script_assert(len(e) < 30, "input(): name is too lengthy")
            s = pid(id_from_humanized(e))
            script_assert(not any(x.get("id") == s for x in S["inputs"]), f'input(): Input parameter named "{e}" already exists')
            kind = "select" if (_is_arr(opts) and len(opts) > 0) else "number"
            if kind == "number":
                script_assert(J.is_number(t), f'input(): Default value for "{e}" must be a number')
                script_assert(not J.truthy(opts) or isinstance(opts, dict), "input(): options must be an object for numeric inputs")
                o = opts if J.truthy(opts) else JSObject()
                S["inputs"].append(JSObject(id=s, title=e, type="number",
                                            min=o.get("min") if J.truthy(o.get("min", undefined)) else 0,
                                            max=o.get("max") if J.truthy(o.get("max", undefined)) else 300,
                                            hidden=J.truthy(o.get("hidden", undefined)),
                                            hideInLegend=J.truthy(o.get("hide_in_legend", undefined)), value=t))
            else:
                script_assert(isinstance(t, str) or J.is_number(t), f'input(): Default value for "{e}" must be a string or a number')
                script_assert(any(J.seq(x, t) for x in opts), "input(): default value must be available in a list of options")
                S["inputs"].append(JSObject(id=s, title=e, type="select_wide",
                                            options=JSArray(JSObject(value=x, title=J.to_str(x)) for x in opts), value=t))
            v = user.get(s, undefined)
            if J.seq(v, 0):
                return 0
            return v if J.truthy(v) else t

        def input_number(e=undefined, t=0, opts=None, *_):
            if t is undefined:
                t = 0
            script_assert(J.is_number(t), f'input.number(): The default value for "{e}" must be a number')
            script_assert(not J.truthy(opts) or isinstance(opts, dict), "input.number(): options must be an object")
            return input_(e, t, opts)

        def input_text(e=undefined, t="", opts=None, *_):
            if t is undefined:
                t = ""
            opts = JSObject() if not isinstance(opts, dict) else opts
            script_assert(isinstance(t, str), f'input.text(): The default value for "{e}" must be a text')
            script_assert(isinstance(e, str) and e.strip(), "input(): input name is missing or incorrect")
            script_assert(len(e) < 30, "input(): name is too lengthy")
            s = pid(id_from_humanized(e))
            _new_input(JSObject(id=s, title=e, type="text", value=t, hideInLegend=J.truthy(opts.get("hide_in_legend", undefined))))
            v = user.get(s, undefined)
            return 0 if J.seq(v, 0) else (v if J.truthy(v) else t)

        def input_select(e=undefined, t=undefined, opts=None, *_):
            script_assert(e != "offset", "input.select(): Cant use reserved word as a title")
            script_assert(_is_arr(opts) and len(opts) > 0, "input.select(): options must be a non-empty array")
            script_assert(any(J.seq(x, t) for x in opts), "input.select(): The default value must be available in a list of options")
            return input_(e, t, opts)

        def input_symbol(e=undefined, t="SPY", opts=None, *_):
            if t is undefined:
                t = "SPY"
            opts = JSObject() if not isinstance(opts, dict) else opts
            script_assert(e != "offset", "input.symbol(): Cant use reserved word as a title")
            script_assert(isinstance(t, str), f'input.symbol(): The default value for "{e}" must be a string')
            sid = pid(f"sym-{id_from_humanized(e)}")
            script_assert(not any(x.get("id") == sid for x in S["inputs"]), f'input.symbol(): An input parameter named "{e}" already exists')
            S["inputs"].append(JSObject(id=sid, title=e, type="symbol-search", value=t,
                                        hideInLegend=J.truthy(opts.get("hide_in_legend", undefined))))
            v = user.get(sid, undefined)
            return v if J.truthy(v) else t

        def input_color(e=undefined, t="black", opts=None, *_):
            if t is undefined:
                t = "black"
            script_assert(e != "offset", "input.color(): Cant use reserved word as a title")
            script_assert(isinstance(t, str), f'input.color(): The default value for "{e}" must be a string')
            s = pid(id_from_humanized(e))
            script_assert(not any(x.get("id") == s for x in S["inputs"]), f'input.color(): An input parameter named "{e}" already exists')
            S["inputs"].append(JSObject(id=s, title=e, type="color", hideInLegend=True, value=t))
            v = user.get(s, undefined)
            return v if J.truthy(v) else t

        def input_boolean(e=undefined, t=True, opts=None, *_):
            if t is undefined:
                t = True
            opts = JSObject() if not isinstance(opts, dict) else opts
            script_assert(e != "offset", "input.color(): Cant use reserved word as a title")
            script_assert(isinstance(t, bool), f'input.boolean(): The default value for "{e}" must be boolean')
            s = pid(id_from_humanized(e))
            script_assert(not any(x.get("id") == s for x in S["inputs"]), f'input.boolean(): An input parameter named "{e}" already exists')
            S["inputs"].append(JSObject(id=s, title=e, type="boolean", value=t,
                                        hideInLegend=J.truthy(opts.get("hide_in_legend", undefined))))
            return user[s] if s in user else t

        def container(kind, tag):
            def make(e=undefined, *_):
                if kind == "row":
                    rows[0] += 1
                    cid = pid(f"r-{rows[0] - 1}")
                else:
                    script_assert(isinstance(e, str) and e.strip(), f"input.{kind}(): {kind} name is missing or incorrect")
                    cid = pid(f"{tag}-{id_from_humanized(e)}")
                    script_assert(cid not in containers, f'input.{kind}(): A {kind} named "{e}" already exists')
                    containers.add(cid)
                return JSObject(make_input_api(cid))

            return make

        rows = [0]
        return {"input": input_, "number": input_number, "text": input_text, "select": input_select,
                "symbol": input_symbol, "color": input_color, "boolean": input_boolean,
                "group": container("group", "g"), "row": container("row", "r"), "tab": container("tab", "t")}

    containers = set()

    def input_anchor(e="highest high", t=20, *_):
        # engine createAnchoringInputs + findAnchorCandlesSync (non-continuous)
        e = "highest high" if e is undefined else e
        t = 20 if t is undefined else t
        types = ["date", "highest vol.", "highest high", "lowest low", "day to date", "week to date",
                 "month to date", "qtr to date", "year to date", "visible range"]
        script_assert(e in types, f'Unknown anchoring type: "{e}"')
        specs = [JSObject(id="anchoring_type", title="Anchor to", type="select_wide",
                          options=JSArray(JSObject(value=v, title=v) for v in types), value=e),
                 JSObject(id="windowSize", title="Window", type="integer", min=1, max=300, value=t)]
        existing = {x.get("id") for x in S["inputs"]}
        script_assert(not any(x["id"] in existing for x in specs), "input_anchor(): Input parameter(s) already exist")
        S["inputs"].extend(specs)
        S["isAnchored"] = True
        kind = user.get("anchoring_type", e)
        window = user.get("windowSize", t)
        idx = _find_anchor(kind, window)
        if idx is None or idx < 0:
            return None
        return JSObject(candleIndex=idx, candleIndexFrom=idx, candleIndexTo=n - 1)

    def _find_anchor(kind, window):
        dec = int(si.get("decimals", 2))
        if kind in ("highest high", "lowest low", "highest vol."):
            src = {"highest high": H, "lowest low": Lo, "highest vol.": V}[kind]
            fn = J._max if kind != "lowest low" else J._min
            half = int(J.js_round(J.to_number(window) / 2))
            for k in range(n - 1 - half, half - 1, -1):
                ext = fn(*src[k - half: k + half + 1])
                if J.truthy(ext) and J.truthy(src[k]) and J.n_toFixed(ext, dec) == J.n_toFixed(src[k], dec):
                    return k
            return None
        period = {"day to date": "D", "week to date": "W", "month to date": "M", "qtr to date": "Q",
                  "year to date": "Y"}.get(kind)
        if period is None:
            raise J.Unsupported(f'input_anchor(): anchoring type "{kind}" is not ported')
        if period == "D" and not ctx.resolution.isdigit():
            return None
        fmt = {"D": "DD MMM", "W": "WW YYYY", "M": "MMM YYYY", "Q": "Q YYYY", "Y": "YYYY"}[period]
        from app.indicators.trendspider_store._runtime import sessions

        def label(ts):
            b = sessions.bar_at("D", ctx.ext_session, ts * 1000)
            return libraries.Moment.tz(b, J.get(ctx.ext_session, "timezone")).format(fmt) if b is not None else "XXX"

        for k in range(n - 1, 0, -1):
            if label(T[k - 1]) != label(T[k]):
                return k
        return None

    _root = make_input_api(None)
    input_obj = J._Callable(_root["input"], number=_root["number"], text=_root["text"], select=_root["select"],
                            symbol=_root["symbol"], color=_root["color"], boolean=_root["boolean"], anchor=input_anchor,
                            group=_root["group"], tab=_root["tab"], row=_root["row"])

    # ---- request ----------------------------------------------------------------
    calls = {"history": 0, "other": 0}

    def history(ticker=undefined, resolution=undefined, opts=undefined, *_):
        opts = JSObject() if opts is undefined else opts
        script_assert(J.truthy(ticker) and isinstance(ticker, str) and len(ticker) < 120, "invalid ticker")
        script_assert(J.truthy(resolution), "invalid resolution")
        script_assert(not any(not (isinstance(v, (str, bool)) or J.is_number(v)) for v in opts.values()),
                      "invalid data type usage in options")
        ct = opts.get("chartType", undefined)
        script_assert(not J.truthy(ct) or ct in ("candles", "rainfall", "heikinashi"), "invalid chart type requested")
        script_assert(calls["history"] < 16, "too many calls for history, only 16 allowed")
        calls["history"] += 1
        if ctx.provider is None:
            raise J.Unsupported("request.history() needs a data provider")
        o = ctx.provider.history(ticker, J.to_str(resolution).upper(), ext_session=J.truthy(opts.get("ext_session", undefined)),
                                 chart_type=J.to_str(opts.get("chart_type", "candles")) if opts.get("chart_type", undefined) is not undefined else "candles",
                                 base=ctx)
        o = J.from_python(o)
        script_assert(not J.truthy(J.get(o, "error")), f"error obtaining history: {J.to_str(J.get(o, 'error'))}")
        for k in ("time", "open", "high", "low", "close"):
            script_assert(_is_arr(J.get(o, k)), f"wrong history format (.{k})")
        if J.truthy(opts.get("land_onto_current_candles", undefined)):
            return JSObject(time=T, open=land_points_onto_series(o["time"], o["open"], T),
                            high=land_points_onto_series(o["time"], o["high"], T),
                            low=land_points_onto_series(o["time"], o["low"], T),
                            close=land_points_onto_series(o["time"], o["close"], T))
        return o

    calls["http"] = 0

    def alt_data(kind):
        # Mirrors the engine's request.* wrappers: call limits (6 http calls,
        # 6 other alternative-data calls; options_schedule is unmetered),
        # error checks, and options_schedule's ms -> s timestamp conversion.
        def f(*args):
            if kind == "http":
                url = args[0] if args else undefined
                script_assert(J.truthy(url) and isinstance(url, str), "'url must be a string")
                script_assert(url.startswith("https://"), "'url must start from \"https://\"")
                script_assert(calls["http"] < 6, "too many calls for http, only 6 allowed")
                calls["http"] += 1
            elif kind == "options_data_for_expiration":
                tk, exp = (args + (undefined, undefined))[:2]
                metrics = args[2] if len(args) > 2 and args[2] is not undefined else JSArray(["oi", "l"])
                script_assert(J.truthy(tk) and isinstance(tk, str) and len(tk) < 120, "invalid ticker")
                script_assert(len(J.to_str(exp)) == 6, "wrong expiration date format. use YYMMDD")
                script_assert(_valid_yymmdd(J.to_str(exp)), "invalid expiration date value")
                bad = [m for m in metrics if J.to_str(J.get(m, "toLowerCase")()) not in OPTION_METRICS]
                script_assert(not bad, f"invalid metrics requested: {', '.join(J.to_str(b) for b in bad)}")
            elif kind == "options_data_for_all_expirations":
                tk = args[0] if args else undefined
                strikes = args[1] if len(args) > 1 and args[1] is not undefined else 6
                metrics = args[2] if len(args) > 2 and args[2] is not undefined else JSArray(["oi", "l"])
                otype = args[3] if len(args) > 3 and args[3] is not undefined else "all"
                script_assert(J.truthy(tk) and isinstance(tk, str) and len(tk) < 120, "invalid ticker")
                script_assert(J.truthy(strikes) and J.lt(strikes, 41), "invalid amount of strikes requested")
                script_assert(otype in ("P", "C", "all"), "invalid optionTypes")
                bad = [m for m in metrics if J.to_str(J.get(m, "toLowerCase")()) not in OPTION_METRICS]
                script_assert(not bad, f"invalid metrics requested: {', '.join(J.to_str(b) for b in bad)}")
            elif kind == "options_schedule":
                tk = args[0] if args else undefined
                script_assert(J.truthy(tk) and isinstance(tk, str) and len(tk) < 120, "invalid ticker")
            if kind not in ("http", "options_schedule"):
                script_assert(calls["other"] < 6, "too many calls for alternative data, only 6 allowed")
                calls["other"] += 1
            if ctx.provider is None or not hasattr(ctx.provider, "alt_data"):
                raise J.Unsupported(f"request.{kind}() needs an alternative-data provider")
            res = J.from_python(ctx.provider.alt_data(kind, *[_py(a) for a in args]))
            if kind in ("http", "fundamental", "options_schedule", "options_data_for_expiration",
                        "options_data_for_all_expirations"):
                err = J.get(res, "error") if isinstance(res, dict) else undefined
                label = {"http": "http data", "fundamental": "fundamentals", "options_schedule": "options schedule"}.get(kind, "options data")
                script_assert(not J.truthy(err), f"error obtaining {label}: {J.to_str(err)}")
            if kind == "options_schedule":
                script_assert(_is_arr(res), "wrong schedule format: not an array")
                for e in res:
                    ex = J.get(e, "expiration")
                    J.set(ex, "timestamp", J.js_round(J.div(J.get(ex, "timestamp"), 1000)))
            return res

        return f

    request = JSObject(history=history)
    request["security"] = history
    for kind in ("analyst_ratings", "crypto_fear", "dark_pool", "dividends", "earnings", "fred_series", "insider_trading",
                 "market_breadth", "splits", "news", "retail_trading", "relative_performance", "short_volume",
                 "unusual_options", "options_schedule", "options_data_for_expiration", "options_data_for_all_expirations",
                 "congress_trading", "wallstreetbets", "seasonality", "fundamental", "http", "fundamental_distribution"):
        request[kind] = alt_data(kind)

    # ---- constants / current ------------------------------------------------------
    now_s = ctx.now if ctx.now is not None else int(T[-1]) if n else 0
    si = ctx.symbol_info
    constants = JSObject(
        now=now_s, resolution=ctx.resolution, chart_type="candles", decimals=si.get("decimals", 2), ticker=ctx.ticker,
        session=ctx.session, ext_session=ctx.ext_session, ext_session_premarket=PRE_SESSION,
        ext_session_postmarket=POST_SESSION, empty_series=JSArray([None] * n),
        price_source_options=JSArray(PRICE_SOURCE_OPTIONS), time_frames=JSArray(TIME_FRAMES),
        ma_types=JSArray(MA_TYPES), band_types=JSArray(["ATR", "St.Dev.", "Constant", "Percentage"]), icons=JSObject(ICONS),
    )
    current = JSObject(
        time=now_s, resolution=ctx.resolution, chart_type="candles", decimals=si.get("decimals", 2),
        ticker=ctx.ticker, symbol=ctx.ticker, session=ctx.session, ext_session=ctx.ext_session,
        ext_session_premarket=PRE_SESSION, ext_session_postmarket=POST_SESSION,
        industry=si.get("industry", undefined), sector=si.get("sector", undefined), assetType=si.get("type", "stock"),
        volumeDataAvailable=True, contractSize=undefined, futuresRoot=si.get("root", ctx.ticker), root=si.get("root", ctx.ticker),
        assets_involved=JSArray([si.get("root", ctx.ticker)]), expiration=0, strike=undefined, option_type=undefined,
        is_ext_hours=False,
    )

    F.update(
        assert_=None,
        sub=fold(lambda a, b: J.sub(a, b)),
        add=fold(lambda a, b: J.add(a, b)),
        div=lambda t=undefined, o=undefined, *_: pairwise(lambda a, b: J.div(a, b), t, o),
        mult=fold(lambda a, b: J.mul(a, b)),
        max_of=fold(lambda a, b: J._max(a, b)),
        min_of=fold(lambda a, b: J._min(a, b)),
        horizontal_line=horizontal_line,
        series_of=series_of,
        sliding_window_function=sliding_window_function,
        shift=shift,
        for_every=for_every,
        describe_indicator=describe_indicator,
        input=input_obj,
        input_anchor=input_anchor,
        library=lambda name=undefined, *_: libraries.get_library(name),
        paint=paint,
        color_candles=color_candles,
        fill=fill,
        paint_label_at_line=paint_label_at_line,
        paint_overlay=paint_overlay,
        paint_projection=paint_projection,
        register_signal=register_signal,
        interpolate_sparse_series=interpolate_sparse_series,
        indexed_points_of=indexed_points_of,
        land_points_onto_series=land_points_onto_series,
        cut_series=cut_series,
        line=line,
        time_of=time_of,
        session_of=session_of,
        time_difference=time_difference,
        request=request,
        console=J.console,
        constants=constants,
        current=current,
    )
    del F["assert_"]
    F["assert"] = lambda cond=undefined, msg=undefined, *_: (
        None if J.truthy(cond) else (_ for _ in ()).throw(J.JSError(J.make_error(msg if J.truthy(msg) else "Indicator logic assertion failed")))
    )
    F["bar_at"] = session_of
    F["plot"] = paint
    F["alertcondition"] = register_signal
    F["pivot_high"] = lambda e=undefined, t=undefined, nn=undefined, *_: F["fractal_high"](e, J.add(J.add(t, nn), 1), t)
    F["pivot_low"] = lambda e=undefined, t=undefined, nn=undefined, *_: F["fractal_low"](e, J.add(J.add(t, nn), 1), t)

    indicators = JSObject()
    F["indicators"] = indicators
    for k, f in C_.items():
        F[k] = f
        indicators[k] = f

    from app.indicators.trendspider_store._runtime import builtins as B

    B.install(F, indicators)
    for name in BANNED:
        F[name] = (lambda nm: lambda *_: (_ for _ in ()).throw(J.JSError(J.make_error(f'Function "{nm}" can\'t be used'))))(name)
    return F


def make_globals(ctx: ScriptContext, res: ScriptResult) -> dict:
    """Script scope: the API object first (it's `with (api)`), then JS globals."""
    api = build_api(ctx, res)
    g = _Globals(J.BUILTINS)
    g.update(api)
    return g


class _Globals(dict):
    def __missing__(self, key):
        return undefined


def run_script(script_fn, ctx: ScriptContext) -> ScriptResult:
    res = ScriptResult()
    g = make_globals(ctx, res)
    script_fn(g)
    return res
