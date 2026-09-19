"""
ADT  (Lower) -- TrendSpider store indicator by Adrian Ieta.

Registered as "adt_lower_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab83-adt-lower/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_parseInt = G["parseInt"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_wma = G["wma"]
    def hexToRgbaSafe(color=J.undefined, a=J.undefined, *_args):
        if (J.nullish(color)):
            return J.template("rgba(128,128,128,", a, ")")
        if J.sne(J.typeof(color), "string"):
            return J.template("rgba(128,128,128,", a, ")")
        if J.truthy(J.get(color, "startsWith")("rgba(")):
            if (J.nullish(a)):
                return color
            return J.get(color, "replace")(J.regex("rgba((d+),(d+),(d+),[^)]+)", ""), J.template("rgba($1,$2,$3,", a, ")"))
        if (not J.truthy(J.get(color, "startsWith")("#"))):
            return J.template("rgba(128,128,128,", a, ")")
        h = J.get(color, "replace")("#", "")
        if J.seq(J.get(h, "length"), 3):
            def _f1(ch=J.undefined, *_args):
                return J.add(ch, ch)
            h = J.get(J.get(J.get(h, "split")(""), "map")(_f1), "join")("")
        r = G_parseInt(J.get(h, "slice")(0, 2), 16)
        g = G_parseInt(J.get(h, "slice")(2, 4), 16)
        b = G_parseInt(J.get(h, "slice")(4, 6), 16)
        return J.template("rgba(", r, ",", g, ",", b, ",", a, ")")
    G_describe_indicator("ADT  (Lower)", "lower", J.obj(("shortName", "ADT-MA"), ("warmup", 300)))
    MA_OPTIONS = J.JSArray(["ema", "sma", "wma"])
    maType = G_input("MA Type", "ema", MA_OPTIONS)
    lenFast = J.get(G_input, "number")("Fast MA (MovAve)", 34, J.obj(("min", 1)))
    lenSlow = J.get(G_input, "number")("Slow MA (MovAvew)", 89, J.obj(("min", 1)))
    atrLength = J.get(G_input, "number")("ATR Length", 34, J.obj(("min", 1)))
    showHistogram = J.get(G_input, "boolean")("Show Histogram", True)
    histOpacity = J.get(G_input, "number")("Histogram Opacity (0–1)", 0.45, J.obj(("min", 0), ("max", 1), ("step", 0.05)))
    showDaily = J.get(G_input, "boolean")("Show Daily Lines (Fast/Slow)", True)
    show4h = J.get(G_input, "boolean")("Show 4h Lines (21/55)", False)
    show1h = J.get(G_input, "boolean")("Show 1h Lines (5/14)", False)
    c = G_close
    c2 = G_shift(c, 2)
    c3 = G_shift(c, 3)
    c5 = G_shift(c, 5)
    c8 = G_shift(c, 8)
    c13 = G_shift(c, 13)
    c21 = G_shift(c, 21)
    c34 = G_shift(c, 34)
    c55 = G_shift(c, 55)
    c89 = G_shift(c, 89)
    c144 = G_shift(c, 144)
    atrV = G_atr(atrLength)
    def _f1(cc=J.undefined, cc2=J.undefined, cc3=J.undefined, cc5=J.undefined, cc8=J.undefined, cc13=J.undefined, cc21=J.undefined, cc34=J.undefined, cc55=J.undefined, cc89=J.undefined, cc144=J.undefined, atrRaw=J.undefined, *_args):
        core = J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.add(J.div(J.sub(cc, cc2), 2), J.div(J.sub(cc, cc3), 3)), J.div(J.sub(cc, cc5), 5)), J.div(J.sub(cc, cc8), 8)), J.div(J.sub(cc, cc13), 13)), J.div(J.sub(cc, cc21), 21)), J.div(J.sub(cc, cc34), 34)), J.div(J.sub(cc, cc55), 55)), J.div(J.sub(cc, cc89), 89)), J.div(J.sub(cc, cc144), 144))
        denom = (0.0001 if ((J.nullish(atrRaw)) or J.seq(atrRaw, 0)) else atrRaw)
        return J.mul(10, J.div(core, denom))
    ADT = G_for_every(c, c2, c3, c5, c8, c13, c21, c34, c55, c89, c144, atrV, _f1)
    maFn = (G_sma if J.seq(maType, "sma") else (G_wma if J.seq(maType, "wma") else G_ema))
    MovAve = maFn(ADT, lenFast)
    MovAvew = maFn(ADT, lenSlow)
    MovAve4h = maFn(ADT, 21)
    MovAvew4h = maFn(ADT, 55)
    MovAve1h = maFn(ADT, 5)
    MovAvew1h = maFn(ADT, 14)
    MAGENTA = "#ff00ff"
    UPTICK = "#00ff00"
    DARK_GRAY = "#444444"
    DARK_GREEN = "#006400"
    LIME = "#66ff66"
    DOWNTICK = "#ff6a00"
    BLUE = "#0080ff"
    LIGHT_GRAY = "#bbbbbb"
    RED = "#ff0000"
    PINK = "#ff66cc"
    GRAY = "#808080"
    fP = G_shift(MovAve, 1)
    sP = G_shift(MovAvew, 1)
    def _f2(f=J.undefined, s=J.undefined, fp=J.undefined, sp=J.undefined, *_args):
        crossDown = ((J.lt(f, s) if J.truthy(_t1 := J.ge(fp, sp)) else _t1) if ((not J.nullish(fp)) and (not J.nullish(sp))) else False)
        fastAbove = J.gt(f, s)
        bothPos = (J.gt(s, 0) if J.truthy(_t2 := J.gt(f, 0)) else _t2)
        bothNeg = (J.lt(s, 0) if J.truthy(_t3 := J.lt(f, 0)) else _t3)
        posInc = (J.gt(f, fp) if (not J.nullish(fp)) else False)
        negInc = (J.lt(f, fp) if (not J.nullish(fp)) else False)
        if J.truthy(crossDown):
            return MAGENTA
        if (J.truthy(fastAbove) and J.truthy(bothPos)):
            return (UPTICK if J.truthy(posInc) else DARK_GRAY)
        if (J.truthy(fastAbove) and J.truthy(bothNeg)):
            return (DARK_GREEN if J.truthy(posInc) else LIME)
        if ((not J.truthy(fastAbove)) and J.truthy(bothPos)):
            widen = (J.gt(J.sub(s, f), J.sub(sp, fp)) if ((not J.nullish(sp)) and (not J.nullish(fp))) else False)
            return (DOWNTICK if J.truthy(widen) else (BLUE if J.truthy(negInc) else LIGHT_GRAY))
        if ((not J.truthy(fastAbove)) and J.truthy(bothNeg)):
            return (RED if J.truthy(negInc) else PINK)
        return GRAY
    baseColors = G_for_every(MovAve, MovAvew, fP, sP, _f2)
    def _f3(col=J.undefined, *_args):
        return hexToRgbaSafe(col, histOpacity)
    histColors = J.get(baseColors, "map")(_f3)
    if J.truthy(showHistogram):
        G_paint(MovAve, J.obj(("name", "MovAve (hist)"), ("style", "histogram"), ("color", histColors), ("padding", 0), ("width", 2)))
    if J.truthy(showDaily):
        G_paint(MovAve, J.obj(("name", "MovAve"), ("color", "#22aa22"), ("thickness", 2)))
        G_paint(MovAvew, J.obj(("name", "MovAvew"), ("color", "#ff9900"), ("thickness", 2)))
    if J.truthy(show4h):
        G_paint(MovAve4h, J.obj(("name", "MovAve 4h (21)"), ("color", "#00bcd4"), ("thickness", 1)))
        G_paint(MovAvew4h, J.obj(("name", "MovAvew 4h (55)"), ("color", "#ab47bc"), ("thickness", 1)))
    if J.truthy(show1h):
        G_paint(MovAve1h, J.obj(("name", "MovAve 1h (5)"), ("color", "#1f77b4"), ("thickness", 1)))
        G_paint(MovAvew1h, J.obj(("name", "MovAvew 1h (14)"), ("color", "#ff7f0e"), ("thickness", 1)))
    def _f4(*_args):
        return 0
    G_paint(J.get(MovAve, "map")(_f4), J.obj(("name", "Zero"), ("color", "#888888"), ("thickness", 1)))
    def _f5(f=J.undefined, s=J.undefined, *_args):
        return J.sub(f, s)
    gap = G_for_every(MovAve, MovAvew, _f5)
    def _f6(v=J.undefined, *_args):
        return ("#00ff3a" if J.ge(v, 0) else "#ff00ff")
    gapColors = J.get(gap, "map")(_f6)
    G_paint(gap, J.obj(("name", "MA Gap (halo)"), ("color", "rgba(0,0,0,0.35)"), ("thickness", 5)))
    G_paint(gap, J.obj(("name", "MA Gap (fast−slow)"), ("color", gapColors), ("thickness", 2), ("style", "dotted")))


register_store_indicator(
    script,
    name='adt_lower_TS',
    title='ADT  (Lower)',
    developer='Adrian Ieta',
    url='https://trendspider.com/trading-tools-store/indicators/68ab83-adt-lower/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 300}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'sma', 'wma']}, {'id': 'fast_ma__movave_', 'title': 'Fast MA (MovAve)', 'type': 'number', 'default': 34}, {'id': 'slow_ma__movavew_', 'title': 'Slow MA (MovAvew)', 'type': 'number', 'default': 89}, {'id': 'atr_length', 'title': 'ATR Length', 'type': 'number', 'default': 34}, {'id': 'show_histogram', 'title': 'Show Histogram', 'type': 'boolean', 'default': True}, {'id': 'histogram_opacity__0_1_', 'title': 'Histogram Opacity (0–1)', 'type': 'number', 'default': 0.45}, {'id': 'show_daily_lines__fast_slow_', 'title': 'Show Daily Lines (Fast/Slow)', 'type': 'boolean', 'default': True}, {'id': 'show_4h_lines__21_55_', 'title': 'Show 4h Lines (21/55)', 'type': 'boolean', 'default': False}, {'id': 'show_1h_lines__5_14_', 'title': 'Show 1h Lines (5/14)', 'type': 'boolean', 'default': False}],
    outputs=['movave__hist_', 'movave', 'movavew', 'zero', 'ma_gap__halo_', 'ma_gap__fast_slow_'],
    signals=[],
    requires=[],
    parity='exact',
)
