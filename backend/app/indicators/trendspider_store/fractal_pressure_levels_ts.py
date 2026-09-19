"""
Fractal Pressure + Levels -- TrendSpider store indicator by Christian Park.

Registered as "fractal_pressure_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68abe2-fractal-pressure-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_candles = G["candles"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_plot = G["plot"]
    def atr_series(len=J.undefined, *_args):
        prevC = None
        def _f1(h=J.undefined, l=J.undefined, c=J.undefined, *_args):
            nonlocal prevC
            a = J.sub(h, l)
            b = (a if (prevC is None) else J.get(G_Math, "abs")(J.sub(h, prevC)))
            d = (a if (prevC is None) else J.get(G_Math, "abs")(J.sub(l, prevC)))
            trv = a
            if J.gt(b, trv):
                trv = b
            if J.gt(d, trv):
                trv = d
            prevC = c
            return trv
        tr = G_for_every(G_high, G_low, G_close, _f1)
        return G_ema(tr, len)
    def lastFractalHigh(span=J.undefined, *_args):
        buf = J.JSArray([])
        lastHi = None
        def _f1(h=J.undefined, *_args):
            nonlocal lastHi
            c = J.undefined
            mid = J.undefined
            isHi = J.undefined
            i = J.undefined
            J.get(buf, "push")(h)
            if J.gt(J.get(buf, "length"), J.add(J.mul(2, span), 1)):
                J.get(buf, "shift")()
            if J.seq(J.get(buf, "length"), J.add(J.mul(2, span), 1)):
                c = span
                mid = J.get(buf, c)
                isHi = True
                i = 0
                while J.lt(i, J.get(buf, "length")):
                    if (J.sne(i, c) and J.gt(J.get(buf, i), mid)):
                        isHi = False
                        break
                    i = J.inc(i)
                if J.truthy(isHi):
                    lastHi = mid
            return (None if (lastHi is None) else lastHi)
        return G_for_every(G_high, _f1)
    def lastFractalLow(span=J.undefined, *_args):
        buf = J.JSArray([])
        lastLo = None
        def _f1(l=J.undefined, *_args):
            nonlocal lastLo
            c = J.undefined
            mid = J.undefined
            isLo = J.undefined
            i = J.undefined
            J.get(buf, "push")(l)
            if J.gt(J.get(buf, "length"), J.add(J.mul(2, span), 1)):
                J.get(buf, "shift")()
            if J.seq(J.get(buf, "length"), J.add(J.mul(2, span), 1)):
                c = span
                mid = J.get(buf, c)
                isLo = True
                i = 0
                while J.lt(i, J.get(buf, "length")):
                    if (J.sne(i, c) and J.lt(J.get(buf, i), mid)):
                        isLo = False
                        break
                    i = J.inc(i)
                if J.truthy(isLo):
                    lastLo = mid
            return (None if (lastLo is None) else lastLo)
        return G_for_every(G_low, _f1)
    def __edgeRise_(series=J.undefined, *_args):
        prev = 0
        def _f1(v=J.undefined, *_args):
            nonlocal prev
            fire = (1 if (J.seq(prev, 0) and J.seq(v, 1)) else None)
            prev = v
            return fire
        return G_for_every(series, _f1)
    G_describe_indicator("Fractal Pressure + Levels (#TSBuild25)")
    Span = J.get(G_input, "number")("Fractal span (L/R)", 2, J.obj(("min", 2), ("max", 5)))
    AtrLen = J.get(G_input, "number")("ATR length", 14, J.obj(("min", 5), ("max", 200)))
    Smooth = J.get(G_input, "number")("Osc smoothing", 3, J.obj(("min", 0), ("max", 20)))
    ViewSm = J.get(G_input, "number")("View smoothing", 5, J.obj(("min", 0), ("max", 30)))
    EPS = 1.0e-9
    fHigh = lastFractalHigh(Span)
    fLow = lastFractalLow(Span)
    atrS = atr_series(AtrLen)
    def _f1(r=J.undefined, c=J.undefined, *_args):
        return (None if (J.nullish(r)) else J.get(G_Math, "max")(J.sub(r, c), 0))
    dRes = G_for_every(fHigh, G_close, _f1)
    def _f2(s=J.undefined, c=J.undefined, *_args):
        return (None if (J.nullish(s)) else J.get(G_Math, "max")(J.sub(c, s), 0))
    dSup = G_for_every(fLow, G_close, _f2)
    def _f3(d=J.undefined, a=J.undefined, *_args):
        return (J.div(d, a) if (J.truthy(a) and J.gt(a, EPS)) else 0)
    nRes = G_for_every(dRes, atrS, _f3)
    def _f4(d=J.undefined, a=J.undefined, *_args):
        return (J.div(d, a) if (J.truthy(a) and J.gt(a, EPS)) else 0)
    nSup = G_for_every(dSup, atrS, _f4)
    def _f5(u=J.undefined, d=J.undefined, *_args):
        up = (_t1 if J.truthy(_t1 := u) else 0)
        down = (_t2 if J.truthy(_t2 := d) else 0)
        return J.div(J.sub(down, up), J.add(J.add(down, up), EPS))
    rawTilt = G_for_every(nRes, nSup, _f5)
    tiltSm = (G_ema(rawTilt, Smooth) if J.gt(Smooth, 0) else rawTilt)
    def _f6(v=J.undefined, *_args):
        x = v
        if J.gt(x, 1):
            x = 1
        if J.lt(x, (-1)):
            x = (-1)
        return J.mul(J.add(x, 1), 50)
    tilt01 = G_for_every(tiltSm, _f6)
    tiltView = (G_ema(tilt01, ViewSm) if J.gt(ViewSm, 0) else tilt01)
    G_plot(fHigh, J.obj(("name", "__fp_res"), ("color", "#d07a7a")))
    G_plot(fLow, J.obj(("name", "__fp_sup"), ("color", "#5bb39b")))
    def _f7(__=J.undefined, *_args):
        return 50
    g50 = G_for_every(G_close, _f7)
    def _f8(__=J.undefined, *_args):
        return 60
    g60 = G_for_every(G_close, _f8)
    def _f9(__=J.undefined, *_args):
        return 40
    g40 = G_for_every(G_close, _f9)
    G_plot(g50, J.obj(("name", "__fp_g50"), ("color", "#666666")))
    G_plot(g60, J.obj(("name", "__fp_g60"), ("color", "#3f63cc")))
    G_plot(g40, J.obj(("name", "__fp_g40"), ("color", "#b94b4b")))
    G_plot(tiltView, J.obj(("name", "__fp_tilt"), ("color", "#dddddd")))
    def _f10(r=J.undefined, s=J.undefined, *_args):
        return (None if ((J.nullish(r)) or (J.nullish(s))) else J.get(G_Math, "max")(J.sub(r, s), 0))
    __fp_bandWidth_ = G_for_every(fHigh, fLow, _f10)
    def _f11(w=J.undefined, a=J.undefined, *_args):
        return (J.div(w, a) if (J.truthy(a) and J.gt(a, EPS)) else None)
    __fp_coilRaw_ = G_for_every(__fp_bandWidth_, atrS, _f11)
    __fp_coilSmooth_ = (G_ema(__fp_coilRaw_, ViewSm) if J.gt(ViewSm, 0) else __fp_coilRaw_)
    G_plot(__fp_coilSmooth_, J.obj(("name", "__fp_coil"), ("color", "#999999")))
    def _f12(c=J.undefined, r=J.undefined, *_args):
        return (0 if (J.nullish(r)) else (1 if J.gt(c, r) else 0))
    __fp_above_ = G_for_every(G_close, fHigh, _f12)
    def _f13(c=J.undefined, s=J.undefined, *_args):
        return (0 if (J.nullish(s)) else (1 if J.lt(c, s) else 0))
    __fp_below_ = G_for_every(G_close, fLow, _f13)
    __fp_upEdge_ = __edgeRise_(__fp_above_)
    __fp_dnEdge_ = __edgeRise_(__fp_below_)
    def _f14(f=J.undefined, c=J.undefined, *_args):
        return (c if J.truthy(f) else None)
    __fp_upY_ = G_for_every(__fp_upEdge_, G_close, _f14)
    def _f15(f=J.undefined, c=J.undefined, *_args):
        return (c if J.truthy(f) else None)
    __fp_dnY_ = G_for_every(__fp_dnEdge_, G_close, _f15)
    G_plot(__fp_upY_, J.obj(("name", "__fp_up"), ("color", "#4cc38a")))
    G_plot(__fp_dnY_, J.obj(("name", "__fp_dn"), ("color", "#e25555")))
    def _f16(u=J.undefined, d=J.undefined, *_args):
        return ("#22c55e" if J.truthy(u) else ("#ef4444" if J.truthy(d) else None))
    __fp_barColor_ = G_for_every(__fp_upEdge_, __fp_dnEdge_, _f16)
    G_paint(G_candles, J.obj(("color", __fp_barColor_)))
    def _f17(v=J.undefined, *_args):
        return (1 if J.gt(v, 60) else 0)
    __fp_tiltHi_ = G_for_every(tiltView, _f17)
    def _f18(v=J.undefined, *_args):
        return (1 if J.lt(v, 40) else 0)
    __fp_tiltLo_ = G_for_every(tiltView, _f18)
    def _f19(v=J.undefined, *_args):
        return (1 if ((not J.nullish(v)) and J.lt(v, 0.6)) else 0)
    __fp_coilLow_ = G_for_every(__fp_coilSmooth_, _f19)
    def _f20(c=J.undefined, t=J.undefined, *_args):
        return (1 if (J.truthy(c) and J.truthy(t)) else None)
    __fp_longSetup_ = G_for_every(__fp_coilLow_, __fp_tiltHi_, _f20)
    def _f21(c=J.undefined, t=J.undefined, *_args):
        return (1 if (J.truthy(c) and J.truthy(t)) else None)
    __fp_shortSetup_ = G_for_every(__fp_coilLow_, __fp_tiltLo_, _f21)
    G_plot(__fp_longSetup_, J.obj(("name", "__fp_longSet"), ("color", "#4cc38a")))
    G_plot(__fp_shortSetup_, J.obj(("name", "__fp_shortSet"), ("color", "#e25555")))


register_store_indicator(
    script,
    name='fractal_pressure_levels_TS',
    title='Fractal Pressure + Levels',
    developer='Christian Park',
    url='https://trendspider.com/trading-tools-store/indicators/68abe2-fractal-pressure-levels/',
    position='price',
    inputs=[{'id': 'fractal_span__l_r_', 'title': 'Fractal span (L/R)', 'type': 'number', 'default': 2}, {'id': 'atr_length', 'title': 'ATR length', 'type': 'number', 'default': 14}, {'id': 'osc_smoothing', 'title': 'Osc smoothing', 'type': 'number', 'default': 3}, {'id': 'view_smoothing', 'title': 'View smoothing', 'type': 'number', 'default': 5}],
    outputs=['__fp_res', '__fp_sup', '__fp_g50', '__fp_g60', '__fp_g40', '__fp_tilt', '__fp_coil', '__fp_up', '__fp_dn', 'line_10', '__fp_longset', '__fp_shortset'],
    signals=[],
    requires=[],
    parity='exact',
)
