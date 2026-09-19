"""
RSI Divergences -- TrendSpider store indicator by Dr. Goose.

Registered as "rsi_divergences_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689ab4-rsi-divergences-tsbuild25/)
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
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def series_const(v=J.undefined, *_args):
        s = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            J.set(s, i, v)
            i = J.inc(i)
        return s
    def pick_source(name=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            c = J.get(G_close, i)
            h = J.get(G_high, i)
            l = J.get(G_low, i)
            o = J.get(G_open, i)
            if (J.seq(name, "hlc3") or J.seq(name, "typical")):
                J.set(out, i, J.div(J.add(J.add(h, l), c), 3))
            elif J.seq(name, "ohlc4"):
                J.set(out, i, J.div(J.add(J.add(J.add(o, h), l), c), 4))
            elif J.seq(name, "weighted"):
                J.set(out, i, J.div(J.add(J.add(J.add(o, J.mul(2, c)), h), l), 5))
            else:
                J.set(out, i, c)
            i = J.inc(i)
        return out
    def calc_rsi(src_2=J.undefined, L=J.undefined, *_args):
        out = G_series_of(None)
        g = 0
        l = 0
        i = 1
        while J.lt(i, J.get(src_2, "length")):
            d = (J.sub(J.get(src_2, i), J.get(src_2, J.sub(i, 1))) if ((not J.nullish(J.get(src_2, i))) and (not J.nullish(J.get(src_2, J.sub(i, 1))))) else 0)
            up = J.get(G_Math, "max")(d, 0)
            dn = J.get(G_Math, "max")(J.neg(d), 0)
            if J.lt(i, L):
                g = J.add(g, up)
                l = J.add(l, dn)
                J.set(out, i, None)
            elif J.seq(i, L):
                g = J.div(J.add(g, up), L)
                l = J.div(J.add(l, dn), L)
                rs = (G_Infinity if J.seq(l, 0) else J.div(g, l))
                J.set(out, i, J.sub(100, J.div(100, J.add(1, rs))))
            else:
                g = J.div(J.add(J.mul(g, J.sub(L, 1)), up), L)
                l = J.div(J.add(J.mul(l, J.sub(L, 1)), dn), L)
                rs_2 = (G_Infinity if J.seq(l, 0) else J.div(g, l))
                J.set(out, i, J.sub(100, J.div(100, J.add(1, rs_2))))
            i = J.inc(i)
        return out
    def is_pivot_low(s=J.undefined, i=J.undefined, L=J.undefined, R=J.undefined, *_args):
        if (J.lt(J.sub(i, L), 0) or J.ge(J.add(i, R), J.get(s, "length"))):
            return False
        v = J.get(s, i)
        if (J.nullish(v)):
            return False
        k = J.sub(i, L)
        while J.le(k, J.add(i, R)):
            vk = J.get(s, k)
            if (J.nullish(vk)):
                return False
            if J.lt(vk, v):
                return False
            k = J.inc(k)
        return True
    def is_pivot_high(s=J.undefined, i=J.undefined, L=J.undefined, R=J.undefined, *_args):
        if (J.lt(J.sub(i, L), 0) or J.ge(J.add(i, R), J.get(s, "length"))):
            return False
        v = J.get(s, i)
        if (J.nullish(v)):
            return False
        k = J.sub(i, L)
        while J.le(k, J.add(i, R)):
            vk = J.get(s, k)
            if (J.nullish(vk)):
                return False
            if J.gt(vk, v):
                return False
            k = J.inc(k)
        return True
    def draw_segment(target=J.undefined, i0=J.undefined, i1=J.undefined, v0=J.undefined, v1=J.undefined, *_args):
        if J.le(i1, i0):
            return J.undefined
        j = i0
        while J.le(j, i1):
            t = J.div(J.sub(j, i0), J.sub(i1, i0))
            J.set(target, j, J.add(v0, J.mul(t, J.sub(v1, v0))))
            j = J.inc(j)
    def draw_segment_dotted(target=J.undefined, i0=J.undefined, i1=J.undefined, v0=J.undefined, v1=J.undefined, *_args):
        if J.le(i1, i0):
            return J.undefined
        span = J.sub(i1, i0)
        j = i0
        while J.le(j, i1):
            t = J.div(J.sub(j, i0), span)
            on = J.lt(J.mod(J.sub(j, i0), 4), 2)
            J.set(target, j, (J.add(v0, J.mul(t, J.sub(v1, v0))) if J.truthy(on) else None))
            j = J.inc(j)
    def is_forming_pivot(series=J.undefined, price=J.undefined, i=J.undefined, isHigh=J.undefined, *_args):
        if (J.lt(J.sub(i, FORMING_LOOKBACK), 0) or J.ge(J.add(i, FORMING_LOOKBACK), J.get(G_time, "length"))):
            return False
        priceVal = J.get(price, i)
        k = J.sub(i, FORMING_LOOKBACK)
        while J.le(k, J.add(i, FORMING_LOOKBACK)):
            if J.seq(k, i):
                k = J.inc(k)
                continue
            if (J.truthy(isHigh) and J.gt(J.get(price, k), priceVal)):
                return False
            if ((not J.truthy(isHigh)) and J.lt(J.get(price, k), priceVal)):
                return False
            k = J.inc(k)
        return True
    G_describe_indicator("RSI Divergences #TSBuild25", "lower", J.obj(("decimals", 2), ("shortName", "RSI Divs")))
    rsiLen = G_input("RSI Period", 14, J.obj(("min", 1), ("step", 1)))
    srcName = G_input("RSI Source", "close", J.JSArray(["close", "hlc3", "ohlc4", "typical", "weighted"]), J.obj(("display", "data_window")))
    lbL = G_input("Pivot Lookback Left", 10, J.obj(("min", 1), ("step", 1), ("display", "data_window")))
    lbR = G_input("Pivot Lookback Right", 10, J.obj(("min", 1), ("step", 1), ("display", "data_window")))
    rangeUpper = G_input("Max of Lookback Range", 100, J.obj(("min", 2), ("step", 1), ("display", "data_window")))
    rangeLower = G_input("Min of Lookback Range", 5, J.obj(("min", 1), ("step", 1), ("display", "data_window")))
    signalMode = G_input("Signals", "Regular Only", J.JSArray(["Regular Only", "Hidden Only", "All", "None"]), J.obj(("display", "data_window")))
    showLines = J.get(G_input, "boolean")("Show Divergence Lines", True, J.obj(("display", "data_window")))
    showForming = J.get(G_input, "boolean")("Show Forming?", True, J.obj(("display", "data_window")))
    showMarks = J.get(G_input, "boolean")("Show Pivot Markers", True, J.obj(("display", "data_window")))
    lineWidth = G_input("Line Width", 2, J.obj(("min", 1), ("max", 4), ("display", "data_window")))
    colRSI = "#FFA500"
    colGuide = "#787B86"
    colBull = "#00C27A"
    colBear = "#E05A5A"
    colHBull = "#61D8A6"
    colHBear = "#F08C8C"
    src = pick_source(srcName)
    rsiS = calc_rsi(src, rsiLen)
    bullRegLine = G_series_of(None)
    bearRegLine = G_series_of(None)
    bullHidLine = G_series_of(None)
    bearHidLine = G_series_of(None)
    bullMark = G_series_of(None)
    bearMark = G_series_of(None)
    hBullMark = G_series_of(None)
    hBearMark = G_series_of(None)
    bullFormLine = G_series_of(None)
    bearFormLine = G_series_of(None)
    lastPL = None
    lastPH = None
    wantReg = (_t1 if J.truthy(_t1 := J.seq(signalMode, "Regular Only")) else J.seq(signalMode, "All"))
    wantHidden = (_t2 if J.truthy(_t2 := J.seq(signalMode, "Hidden Only")) else J.seq(signalMode, "All"))
    FORMING_LOOKBACK = 2
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        p = J.sub(i, lbR)
        if J.lt(p, 0):
            i = J.inc(i)
            continue
        pl = is_pivot_low(rsiS, p, lbL, lbR)
        ph = is_pivot_high(rsiS, p, lbL, lbR)
        if J.truthy(pl):
            if J.truthy(lastPL):
                bars = J.sub(p, J.get(lastPL, "idx"))
                if (J.ge(bars, rangeLower) and J.le(bars, rangeUpper)):
                    rsiHL = J.gt(J.get(rsiS, p), J.get(lastPL, "rsi"))
                    rsiLL = J.lt(J.get(rsiS, p), J.get(lastPL, "rsi"))
                    priceLL = J.lt(J.get(G_low, p), J.get(lastPL, "price"))
                    priceHL = J.gt(J.get(G_low, p), J.get(lastPL, "price"))
                    if ((J.truthy(wantReg) and J.truthy(priceLL)) and J.truthy(rsiHL)):
                        if J.truthy(showLines):
                            draw_segment(bullRegLine, J.get(lastPL, "idx"), p, J.get(lastPL, "rsi"), J.get(rsiS, p))
                        if J.truthy(showMarks):
                            J.set(bullMark, p, J.get(rsiS, p))
                    if ((J.truthy(wantHidden) and J.truthy(priceHL)) and J.truthy(rsiLL)):
                        if J.truthy(showLines):
                            draw_segment(bullHidLine, J.get(lastPL, "idx"), p, J.get(lastPL, "rsi"), J.get(rsiS, p))
                        if J.truthy(showMarks):
                            J.set(hBullMark, p, J.get(rsiS, p))
            lastPL = J.obj(("idx", p), ("rsi", J.get(rsiS, p)), ("price", J.get(G_low, p)))
        if J.truthy(ph):
            if J.truthy(lastPH):
                bars_2 = J.sub(p, J.get(lastPH, "idx"))
                if (J.ge(bars_2, rangeLower) and J.le(bars_2, rangeUpper)):
                    rsiLH = J.lt(J.get(rsiS, p), J.get(lastPH, "rsi"))
                    rsiHH = J.gt(J.get(rsiS, p), J.get(lastPH, "rsi"))
                    priceHH = J.gt(J.get(G_high, p), J.get(lastPH, "price"))
                    priceLH = J.lt(J.get(G_high, p), J.get(lastPH, "price"))
                    if ((J.truthy(wantReg) and J.truthy(priceHH)) and J.truthy(rsiLH)):
                        if J.truthy(showLines):
                            draw_segment(bearRegLine, J.get(lastPH, "idx"), p, J.get(lastPH, "rsi"), J.get(rsiS, p))
                        if J.truthy(showMarks):
                            J.set(bearMark, p, J.get(rsiS, p))
                    if ((J.truthy(wantHidden) and J.truthy(priceLH)) and J.truthy(rsiHH)):
                        if J.truthy(showLines):
                            draw_segment(bearHidLine, J.get(lastPH, "idx"), p, J.get(lastPH, "rsi"), J.get(rsiS, p))
                        if J.truthy(showMarks):
                            J.set(hBearMark, p, J.get(rsiS, p))
            lastPH = J.obj(("idx", p), ("rsi", J.get(rsiS, p)), ("price", J.get(G_high, p)))
        i = J.inc(i)
    if J.truthy(showForming):
        if J.truthy(lastPH):
            i_2 = J.sub(J.sub(J.get(G_time, "length"), 1), FORMING_LOOKBACK)
            while J.gt(i_2, J.get(lastPH, "idx")):
                if J.truthy(is_forming_pivot(rsiS, G_high, i_2, True)):
                    potentialPivotIdx = i_2
                    priceHH_2 = J.gt(J.get(G_high, potentialPivotIdx), J.get(lastPH, "price"))
                    priceLH_2 = J.lt(J.get(G_high, potentialPivotIdx), J.get(lastPH, "price"))
                    rsiLH_2 = J.lt(J.get(rsiS, potentialPivotIdx), J.get(lastPH, "rsi"))
                    rsiHH_2 = J.gt(J.get(rsiS, potentialPivotIdx), J.get(lastPH, "rsi"))
                    if (((J.truthy(wantReg) and J.truthy(priceHH_2)) and J.truthy(rsiLH_2)) or ((J.truthy(wantHidden) and J.truthy(priceLH_2)) and J.truthy(rsiHH_2))):
                        draw_segment_dotted(bearFormLine, J.get(lastPH, "idx"), potentialPivotIdx, J.get(lastPH, "rsi"), J.get(rsiS, potentialPivotIdx))
                    break
                i_2 = J.dec(i_2)
        if J.truthy(lastPL):
            i_3 = J.sub(J.sub(J.get(G_time, "length"), 1), FORMING_LOOKBACK)
            while J.gt(i_3, J.get(lastPL, "idx")):
                if J.truthy(is_forming_pivot(rsiS, G_low, i_3, False)):
                    potentialPivotIdx_2 = i_3
                    priceLL_2 = J.lt(J.get(G_low, potentialPivotIdx_2), J.get(lastPL, "price"))
                    priceHL_2 = J.gt(J.get(G_low, potentialPivotIdx_2), J.get(lastPL, "price"))
                    rsiHL_2 = J.gt(J.get(rsiS, potentialPivotIdx_2), J.get(lastPL, "rsi"))
                    rsiLL_2 = J.lt(J.get(rsiS, potentialPivotIdx_2), J.get(lastPL, "rsi"))
                    if (((J.truthy(wantReg) and J.truthy(priceLL_2)) and J.truthy(rsiHL_2)) or ((J.truthy(wantHidden) and J.truthy(priceHL_2)) and J.truthy(rsiLL_2))):
                        draw_segment_dotted(bullFormLine, J.get(lastPL, "idx"), potentialPivotIdx_2, J.get(lastPL, "rsi"), J.get(rsiS, potentialPivotIdx_2))
                    break
                i_3 = J.dec(i_3)
    G_paint(series_const(50), J.obj(("name", ""), ("color", colGuide), ("style", "line"), ("thickness", 1), ("opacity", 40)))
    G_paint(series_const(70), J.obj(("name", ""), ("color", colGuide), ("style", "line"), ("thickness", 1), ("opacity", 25)))
    G_paint(series_const(30), J.obj(("name", ""), ("color", colGuide), ("style", "line"), ("thickness", 1), ("opacity", 25)))
    G_paint(rsiS, J.obj(("name", "RSI"), ("color", colRSI), ("style", "line"), ("thickness", 2)))
    G_paint((bullRegLine if (J.truthy(showLines) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBull), ("style", "line"), ("thickness", lineWidth), ("opacity", 80)))
    G_paint((bearRegLine if (J.truthy(showLines) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBear), ("style", "line"), ("thickness", lineWidth), ("opacity", 80)))
    G_paint((bullHidLine if (J.truthy(showLines) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBull), ("style", "line"), ("thickness", lineWidth), ("opacity", 50)))
    G_paint((bearHidLine if (J.truthy(showLines) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBear), ("style", "line"), ("thickness", lineWidth), ("opacity", 50)))
    if J.truthy(showForming):
        G_paint(bullFormLine, J.obj(("name", ""), ("color", colBull), ("style", "line"), ("thickness", lineWidth), ("opacity", 65)))
        G_paint(bearFormLine, J.obj(("name", ""), ("color", colBear), ("style", "line"), ("thickness", lineWidth), ("opacity", 65)))


register_store_indicator(
    script,
    name='rsi_divergences_TS',
    title='RSI Divergences',
    developer='Dr. Goose',
    url='https://trendspider.com/trading-tools-store/indicators/689ab4-rsi-divergences-tsbuild25/',
    position='lower',
    inputs=[{'id': 'rsi_period', 'title': 'RSI Period', 'type': 'number', 'default': 14}, {'id': 'rsi_source', 'title': 'RSI Source', 'type': 'select_wide', 'default': 'close', 'options': ['close', 'hlc3', 'ohlc4', 'typical', 'weighted']}, {'id': 'pivot_lookback_left', 'title': 'Pivot Lookback Left', 'type': 'number', 'default': 10}, {'id': 'pivot_lookback_right', 'title': 'Pivot Lookback Right', 'type': 'number', 'default': 10}, {'id': 'max_of_lookback_range', 'title': 'Max of Lookback Range', 'type': 'number', 'default': 100}, {'id': 'min_of_lookback_range', 'title': 'Min of Lookback Range', 'type': 'number', 'default': 5}, {'id': 'signals', 'title': 'Signals', 'type': 'select_wide', 'default': 'Regular Only', 'options': ['Regular Only', 'Hidden Only', 'All', 'None']}, {'id': 'show_divergence_lines', 'title': 'Show Divergence Lines', 'type': 'boolean', 'default': True}, {'id': 'show_forming_', 'title': 'Show Forming?', 'type': 'boolean', 'default': True}, {'id': 'show_pivot_markers', 'title': 'Show Pivot Markers', 'type': 'boolean', 'default': True}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 2}],
    outputs=['line_1', 'line_2', 'line_3', 'rsi', 'line_5', 'line_6', 'line_7', 'line_8', 'line_9', 'line_10'],
    signals=[],
    requires=[],
    parity='exact',
)
