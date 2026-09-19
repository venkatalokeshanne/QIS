"""
CMF Divergences -- TrendSpider store indicator by khaled elsokkary.

Registered as "cmf_divergences_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa18-cmf-divergences/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_volume = G["volume"]
    def series_const(v=J.undefined, *_args):
        s = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            J.set(s, i, v)
            i = J.inc(i)
        return s
    def calc_cmf(length=J.undefined, *_args):
        out = G_series_of(None)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            if J.lt(i, J.sub(length, 1)):
                J.set(out, i, None)
                i = J.inc(i)
                continue
            sumMFV = 0
            sumVol = 0
            j = J.add(J.sub(i, length), 1)
            while J.le(j, i):
                h = J.get(G_high, j)
                l = J.get(G_low, j)
                c = J.get(G_close, j)
                v = J.get(G_volume, j)
                mfm = J.div(J.sub(J.sub(c, l), J.sub(h, c)), J.sub(h, l))
                sumMFV = J.add(sumMFV, J.mul(mfm, v))
                sumVol = J.add(sumVol, v)
                j = J.inc(j)
            J.set(out, i, (J.div(sumMFV, sumVol) if J.sne(sumVol, 0) else 0))
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
    G_describe_indicator("CMF Divergences", "lower", J.obj(("decimals", 2), ("shortName", "CMF Divs")))
    cmfLen = J.get(G_input, "number")("CMF Period", 20, J.obj(("min", 1), ("step", 1)))
    lbL = J.get(G_input, "number")("Pivot Lookback Left", 7, J.obj(("min", 1), ("step", 1)))
    lbR = J.get(G_input, "number")("Pivot Lookback Right", 7, J.obj(("min", 1), ("step", 1)))
    rangeUpper = J.get(G_input, "number")("Max of Lookback Range", 60, J.obj(("min", 2), ("step", 1)))
    rangeLower = J.get(G_input, "number")("Min of Lookback Range", 5, J.obj(("min", 1), ("step", 1)))
    signalMode = J.get(G_input, "select")("Signals", "Regular Only", J.JSArray(["Regular Only", "Hidden Only", "All", "None"]))
    showLines = J.get(G_input, "boolean")("Show Divergence Lines", True)
    showMarks = J.get(G_input, "boolean")("Show Pivot Markers", True)
    lineWidth = J.get(G_input, "number")("Line Width", 2, J.obj(("min", 1), ("max", 4)))
    colCMF = "#FFA500"
    colGuide = "#787B86"
    colBull = "#00C27A"
    colBear = "#E05A5A"
    colHBull = "#61D8A6"
    colHBear = "#F08C8C"
    cmfS = calc_cmf(cmfLen)
    G_paint(series_const(0), J.obj(("name", ""), ("color", colGuide), ("style", "line"), ("thickness", 1), ("opacity", 40)))
    G_paint(cmfS, J.obj(("name", "CMF"), ("color", colCMF), ("style", "line"), ("thickness", 2)))
    bullRegLine = G_series_of(None)
    bearRegLine = G_series_of(None)
    bullHidLine = G_series_of(None)
    bearHidLine = G_series_of(None)
    bullMark = G_series_of(None)
    bearMark = G_series_of(None)
    hBullMark = G_series_of(None)
    hBearMark = G_series_of(None)
    lastPL = None
    lastPH = None
    wantReg = (_t1 if J.truthy(_t1 := J.seq(signalMode, "Regular Only")) else J.seq(signalMode, "All"))
    wantHidden = (_t2 if J.truthy(_t2 := J.seq(signalMode, "Hidden Only")) else J.seq(signalMode, "All"))
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        p = J.sub(i, lbR)
        if J.lt(p, 0):
            i = J.inc(i)
            continue
        pl = is_pivot_low(cmfS, p, lbL, lbR)
        ph = is_pivot_high(cmfS, p, lbL, lbR)
        if J.truthy(pl):
            if J.truthy(lastPL):
                bars = J.sub(p, J.get(lastPL, "idx"))
                if (J.ge(bars, rangeLower) and J.le(bars, rangeUpper)):
                    cmfHL = J.gt(J.get(cmfS, p), J.get(lastPL, "cmf"))
                    cmfLL = J.lt(J.get(cmfS, p), J.get(lastPL, "cmf"))
                    priceLL = J.lt(J.get(G_low, p), J.get(lastPL, "price"))
                    priceHL = J.gt(J.get(G_low, p), J.get(lastPL, "price"))
                    if ((J.truthy(wantReg) and J.truthy(priceLL)) and J.truthy(cmfHL)):
                        if J.truthy(showLines):
                            draw_segment(bullRegLine, J.get(lastPL, "idx"), p, J.get(lastPL, "cmf"), J.get(cmfS, p))
                        if J.truthy(showMarks):
                            J.set(bullMark, p, J.get(cmfS, p))
                    if ((J.truthy(wantHidden) and J.truthy(priceHL)) and J.truthy(cmfLL)):
                        if J.truthy(showLines):
                            draw_segment(bullHidLine, J.get(lastPL, "idx"), p, J.get(lastPL, "cmf"), J.get(cmfS, p))
                        if J.truthy(showMarks):
                            J.set(hBullMark, p, J.get(cmfS, p))
            lastPL = J.obj(("idx", p), ("cmf", J.get(cmfS, p)), ("price", J.get(G_low, p)))
        if J.truthy(ph):
            if J.truthy(lastPH):
                bars_2 = J.sub(p, J.get(lastPH, "idx"))
                if (J.ge(bars_2, rangeLower) and J.le(bars_2, rangeUpper)):
                    cmfLH = J.lt(J.get(cmfS, p), J.get(lastPH, "cmf"))
                    cmfHH = J.gt(J.get(cmfS, p), J.get(lastPH, "cmf"))
                    priceHH = J.gt(J.get(G_high, p), J.get(lastPH, "price"))
                    priceLH = J.lt(J.get(G_high, p), J.get(lastPH, "price"))
                    if ((J.truthy(wantReg) and J.truthy(priceHH)) and J.truthy(cmfLH)):
                        if J.truthy(showLines):
                            draw_segment(bearRegLine, J.get(lastPH, "idx"), p, J.get(lastPH, "cmf"), J.get(cmfS, p))
                        if J.truthy(showMarks):
                            J.set(bearMark, p, J.get(cmfS, p))
                    if ((J.truthy(wantHidden) and J.truthy(priceLH)) and J.truthy(cmfHH)):
                        if J.truthy(showLines):
                            draw_segment(bearHidLine, J.get(lastPH, "idx"), p, J.get(lastPH, "cmf"), J.get(cmfS, p))
                        if J.truthy(showMarks):
                            J.set(hBearMark, p, J.get(cmfS, p))
            lastPH = J.obj(("idx", p), ("cmf", J.get(cmfS, p)), ("price", J.get(G_high, p)))
        i = J.inc(i)
    G_paint((bullRegLine if (J.truthy(showLines) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBull), ("style", "line"), ("thickness", lineWidth), ("opacity", 80)))
    G_paint((bearRegLine if (J.truthy(showLines) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBear), ("style", "line"), ("thickness", lineWidth), ("opacity", 80)))
    G_paint((bullHidLine if (J.truthy(showLines) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBull), ("style", "line"), ("thickness", lineWidth), ("opacity", 50)))
    G_paint((bearHidLine if (J.truthy(showLines) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBear), ("style", "line"), ("thickness", lineWidth), ("opacity", 50)))
    G_paint((bullMark if (J.truthy(showMarks) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBull), ("style", "column"), ("thickness", 4)))
    G_paint((bearMark if (J.truthy(showMarks) and J.truthy(wantReg)) else G_series_of(None)), J.obj(("name", ""), ("color", colBear), ("style", "column"), ("thickness", 4)))
    G_paint((hBullMark if (J.truthy(showMarks) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBull), ("style", "column"), ("thickness", 4)))
    G_paint((hBearMark if (J.truthy(showMarks) and J.truthy(wantHidden)) else G_series_of(None)), J.obj(("name", ""), ("color", colHBear), ("style", "column"), ("thickness", 4)))


register_store_indicator(
    script,
    name='cmf_divergences_TS',
    title='CMF Divergences',
    developer='khaled elsokkary',
    url='https://trendspider.com/trading-tools-store/indicators/68aa18-cmf-divergences/',
    position='lower',
    inputs=[{'id': 'cmf_period', 'title': 'CMF Period', 'type': 'number', 'default': 20}, {'id': 'pivot_lookback_left', 'title': 'Pivot Lookback Left', 'type': 'number', 'default': 7}, {'id': 'pivot_lookback_right', 'title': 'Pivot Lookback Right', 'type': 'number', 'default': 7}, {'id': 'max_of_lookback_range', 'title': 'Max of Lookback Range', 'type': 'number', 'default': 60}, {'id': 'min_of_lookback_range', 'title': 'Min of Lookback Range', 'type': 'number', 'default': 5}, {'id': 'signals', 'title': 'Signals', 'type': 'select_wide', 'default': 'Regular Only', 'options': ['Regular Only', 'Hidden Only', 'All', 'None']}, {'id': 'show_divergence_lines', 'title': 'Show Divergence Lines', 'type': 'boolean', 'default': True}, {'id': 'show_pivot_markers', 'title': 'Show Pivot Markers', 'type': 'boolean', 'default': True}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 2}],
    outputs=['line_1', 'cmf', 'line_3', 'line_4', 'line_5', 'line_6', 'line_7', 'line_8', 'line_9', 'line_10'],
    signals=[],
    requires=[],
    parity='exact',
)
