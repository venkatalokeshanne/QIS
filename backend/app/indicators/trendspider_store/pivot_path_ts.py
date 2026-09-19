"""
Pivot Path -- TrendSpider store indicator by Kodexius.

Registered as "pivot_path_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e90a-zigzag/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("Pivot Path", "price")
    lengthInput = J.get(G_input, "number")("Pivot Length", 20, J.obj(("min", 1), ("max", 100)))
    addPivotInput = J.get(G_input, "boolean")("Detect additional pivots", True)
    zzBullColorInput = J.get(G_input, "color")("Bull Color", "green")
    zzBearColorInput = J.get(G_input, "color")("Bear Color", "red")
    zzwidthInput = J.get(G_input, "number")("Line Width", 2, J.obj(("min", 1)))
    def highestBars(_high=J.undefined, _length=J.undefined, *_args):
        out = J.JSArray([])
        i = 0
        while J.lt(i, J.get(_high, "length")):
            if J.lt(i, J.sub(_length, 1)):
                J.get(out, "push")(None)
                i = J.inc(i)
                continue
            maxVal = J.get(_high, i)
            maxOff = 0
            j = 1
            while J.lt(j, _length):
                if J.gt(J.get(_high, J.sub(i, j)), maxVal):
                    maxVal = J.get(_high, J.sub(i, j))
                    maxOff = J.neg(j)
                j = J.inc(j)
            J.get(out, "push")(maxOff)
            i = J.inc(i)
        return out
    def lowestBars(_low=J.undefined, _length=J.undefined, *_args):
        out = J.JSArray([])
        i = 0
        while J.lt(i, J.get(_low, "length")):
            if J.lt(i, J.sub(_length, 1)):
                J.get(out, "push")(None)
                i = J.inc(i)
                continue
            minVal = J.get(_low, i)
            minOff = 0
            j = 1
            while J.lt(j, _length):
                if J.lt(J.get(_low, J.sub(i, j)), minVal):
                    minVal = J.get(_low, J.sub(i, j))
                    minOff = J.neg(j)
                j = J.inc(j)
            J.get(out, "push")(minOff)
            i = J.inc(i)
        return out
    pivots = J.JSArray([])
    curPivot = None
    dir = None
    i = J.sub(lengthInput, 1)
    while J.lt(i, J.get(G_close, "length")):
        hiBar = J.get(highestBars(J.get(G_high, "slice")(0, J.add(i, 1)), lengthInput), i)
        loBar = J.get(lowestBars(J.get(G_low, "slice")(0, J.add(i, 1)), lengthInput), i)
        newDir = None
        if (J.seq(hiBar, 0) and J.seq(loBar, 0)):
            newDir = ((-1) if J.seq(dir, 1) else 1)
        elif J.seq(hiBar, 0):
            newDir = 1
        elif J.seq(loBar, 0):
            newDir = (-1)
        if ((J.truthy(addPivotInput) and J.truthy(curPivot)) and (not J.truthy(newDir))):
            bars = J.sub(i, J.get(curPivot, "index"))
            if J.ge(bars, lengthInput):
                altLen = J.get(G_Math, "max")(bars, 1)
                altHi = J.get(highestBars(J.get(G_high, "slice")(0, J.add(i, 1)), altLen), i)
                altLo = J.get(lowestBars(J.get(G_low, "slice")(0, J.add(i, 1)), altLen), i)
                missed = (not ((J.seq(hiBar, 0) and J.gt(J.get(G_high, i), J.get(curPivot, "value"))) or (J.seq(loBar, 0) and J.lt(J.get(G_low, i), J.get(curPivot, "value")))))
                if J.truthy(missed):
                    newDir = ((-1) if J.seq(dir, 1) else 1)
                    altIdx = J.add(i, (altHi if J.gt(newDir, 0) else altLo))
                    altVal = (J.get(G_high, altIdx) if J.gt(newDir, 0) else J.get(G_low, altIdx))
                    J.get(pivots, "push")(J.obj(("index", altIdx), ("value", altVal), ("direction", newDir)))
                    curPivot = J.get(pivots, J.sub(J.get(pivots, "length"), 1))
                    dir = newDir
                    i = J.inc(i)
                    continue
        if (J.truthy(newDir) and J.sne(newDir, dir)):
            pv = (J.get(G_high, i) if J.gt(newDir, 0) else J.get(G_low, i))
            J.get(pivots, "push")(J.obj(("index", i), ("value", pv), ("direction", newDir)))
            curPivot = J.get(pivots, J.sub(J.get(pivots, "length"), 1))
            dir = newDir
        if J.truthy(curPivot):
            curVal = (J.get(G_high, i) if J.gt(dir, 0) else J.get(G_low, i))
            if J.gt(J.mul(curVal, dir), J.mul(J.get(curPivot, "value"), dir)):
                J.set(curPivot, "index", i)
                J.set(curPivot, "value", curVal)
        i = J.inc(i)
    zzSeries = G_series_of(None)
    colorSeries = J.JSArray([])
    p = 0
    while J.lt(p, J.get(pivots, "length")):
        J.set(zzSeries, J.get(J.get(pivots, p), "index"), J.get(J.get(pivots, p), "value"))
        p = J.inc(p)
    p_2 = 0
    while J.lt(p_2, J.sub(J.get(pivots, "length"), 1)):
        a = J.get(pivots, p_2)
        b = J.get(pivots, J.add(p_2, 1))
        segColor = (zzBullColorInput if J.gt(J.get(b, "direction"), 0) else zzBearColorInput)
        i_2 = J.get(a, "index")
        while J.le(i_2, J.get(b, "index")):
            J.set(colorSeries, i_2, segColor)
            i_2 = J.inc(i_2)
        p_2 = J.inc(p_2)
    if J.gt(J.get(pivots, "length"), 0):
        last = J.get(pivots, J.sub(J.get(pivots, "length"), 1))
        curIdx = J.sub(J.get(G_close, "length"), 1)
        curVal_2 = (J.get(G_high, curIdx) if J.gt(dir, 0) else J.get(G_low, curIdx))
        J.set(zzSeries, J.get(last, "index"), J.get(last, "value"))
        J.set(zzSeries, curIdx, curVal_2)
        curColor = (zzBullColorInput if J.gt(dir, 0) else zzBearColorInput)
        i_3 = J.get(last, "index")
        while J.le(i_3, curIdx):
            J.set(colorSeries, i_3, curColor)
            i_3 = J.inc(i_3)
    G_paint(zzSeries, J.obj(("style", "line"), ("color", colorSeries), ("width", zzwidthInput), ("name", "Path")))


register_store_indicator(
    script,
    name='pivot_path_TS',
    title='Pivot Path',
    developer='Kodexius',
    url='https://trendspider.com/trading-tools-store/indicators/68e90a-zigzag/',
    position='price',
    inputs=[{'id': 'pivot_length', 'title': 'Pivot Length', 'type': 'number', 'default': 20}, {'id': 'detect_additional_pivots', 'title': 'Detect additional pivots', 'type': 'boolean', 'default': True}, {'id': 'bull_color', 'title': 'Bull Color', 'type': 'color', 'default': 'green'}, {'id': 'bear_color', 'title': 'Bear Color', 'type': 'color', 'default': 'red'}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 2}],
    outputs=['path'],
    signals=[],
    requires=[],
    parity='exact',
)
