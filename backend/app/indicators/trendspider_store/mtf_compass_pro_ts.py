"""
MTF Compass Pro -- TrendSpider store indicator by Feliks Ba\u0144ka.

Registered as "mtf_compass_pro_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a60d-mtf-compass-pro/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def move(s=J.undefined, k=J.undefined, *_args):
        o = G_series_of(None)
        i = 0
        while J.lt(i, J.get(s, "length")):
            j = J.sub(i, k)
            J.set(o, i, (J.get(s, j) if J.ge(j, 0) else None))
            i = J.inc(i)
        return o
    def lastVal(s=J.undefined, *_args):
        return J.get(s, J.sub(J.get(s, "length"), 1))
    def fmt(x=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 2
        dec = _t2
        return ("—" if (J.nullish(x)) else J.get(G_Number(x), "toFixed")(dec))
    def lerp(a=J.undefined, b=J.undefined, t=J.undefined, *_args):
        return J.add(a, J.mul(J.sub(b, a), t))
    def colorBlend(c1=J.undefined, c2=J.undefined, t=J.undefined, *_args):
        h1 = G_parseInt(J.get(c1, "slice")(1), 16)
        h2 = G_parseInt(J.get(c2, "slice")(1), 16)
        r1 = J.bit_and(J.shr(h1, 16), 255)
        g1 = J.bit_and(J.shr(h1, 8), 255)
        b1 = J.bit_and(h1, 255)
        r2 = J.bit_and(J.shr(h2, 16), 255)
        g2 = J.bit_and(J.shr(h2, 8), 255)
        b2 = J.bit_and(h2, 255)
        r = lerp(r1, r2, t)
        g = lerp(g1, g2, t)
        b = lerp(b1, b2, t)
        return J.get(J.template("#", J.get(J.get(J.get(G_Math, "round")(r), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(g), "toString")(16), "padStart")(2, "0"), J.get(J.get(J.get(G_Math, "round")(b), "toString")(16), "padStart")(2, "0")), "toUpperCase")()
    def normSlope(s=J.undefined, *_args):
        def _f1(c=J.undefined, p=J.undefined, *_args):
            return (J.sub(c, p) if ((not J.nullish(c)) and (not J.nullish(p))) else None)
        d = G_for_every(s, move(s, 1), _f1)
        def _f2(x=J.undefined, a=J.undefined, *_args):
            return (J.div(J.mul(100, x), a) if (((not J.nullish(x)) and (not J.nullish(a))) and J.sne(a, 0)) else None)
        return G_for_every(d, atrPct, _f2)
    def horizonBias(ema=J.undefined, slopeSeries=J.undefined, *_args):
        def _f1(c=J.undefined, e=J.undefined, sl=J.undefined, rs=J.undefined, *_args):
            if ((((J.nullish(c)) or (J.nullish(e))) or (J.nullish(sl))) or (J.nullish(rs))):
                return None
            bull = (J.ge(rs, rsiBull) if J.truthy(_t1 := (J.ge(sl, slopeK) if J.truthy(_t2 := J.gt(c, e)) else _t2)) else _t1)
            bear = (J.le(rs, rsiBear) if J.truthy(_t3 := (J.le(sl, J.neg(slopeK)) if J.truthy(_t4 := J.lt(c, e)) else _t4)) else _t3)
            if J.truthy(bull):
                return 1
            if J.truthy(bear):
                return (-1)
            return 0
        return G_for_every(G_close, ema, slopeSeries, rsi_indicator, _f1)
    def biasColor(b=J.undefined, *_args):
        if (J.nullish(b)):
            return "#C6C5C5"
        if J.gt(b, 0):
            return colorBlend("#C6C5C5", "#17B26A", 0.9)
        if J.lt(b, 0):
            return colorBlend("#C6C5C5", "#F04438", 0.9)
        return "#C6C5C5"
    def biasArrow(b=J.undefined, *_args):
        return ("↑" if J.gt(b, 0) else ("↓" if J.lt(b, 0) else "→"))
    G_describe_indicator("MTF Compass Pro #TSBuild25", "price", J.obj(("shortName", "MTF Compass+"), ("decimals", 2)))
    grpTF = "① Horizons"
    grpCore = "② Core"
    grpThr = "③ Thresholds"
    grpVis = "④ Display"
    lenS = J.get(G_input, "number")("Short EMA Len", 20, J.obj(("min", 2), ("step", 1), ("group", grpTF)))
    lenM = J.get(G_input, "number")("Mid EMA Len", 50, J.obj(("min", 3), ("step", 1), ("group", grpTF)))
    lenL = J.get(G_input, "number")("Long EMA Len", 200, J.obj(("min", 5), ("step", 1), ("group", grpTF)))
    rsiLen = J.get(G_input, "number")("RSI Len", 14, J.obj(("min", 2), ("step", 1), ("group", grpCore)))
    slopeK = J.get(G_input, "number")("Min EMA Slope (× ATR%)", 0.1, J.obj(("step", 0.01), ("group", grpThr)))
    rsiBull = J.get(G_input, "number")("RSI Bull ≥", 55, J.obj(("min", 0), ("max", 100), ("step", 1), ("group", grpThr)))
    rsiBear = J.get(G_input, "number")("RSI Bear ≤", 45, J.obj(("min", 0), ("max", 100), ("step", 1), ("group", grpThr)))
    showOverlay = J.get(G_input, "boolean")("Show Compass Overlay", True, J.obj(("group", grpVis)))
    showSignals = J.get(G_input, "boolean")("Register Bias Signals", True, J.obj(("group", grpVis)))
    tintChart = J.get(G_input, "boolean")("Background tint when aligned", True, J.obj(("group", grpVis)))
    prevClose = move(G_close, 1)
    def _f1(h=J.undefined, l=J.undefined, pc=J.undefined, *_args):
        if (((J.nullish(h)) or (J.nullish(l))) or (J.nullish(pc))):
            return None
        return J.get(G_Math, "max")(J.get(G_Math, "abs")(J.sub(h, l)), J.get(G_Math, "abs")(J.sub(h, pc)), J.get(G_Math, "abs")(J.sub(l, pc)))
    tr = G_for_every(G_high, G_low, prevClose, _f1)
    atrCalc = G_ema(tr, 14)
    def _f2(a=J.undefined, c=J.undefined, *_args):
        return (J.div(J.mul(100, a), c) if (((not J.nullish(a)) and (not J.nullish(c))) and J.sne(c, 0)) else None)
    atrPct = G_for_every(atrCalc, G_close, _f2)
    def _f3(c=J.undefined, p=J.undefined, *_args):
        return (J.sub(c, p) if ((not J.nullish(c)) and (not J.nullish(p))) else None)
    chg = G_for_every(G_close, prevClose, _f3)
    def _f4(x=J.undefined, *_args):
        return (x if ((not J.nullish(x)) and J.gt(x, 0)) else 0)
    up = G_for_every(chg, _f4)
    def _f5(x=J.undefined, *_args):
        return (J.neg(x) if ((not J.nullish(x)) and J.lt(x, 0)) else 0)
    dn = G_for_every(chg, _f5)
    rUp = G_ema(up, rsiLen)
    rDn = G_ema(dn, rsiLen)
    def _f6(u=J.undefined, d=J.undefined, *_args):
        return (J.div(J.mul(100, u), J.add(u, d)) if (((not J.nullish(u)) and (not J.nullish(d))) and J.gt(J.add(u, d), 0)) else None)
    rsi_indicator = G_for_every(rUp, rDn, _f6)
    emaS = G_ema(G_close, lenS)
    emaM = G_ema(G_close, lenM)
    emaL = G_ema(G_close, lenL)
    slS = normSlope(emaS)
    slM = normSlope(emaM)
    slL = normSlope(emaL)
    biasS = horizonBias(emaS, slS)
    biasM = horizonBias(emaM, slM)
    biasL = horizonBias(emaL, slL)
    snap = J.obj(("price", lastVal(G_close)), ("rsi", lastVal(rsi_indicator)), ("emaS", lastVal(emaS)), ("emaM", lastVal(emaM)), ("emaL", lastVal(emaL)), ("slS", lastVal(slS)), ("slM", lastVal(slM)), ("slL", lastVal(slL)), ("bS", lastVal(biasS)), ("bM", lastVal(biasM)), ("bL", lastVal(biasL)))
    allBull = (J.seq(J.get(snap, "bL"), 1) if J.truthy(_t7 := (J.seq(J.get(snap, "bM"), 1) if J.truthy(_t8 := J.seq(J.get(snap, "bS"), 1)) else _t8)) else _t7)
    allBear = (J.seq(J.get(snap, "bL"), (-1)) if J.truthy(_t9 := (J.seq(J.get(snap, "bM"), (-1)) if J.truthy(_t10 := J.seq(J.get(snap, "bS"), (-1))) else _t10)) else _t9)
    def _f12(x=J.undefined, *_args):
        return J.seq(x, 1)
    def _f13(x=J.undefined, *_args):
        return J.seq(x, (-1))
    align2 = (_t11 if J.truthy(_t11 := J.ge(J.get(J.get(J.JSArray([J.get(snap, "bS"), J.get(snap, "bM"), J.get(snap, "bL")]), "filter")(_f12), "length"), 2)) else J.ge(J.get(J.get(J.JSArray([J.get(snap, "bS"), J.get(snap, "bM"), J.get(snap, "bL")]), "filter")(_f13), "length"), 2))
    modeText = "Neutral"
    if J.truthy(allBull):
        modeText = "TREND MODE: Bull Breakouts"
    elif J.truthy(allBear):
        modeText = "TREND MODE: Bear Breakdowns"
    elif J.truthy(align2):
        modeText = "Trend Bias (≥2 aligned)"
    else:
        modeText = "RANGE MODE: Fade Extremes"
    if J.truthy(showOverlay):
        rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Multi-Timeframe Compass Pro"), ("bold", True))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Mode: ", modeText)), ("bold", True), ("color", ("#17B26A" if J.truthy(allBull) else ("#F04438" if J.truthy(allBear) else "#FFA500"))))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Price: ", fmt(J.get(snap, "price")), "   RSI: ", fmt(J.get(snap, "rsi"), 1))), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Short (", lenS, ") EMA ", fmt(J.get(snap, "emaS")), "  Sl:", fmt(J.get(snap, "slS"), 2), "×")), ("color", biasColor(J.get(snap, "bS")))), J.obj(("text", biasArrow(J.get(snap, "bS"))), ("align", "right"), ("color", biasColor(J.get(snap, "bS"))))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Mid   (", lenM, ") EMA ", fmt(J.get(snap, "emaM")), "  Sl:", fmt(J.get(snap, "slM"), 2), "×")), ("color", biasColor(J.get(snap, "bM")))), J.obj(("text", biasArrow(J.get(snap, "bM"))), ("align", "right"), ("color", biasColor(J.get(snap, "bM"))))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Long  (", lenL, ") EMA ", fmt(J.get(snap, "emaL")), "  Sl:", fmt(J.get(snap, "slL"), 2), "×")), ("color", biasColor(J.get(snap, "bL")))), J.obj(("text", biasArrow(J.get(snap, "bL"))), ("align", "right"), ("color", biasColor(J.get(snap, "bL"))))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Trend Alignment Meter"), ("bold", True))]))), J.obj(("cells", J.JSArray([J.obj(("text", "S"), ("color", biasColor(J.get(snap, "bS"))), ("align", "center"), ("padding", 4)), J.obj(("text", "M"), ("color", biasColor(J.get(snap, "bM"))), ("align", "center"), ("padding", 4)), J.obj(("text", "L"), ("color", biasColor(J.get(snap, "bL"))), ("align", "center"), ("padding", 4))])))])
        G_paint_overlay("MTF_CompassPro", J.obj(("position", "top_right")), J.obj(("rows", rows), ("border", "solid var(--border-color) 1px"), ("padding", 6)))
    if J.truthy(showSignals):
        def _f14(s=J.undefined, m=J.undefined, l=J.undefined, *_args):
            return (J.seq(l, 1) if J.truthy(_t1 := (J.seq(m, 1) if J.truthy(_t2 := J.seq(s, 1)) else _t2)) else _t1)
        bullNow = G_for_every(biasS, biasM, biasL, _f14)
        def _f15(s=J.undefined, m=J.undefined, l=J.undefined, *_args):
            return (J.seq(l, (-1)) if J.truthy(_t1 := (J.seq(m, (-1)) if J.truthy(_t2 := J.seq(s, (-1))) else _t2)) else _t1)
        bearNow = G_for_every(biasS, biasM, biasL, _f15)
        def _f16(s=J.undefined, m=J.undefined, l=J.undefined, *_args):
            return J.ge(J.add(J.add(J.seq(s, 1), J.seq(m, 1)), J.seq(l, 1)), 2)
        align2Up = G_for_every(biasS, biasM, biasL, _f16)
        def _f17(s=J.undefined, m=J.undefined, l=J.undefined, *_args):
            return J.ge(J.add(J.add(J.seq(s, (-1)), J.seq(m, (-1))), J.seq(l, (-1))), 2)
        align2Dn = G_for_every(biasS, biasM, biasL, _f17)
        G_register_signal(bullNow, "MTF+: All Bull")
        G_register_signal(bearNow, "MTF+: All Bear")
        G_register_signal(align2Up, "MTF+: ≥2 Bull")
        G_register_signal(align2Dn, "MTF+: ≥2 Bear")
    if J.truthy(tintChart):
        def _f18(s=J.undefined, m=J.undefined, l=J.undefined, *_args):
            if ((J.seq(s, 1) and J.seq(m, 1)) and J.seq(l, 1)):
                return "#E6FFEA"
            if ((J.seq(s, (-1)) and J.seq(m, (-1))) and J.seq(l, (-1))):
                return "#FFE6E6"
            return None
        tintSeries = G_for_every(biasS, biasM, biasL, _f18)
        G_color_candles(tintSeries)


register_store_indicator(
    script,
    name='mtf_compass_pro_TS',
    title='MTF Compass Pro',
    developer='Feliks Ba\\u0144ka',
    url='https://trendspider.com/trading-tools-store/indicators/68a60d-mtf-compass-pro/',
    position='price',
    inputs=[{'id': 'short_ema_len', 'title': 'Short EMA Len', 'type': 'number', 'default': 20}, {'id': 'mid_ema_len', 'title': 'Mid EMA Len', 'type': 'number', 'default': 50}, {'id': 'long_ema_len', 'title': 'Long EMA Len', 'type': 'number', 'default': 200}, {'id': 'rsi_len', 'title': 'RSI Len', 'type': 'number', 'default': 14}, {'id': 'min_ema_slope____atr__', 'title': 'Min EMA Slope (× ATR%)', 'type': 'number', 'default': 0.1}, {'id': 'rsi_bull__', 'title': 'RSI Bull ≥', 'type': 'number', 'default': 55}, {'id': 'rsi_bear__', 'title': 'RSI Bear ≤', 'type': 'number', 'default': 45}, {'id': 'show_compass_overlay', 'title': 'Show Compass Overlay', 'type': 'boolean', 'default': True}, {'id': 'register_bias_signals', 'title': 'Register Bias Signals', 'type': 'boolean', 'default': True}, {'id': 'background_tint_when_aligned', 'title': 'Background tint when aligned', 'type': 'boolean', 'default': True}],
    outputs=['mtf___all_bull', 'mtf___all_bear', 'mtf____2_bull', 'mtf____2_bear', 'cdl'],
    signals=['mtf___all_bull', 'mtf___all_bear', 'mtf____2_bull', 'mtf____2_bear'],
    requires=[],
    parity='exact',
)
