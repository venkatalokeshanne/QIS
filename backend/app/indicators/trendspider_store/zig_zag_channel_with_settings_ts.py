"""
Zig Zag Channel with Settings -- TrendSpider store indicator by TrendSpider Team.

Registered as "zig_zag_channel_with_settings_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/zig-zag-channel-with-settings/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_indexed_points_of = G["indexed_points_of"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_line = G["line"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_projection = G["paint_projection"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_zigzag_points = G["zigzag_points"]
    G_describe_indicator("Zig Zag Channel with Settings")
    position = J.get(G_input, "select")("Position", "auto", J.JSArray(["auto", 0, 1, 2, 3, 4, 5]))
    depth = J.get(G_input, "number")("Depth", 20)
    deviation = J.get(G_input, "number")("Deviation", 1)
    backstep = J.get(G_input, "number")("Backstep", 2)
    zigZagPointsObject = G_zigzag_points(depth, deviation, backstep)
    zigZagPoints = G_series_of(None)
    def _f1(pointIndex=J.undefined, *_args):
        return J.set(zigZagPoints, pointIndex, J.get(G_high, pointIndex))
    J.get(J.get(zigZagPointsObject, "highIndexes"), "forEach")(_f1)
    def _f2(pointIndex=J.undefined, *_args):
        return J.set(zigZagPoints, pointIndex, J.get(G_low, pointIndex))
    J.get(J.get(zigZagPointsObject, "lowIndexes"), "forEach")(_f2)
    zigZagLine = G_interpolate_sparse_series(zigZagPoints)
    indexedPointsOfZigZag = G_indexed_points_of(zigZagPoints)
    G_assert((J.gt(J.get(indexedPointsOfZigZag, "length"), 3) if J.truthy(_t3 := indexedPointsOfZigZag) else _t3), J.template("Not enough zig zag points. Try loading more candles or changing timeframe"))
    def computeChannel(position_2=J.undefined, *_args):
        G_assert(J.lt(position_2, J.sub(J.get(indexedPointsOfZigZag, "length"), 3)), J.template("Not enough zig zag points for this position. Try lower position number."))
        A = J.get(indexedPointsOfZigZag, J.sub(J.sub(J.get(indexedPointsOfZigZag, "length"), position_2), 3))
        B = J.get(indexedPointsOfZigZag, J.sub(J.sub(J.get(indexedPointsOfZigZag, "length"), position_2), 2))
        C = J.get(indexedPointsOfZigZag, J.sub(J.sub(J.get(indexedPointsOfZigZag, "length"), position_2), 1))
        startIndex_2 = J.get(A, "candleIndex")
        line1 = G_line(J.get(A, "candleIndex"), J.get(A, "value"), J.get(C, "candleIndex"), J.get(C, "value"))
        distanceBetweenLineACandB = J.sub(J.get(B, "value"), J.get(line1, J.get(B, "candleIndex")))
        line2 = G_add(line1, distanceBetweenLineACandB)
        middleLine_2 = G_add(line1, J.div(distanceBetweenLineACandB, 2))
        line3 = G_add(line1, J.div(distanceBetweenLineACandB, 4))
        line4 = G_add(line1, J.div(J.mul(3, distanceBetweenLineACandB), 4))
        topLine_2 = J.JSArray([])
        bottomLine_2 = J.JSArray([])
        upperQuarterLine_2 = J.JSArray([])
        lowerQuarterLine_2 = J.JSArray([])
        APointIsHigh = J.gt(J.get(A, "value"), J.get(B, "value"))
        if J.truthy(APointIsHigh):
            topLine_2 = line1
            bottomLine_2 = line2
            upperQuarterLine_2 = line3
            lowerQuarterLine_2 = line4
        else:
            topLine_2 = line2
            bottomLine_2 = line1
            upperQuarterLine_2 = line4
            lowerQuarterLine_2 = line3
        return J.obj(("topLine", topLine_2), ("bottomLine", bottomLine_2), ("upperQuarterLine", upperQuarterLine_2), ("lowerQuarterLine", lowerQuarterLine_2), ("middleLine", middleLine_2), ("startIndex", startIndex_2))
    channelObject = J.obj()
    if J.eq(position, "auto"):
        lastIndex = J.sub(J.get(G_close, "length"), 1)
        position = 0
        while J.lt(position, J.sub(J.get(indexedPointsOfZigZag, "length"), 3)):
            testChannel = computeChannel(J.add(position, 1))
            lastCloseIsNotInTheChannel = (_t4 if J.truthy(_t4 := J.lt(J.get(J.get(testChannel, "topLine"), lastIndex), J.get(G_close, lastIndex))) else J.gt(J.get(J.get(testChannel, "bottomLine"), lastIndex), J.get(G_close, lastIndex)))
            if J.truthy(lastCloseIsNotInTheChannel):
                break
            position = J.inc(position)
    channelObject = computeChannel(position)
    _t5 = J.require_object(computeChannel(position))
    topLine = J.get(_t5, "topLine")
    bottomLine = J.get(_t5, "bottomLine")
    upperQuarterLine = J.get(_t5, "upperQuarterLine")
    lowerQuarterLine = J.get(_t5, "lowerQuarterLine")
    middleLine = J.get(_t5, "middleLine")
    startIndex = J.get(_t5, "startIndex")
    topLineRef = G_paint(topLine, "Top Line", "red")
    bottomLineRef = G_paint(bottomLine, "Bottom Line", "green")
    G_fill(topLineRef, bottomLineRef, "blue", 0.1)
    middleLineRef = G_paint(middleLine, "Middle Line", "grey")
    upperQuarterLineRef = G_paint(upperQuarterLine, "Upper Quarter Line", "red")
    lowerQuarterLineRef = G_paint(lowerQuarterLine, "Lower Quarter Line", "green")
    G_paint(zigZagLine, "ZigZag Line", "black")
    def getProjectionSeries(originalLine=J.undefined, *_args):
        return G_add(G_shift(originalLine, J.neg(startIndex)), J.sub(J.get(originalLine, J.sub(J.get(originalLine, "length"), 1)), J.get(originalLine, startIndex)))
    G_fill(G_paint_projection(topLineRef, getProjectionSeries(topLine)), G_paint_projection(bottomLineRef, getProjectionSeries(bottomLine)), "blue", 0.1)
    G_paint_projection(middleLineRef, getProjectionSeries(middleLine))
    G_paint_projection(upperQuarterLineRef, getProjectionSeries(upperQuarterLine))
    G_paint_projection(lowerQuarterLineRef, getProjectionSeries(lowerQuarterLine))


register_store_indicator(
    script,
    name='zig_zag_channel_with_settings_TS',
    title='Zig Zag Channel with Settings',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/zig-zag-channel-with-settings/',
    position='price',
    inputs=[{'id': 'position', 'title': 'Position', 'type': 'select_wide', 'default': 'auto', 'options': ['auto', 0, 1, 2, 3, 4, 5]}, {'id': 'depth', 'title': 'Depth', 'type': 'number', 'default': 20}, {'id': 'deviation', 'title': 'Deviation', 'type': 'number', 'default': 1}, {'id': 'backstep', 'title': 'Backstep', 'type': 'number', 'default': 2}],
    outputs=['top_line', 'bottom_line', 'middle_line', 'upper_quarter_line', 'lower_quarter_line', 'zigzag_line'],
    signals=[],
    requires=[],
    parity='exact',
)
