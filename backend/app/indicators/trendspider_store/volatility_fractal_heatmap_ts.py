"""
Volatility Fractal Heatmap -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "volatility_fractal_heatmap_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a603-volatility-fractal-heatmap/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_time = G["time"]
    def colorFromHeat(h=J.undefined, *_args):
        if (J.nullish(h)):
            return None
        t = clamp01(J.div(J.get(G_Math, "min")(3, J.get(G_Math, "max")(0, h)), 3))
        midT = (J.div(t, 0.5) if J.lt(t, 0.5) else J.div(J.sub(t, 0.5), 0.5))
        if J.lt(t, 0.5):
            c1 = J.JSArray([198, 197, 197])
            c2 = J.JSArray([255, 165, 0])
            r = lerp(J.get(c1, 0), J.get(c2, 0), midT)
            g = lerp(J.get(c1, 1), J.get(c2, 1), midT)
            b = lerp(J.get(c1, 2), J.get(c2, 2), midT)
            return J.get(J.template("#", J.get(J.get(J.get(G_Math, "round")(r), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(g), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(b), "toString")(16), "padStart")(2, "0")), "toUpperCase")()
        else:
            c1_2 = J.JSArray([255, 165, 0])
            c2_2 = J.JSArray([255, 45, 45])
            r_2 = lerp(J.get(c1_2, 0), J.get(c2_2, 0), midT)
            g_2 = lerp(J.get(c1_2, 1), J.get(c2_2, 1), midT)
            b_2 = lerp(J.get(c1_2, 2), J.get(c2_2, 2), midT)
            return J.get(J.template("#", J.get(J.get(J.get(G_Math, "round")(r_2), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(g_2), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(b_2), "toString")(16), "padStart")(2, "0")), "toUpperCase")()
    G_describe_indicator("Volatility Fractal Heatmap #TSBuild25", "price", J.obj(("shortName", "VF Heatmap"), ("decimals", 2)))
    grpCore = "① Core"
    grpBand = "② Bands"
    grpDisp = "③ Display"
    lenS = J.get(G_input, "number")("Short ATR Len", 10, J.obj(("min", 2), ("step", 1), ("group", grpCore)))
    lenM = J.get(G_input, "number")("Mid ATR Len", 21, J.obj(("min", 2), ("step", 1), ("group", grpCore)))
    lenL = J.get(G_input, "number")("Long ATR Len", 50, J.obj(("min", 2), ("step", 1), ("group", grpCore)))
    zWin = J.get(G_input, "number")("Z-Score Window", 200, J.obj(("min", 50), ("step", 10), ("group", grpCore)))
    smooth = J.get(G_input, "number")("Heat Smooth", 5, J.obj(("min", 1), ("step", 1), ("group", grpCore)))
    bandMult = J.get(G_input, "number")("Band Mult (ATR-blend)", 1.5, J.obj(("min", 0.1), ("step", 0.1), ("group", grpBand)))
    showBands = J.get(G_input, "boolean")("Show Bands", True, J.obj(("group", grpBand)))
    pressureZ = J.get(G_input, "number")("Pressure Z Threshold", 1.25, J.obj(("min", 0.5), ("step", 0.05), ("group", grpDisp)))
    showDots = J.get(G_input, "boolean")("Show Pressure Dots", True, J.obj(("group", grpDisp)))
    def move(s=J.undefined, k=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(s, "length")):
            j = J.sub(i, k)
            J.set(out, i, (J.get(s, j) if J.ge(j, 0) else None))
            i = J.inc(i)
        return out
    def ema_ts(s=J.undefined, length=J.undefined, *_args):
        out = G_series_of(None)
        if J.lt(length, 1):
            return out
        a = J.div(2, J.add(length, 1))
        prev = None
        i = 0
        while J.lt(i, J.get(s, "length")):
            v = J.get(s, i)
            if (J.nullish(v)):
                J.set(out, i, (J.get(out, J.sub(i, 1)) if J.gt(i, 0) else None))
                i = J.inc(i)
                continue
            prev = (v if (J.nullish(prev)) else J.add(J.mul(a, v), J.mul(J.sub(1, a), prev)))
            J.set(out, i, prev)
            i = J.inc(i)
        return out
    def _f1(*_args):
        pc = move(G_close, 1)
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            if J.seq(i, 0):
                J.set(out, i, None)
                i = J.inc(i)
                continue
            a = (J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(G_low, i))) if ((not J.nullish(J.get(G_high, i))) and (not J.nullish(J.get(G_low, i)))) else None)
            b = (J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(pc, i))) if ((not J.nullish(J.get(G_high, i))) and (not J.nullish(J.get(pc, i)))) else None)
            c = (J.get(G_Math, "abs")(J.sub(J.get(G_low, i), J.get(pc, i))) if ((not J.nullish(J.get(G_low, i))) and (not J.nullish(J.get(pc, i)))) else None)
            m = J.get(G_Math, "max")((J.neg(G_Infinity) if J.nullish(_t1 := a) else _t1), (J.neg(G_Infinity) if J.nullish(_t2 := b) else _t2), (J.neg(G_Infinity) if J.nullish(_t3 := c) else _t3))
            J.set(out, i, (None if J.seq(m, J.neg(G_Infinity)) else m))
            i = J.inc(i)
        return out
    trueRange = _f1()
    def atrr(len=J.undefined, *_args):
        return ema_ts(trueRange, len)
    def zscore(s=J.undefined, win=J.undefined, *_args):
        m = G_sma(s, win)
        sd = G_stdev(s, win)
        def _f1(v=J.undefined, mm=J.undefined, ss=J.undefined, *_args):
            if (((((J.nullish(v)) or (J.nullish(mm))) or (J.nullish(ss))) or (not J.truthy(G_isFinite(ss)))) or J.seq(ss, 0)):
                return None
            return J.div(J.sub(v, mm), ss)
        return G_for_every(s, m, sd, _f1)
    def sma_ts(s=J.undefined, n=J.undefined, *_args):
        return G_sma(s, J.get(G_Math, "max")(1, n))
    def clamp01(t=J.undefined, *_args):
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, t))
    def lerp(a=J.undefined, b=J.undefined, t=J.undefined, *_args):
        return J.add(a, J.mul(J.sub(b, a), t))
    atrS = atrr(lenS)
    atrM = atrr(lenM)
    atrL = atrr(lenL)
    zS = zscore(atrS, zWin)
    zM = zscore(atrM, zWin)
    zL = zscore(atrL, zWin)
    def _f2(a=J.undefined, b=J.undefined, c=J.undefined, *_args):
        aa = (0 if (J.nullish(a)) else J.get(G_Math, "abs")(a))
        bb = (0 if (J.nullish(b)) else J.get(G_Math, "abs")(b))
        cc = (0 if (J.nullish(c)) else J.get(G_Math, "abs")(c))
        return J.div(J.add(J.add(aa, bb), cc), 3)
    heatRaw = G_for_every(zS, zM, zL, _f2)
    heat = sma_ts(heatRaw, smooth)
    wS = 1
    wM = 1.2
    wL = 1.5
    def _f3(a=J.undefined, b=J.undefined, c=J.undefined, *_args):
        if (((J.nullish(a)) or (J.nullish(b))) or (J.nullish(c))):
            return None
        return J.div(J.add(J.add(J.mul(wS, a), J.mul(wM, b)), J.mul(wL, c)), J.add(J.add(wS, wM), wL))
    atrBlend = G_for_every(atrS, atrM, atrL, _f3)
    def _f4(c=J.undefined, a=J.undefined, *_args):
        return (J.add(c, J.mul(bandMult, a)) if ((not J.nullish(c)) and (not J.nullish(a))) else None)
    upper = G_for_every(G_close, atrBlend, _f4)
    def _f5(c=J.undefined, a=J.undefined, *_args):
        return (J.sub(c, J.mul(bandMult, a)) if ((not J.nullish(c)) and (not J.nullish(a))) else None)
    lower = G_for_every(G_close, atrBlend, _f5)
    def _f6(h=J.undefined, *_args):
        return colorFromHeat(h)
    candleColors = G_for_every(heat, _f6)
    G_color_candles(candleColors)
    if J.truthy(showBands):
        G_paint(upper, J.obj(("name", "VF Upper"), ("color", "#FF7F50"), ("style", "line"), ("thickness", 1)))
        G_paint(lower, J.obj(("name", "VF Lower"), ("color", "#FF7F50"), ("style", "line"), ("thickness", 1)))
    def _f7(a=J.undefined, b=J.undefined, c=J.undefined, *_args):
        cond = (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := (J.ge(a, pressureZ) if J.truthy(_t3 := (not J.nullish(a))) else _t3)) else (J.ge(b, pressureZ) if J.truthy(_t4 := (not J.nullish(b))) else _t4))) else (J.ge(c, pressureZ) if J.truthy(_t5 := (not J.nullish(c))) else _t5))
        return (G_low if J.truthy(cond) else None)
    press = G_for_every(zS, zM, zL, _f7)
    if J.truthy(showDots):
        G_paint(press, J.obj(("name", "Pressure Dots"), ("color", "#FF007A"), ("style", "dotted"), ("thickness", 3)))
    def _f8(a=J.undefined, b=J.undefined, c=J.undefined, *_args):
        ok = (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := (J.ge(a, pressureZ) if J.truthy(_t3 := (not J.nullish(a))) else _t3)) else (J.ge(b, pressureZ) if J.truthy(_t4 := (not J.nullish(b))) else _t4))) else (J.ge(c, pressureZ) if J.truthy(_t5 := (not J.nullish(c))) else _t5))
        return (True if J.truthy(ok) else False)
    sig_VolPressure = G_for_every(zS, zM, zL, _f8)
    def _f9(c=J.undefined, u=J.undefined, l=J.undefined, *_args):
        if (((J.nullish(c)) or (J.nullish(u))) or (J.nullish(l))):
            return False
        return (_t1 if J.truthy(_t1 := J.ge(c, u)) else J.le(c, l))
    sig_BandTouch = G_for_every(G_close, upper, lower, _f9)
    G_register_signal(sig_VolPressure, "VF: Vol Pressure ≥ Z")
    G_register_signal(sig_BandTouch, "VF: Touch Band")


register_store_indicator(
    script,
    name='volatility_fractal_heatmap_TS',
    title='Volatility Fractal Heatmap',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68a603-volatility-fractal-heatmap/',
    position='price',
    inputs=[{'id': 'short_atr_len', 'title': 'Short ATR Len', 'type': 'number', 'default': 10}, {'id': 'mid_atr_len', 'title': 'Mid ATR Len', 'type': 'number', 'default': 21}, {'id': 'long_atr_len', 'title': 'Long ATR Len', 'type': 'number', 'default': 50}, {'id': 'z_score_window', 'title': 'Z-Score Window', 'type': 'number', 'default': 200}, {'id': 'heat_smooth', 'title': 'Heat Smooth', 'type': 'number', 'default': 5}, {'id': 'band_mult__atr_blend_', 'title': 'Band Mult (ATR-blend)', 'type': 'number', 'default': 1.5}, {'id': 'show_bands', 'title': 'Show Bands', 'type': 'boolean', 'default': True}, {'id': 'pressure_z_threshold', 'title': 'Pressure Z Threshold', 'type': 'number', 'default': 1.25}, {'id': 'show_pressure_dots', 'title': 'Show Pressure Dots', 'type': 'boolean', 'default': True}],
    outputs=['cdl', 'vf_upper', 'vf_lower', 'pressure_dots', 'vf__vol_pressure___z', 'vf__touch_band'],
    signals=['vf__vol_pressure___z', 'vf__touch_band'],
    requires=[],
    parity='exact',
)
