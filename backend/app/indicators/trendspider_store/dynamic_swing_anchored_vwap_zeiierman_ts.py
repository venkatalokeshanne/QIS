"""
Dynamic Swing Anchored VWAP (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "dynamic_swing_anchored_vwap_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e7b9-dynamic-swing-anchored-vwap-zeiierman/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_hlc3 = G["hlc3"]
    G_indexed_points_of = G["indexed_points_of"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_pivot_high = G["pivot_high"]
    G_pivot_low = G["pivot_low"]
    G_series_of = G["series_of"]
    G_volume = G["volume"]
    G_describe_indicator("Dynamic Swing Anchored VWAP (Zeiierman)", J.obj(("mainColorInheritFrom", "text"), ("shortName", "Dynamic Swing Anchored VWAP (Zeiierman)")))
    prd = J.get(G_input, "number")("Swing Period", 30, J.obj(("min", 2), ("max", 500)))
    baseAPT = J.get(G_input, "number")("Adaptive Price Tracking", 20, J.obj(("min", 1), ("max", 300)))
    useAdapt = J.get(G_input, "boolean")("Adapt APT by ATR ratio", False)
    volBias = J.get(G_input, "number")("Volatility Bias", 10, J.obj(("min", 0.1), ("max", 100)))
    highS = J.get(G_input, "color")("Swing High Color", "lime")
    lowS = J.get(G_input, "color")("Swing Low Color", "red")
    upColor = J.get(G_input, "color")("VWAP Up Color", "lime")
    downColor = J.get(G_input, "color")("VWAP Down Color", "red")
    pivotHigh = G_pivot_high(G_high, prd, prd)
    pivotLow = G_pivot_low(G_low, prd, prd)
    pivotHighIndexes = G_indexed_points_of(pivotHigh)
    pivotLowIndexes = G_indexed_points_of(pivotLow)
    def _f1(p=J.undefined, *_args):
        return J.obj(*J.obj_spread(p), ("type", "high"))
    def _f2(p=J.undefined, *_args):
        return J.obj(*J.obj_spread(p), ("type", "low"))
    allPivots = J.JSArray([*J.spread(J.get(pivotHighIndexes, "map")(_f1)), *J.spread(J.get(pivotLowIndexes, "map")(_f2))])
    def _f3(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(a, "candleIndex"), J.get(b, "candleIndex"))
    J.get(allPivots, "sort")(_f3)
    filteredPivots = J.JSArray([])
    lastPivot = None
    for pivot in J.iter_of(allPivots):
        if J.seq(J.get(filteredPivots, "length"), 0):
            J.get(filteredPivots, "push")(pivot)
            lastPivot = pivot
        else:
            if J.sne(J.get(pivot, "type"), J.get(lastPivot, "type")):
                J.get(filteredPivots, "push")(pivot)
                lastPivot = pivot
            else:
                if J.seq(J.get(pivot, "type"), "high"):
                    if J.gt(J.get(pivot, "value"), J.get(lastPivot, "value")):
                        J.set(filteredPivots, J.sub(J.get(filteredPivots, "length"), 1), pivot)
                        lastPivot = pivot
                else:
                    if J.lt(J.get(pivot, "value"), J.get(lastPivot, "value")):
                        J.set(filteredPivots, J.sub(J.get(filteredPivots, "length"), 1), pivot)
                        lastPivot = pivot
    atrLen = 50
    myAtr = G_atr(G_high, G_low, G_close, atrLen)
    atrAvg = G_ema(myAtr, atrLen)
    def _f4(_atr=J.undefined, _avg=J.undefined, *_args):
        ratio = (J.div(_atr, _avg) if J.gt(_avg, 0) else 1)
        aptRaw = (J.div(baseAPT, J.get(G_Math, "pow")(ratio, volBias)) if J.truthy(useAdapt) else baseAPT)
        aptClamped = J.get(G_Math, "max")(5, J.get(G_Math, "min")(300, aptRaw))
        return J.get(G_Math, "round")(aptClamped)
    aptSeries = G_for_every(myAtr, atrAvg, _f4)
    vwapUp = G_series_of(None)
    vwapDown = G_series_of(None)
    swingHighLabels = G_series_of(None)
    swingLowLabels = G_series_of(None)
    lastHighPrice = None
    lastLowPrice = None
    i = 0
    while J.lt(i, J.get(filteredPivots, "length")):
        pivot_2 = J.get(filteredPivots, i)
        startIdx = J.get(pivot_2, "candleIndex")
        endIdx = (J.get(J.get(filteredPivots, J.add(i, 1)), "candleIndex") if J.lt(i, J.sub(J.get(filteredPivots, "length"), 1)) else J.sub(J.get(G_close, "length"), 1))
        isHigh = J.seq(J.get(pivot_2, "type"), "high")
        direction = ((-1) if J.truthy(isHigh) else 1)
        swingLabel = ""
        if J.truthy(isHigh):
            if (lastHighPrice is not None):
                swingLabel = ("HH" if J.gt(J.get(pivot_2, "value"), lastHighPrice) else "LH")
            lastHighPrice = J.get(pivot_2, "value")
        else:
            if (lastLowPrice is not None):
                swingLabel = ("HL" if J.gt(J.get(pivot_2, "value"), lastLowPrice) else "LL")
            lastLowPrice = J.get(pivot_2, "value")
        anchorPrice = (J.get(G_high, startIdx) if J.truthy(isHigh) else J.get(G_low, startIdx))
        myP = J.mul(anchorPrice, J.get(G_volume, startIdx))
        myVol = J.get(G_volume, startIdx)
        j = startIdx
        while (J.le(j, endIdx) and J.lt(j, J.get(G_close, "length"))):
            apt = J.get(aptSeries, j)
            alpha = J.sub(1, J.get(G_Math, "exp")(J.div(J.neg(J.get(G_Math, "log")(2)), J.get(G_Math, "max")(1, apt))))
            pxv = J.mul(J.get(G_hlc3, j), J.get(G_volume, j))
            v = J.get(G_volume, j)
            myP = J.add(J.mul(J.sub(1, alpha), myP), J.mul(alpha, pxv))
            myVol = J.add(J.mul(J.sub(1, alpha), myVol), J.mul(alpha, v))
            vwapValue = (J.div(myP, myVol) if J.gt(myVol, 0) else None)
            if J.gt(direction, 0):
                J.set(vwapUp, j, vwapValue)
            else:
                J.set(vwapDown, j, vwapValue)
            if (J.seq(j, startIdx) and J.truthy(swingLabel)):
                if J.truthy(isHigh):
                    J.set(swingHighLabels, j, swingLabel)
                else:
                    J.set(swingLowLabels, j, swingLabel)
            j = J.inc(j)
        i = J.inc(i)
    G_paint(vwapUp, J.obj(("color", upColor), ("style", "line"), ("name", "Dynamic VWAP Up")))
    G_paint(vwapDown, J.obj(("color", downColor), ("style", "line"), ("name", "Dynamic VWAP Down")))
    def _f5(_label=J.undefined, *_args):
        if (not J.truthy(_label)):
            return None
        return ("red" if J.seq(_label, "HH") else "orange")
    highLabelColors = G_for_every(swingHighLabels, _f5)
    G_paint(swingHighLabels, J.obj(("style", "labels_above"), ("color", highLabelColors), ("name", "Swing High Labels")))
    def _f6(_label=J.undefined, *_args):
        if (not J.truthy(_label)):
            return None
        return ("green" if J.seq(_label, "LL") else "lime")
    lowLabelColors = G_for_every(swingLowLabels, _f6)
    G_paint(swingLowLabels, J.obj(("style", "labels_below"), ("color", lowLabelColors), ("name", "Swing Low Labels")))


register_store_indicator(
    script,
    name='dynamic_swing_anchored_vwap_zeiierman_TS',
    title='Dynamic Swing Anchored VWAP (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/68e7b9-dynamic-swing-anchored-vwap-zeiierman/',
    position='price',
    inputs=[{'id': 'swing_period', 'title': 'Swing Period', 'type': 'number', 'default': 30}, {'id': 'adaptive_price_tracking', 'title': 'Adaptive Price Tracking', 'type': 'number', 'default': 20}, {'id': 'adapt_apt_by_atr_ratio', 'title': 'Adapt APT by ATR ratio', 'type': 'boolean', 'default': False}, {'id': 'volatility_bias', 'title': 'Volatility Bias', 'type': 'number', 'default': 10}, {'id': 'swing_high_color', 'title': 'Swing High Color', 'type': 'color', 'default': 'lime'}, {'id': 'swing_low_color', 'title': 'Swing Low Color', 'type': 'color', 'default': 'red'}, {'id': 'vwap_up_color', 'title': 'VWAP Up Color', 'type': 'color', 'default': 'lime'}, {'id': 'vwap_down_color', 'title': 'VWAP Down Color', 'type': 'color', 'default': 'red'}],
    outputs=['dynamic_vwap_up', 'dynamic_vwap_down', 'swing_high_labels', 'swing_low_labels'],
    signals=[],
    requires=[],
    parity='exact',
)
