"""
Market Structure Break (MSB) Indicator -- TrendSpider store indicator by TrendSpider Team.

Registered as "market_structure_break_msb_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/market-structure-break-msb-indicator/)
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
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_describe_indicator("Market Structure Break (MSB) Detector")
    swingLookback = J.get(G_input, "number")("Swing Lookback", 3, J.obj(("min", 2)))
    bullishColor = J.get(G_input, "color")("Bullish MSB Color", "#00FF00")
    bearishColor = J.get(G_input, "color")("Bearish MSB Color", "#FF0000")
    lineLength = J.get(G_input, "number")("MSB Line Length (bars)", 20, J.obj(("min", 10), ("max", 200)))
    msbLookback = J.get(G_input, "number")("MSB Lookback Period", 100, J.obj(("min", 1), ("max", 1000)))
    def detectSwings(high=J.undefined, low=J.undefined, lookback=J.undefined, *_args):
        swingHighs_2 = G_series_of(None)
        swingLows_2 = G_series_of(None)
        i = lookback
        while J.lt(i, J.sub(J.get(high, "length"), lookback)):
            isSwingHigh = True
            isSwingLow = True
            j = 1
            while J.le(j, lookback):
                if (J.ge(J.get(high, J.sub(i, j)), J.get(high, i)) or J.ge(J.get(high, J.add(i, j)), J.get(high, i))):
                    isSwingHigh = False
                if (J.le(J.get(low, J.sub(i, j)), J.get(low, i)) or J.le(J.get(low, J.add(i, j)), J.get(low, i))):
                    isSwingLow = False
                j = J.inc(j)
            if J.truthy(isSwingHigh):
                J.set(swingHighs_2, i, J.get(high, i))
            if J.truthy(isSwingLow):
                J.set(swingLows_2, i, J.get(low, i))
            i = J.inc(i)
        return J.obj(("swingHighs", swingHighs_2), ("swingLows", swingLows_2))
    _t1 = J.require_object(detectSwings(G_high, G_low, swingLookback))
    swingHighs = J.get(_t1, "swingHighs")
    swingLows = J.get(_t1, "swingLows")
    bullishMSB = G_series_of(None)
    bearishMSB = G_series_of(None)
    bullishMSBLines = J.JSArray([])
    bearishMSBLines = J.JSArray([])
    lastSwingHighIndex = None
    lastSwingLowIndex = None
    i = swingLookback
    while J.lt(i, J.get(G_close, "length")):
        if (J.get(swingHighs, i) is not None):
            lastSwingHighIndex = i
        if (J.get(swingLows, i) is not None):
            lastSwingLowIndex = i
        if ((lastSwingHighIndex is not None) and J.gt(J.get(G_close, i), J.get(G_high, lastSwingHighIndex))):
            J.set(bullishMSB, i, J.get(G_high, lastSwingHighIndex))
            J.get(bullishMSBLines, "push")(J.obj(("startIndex", lastSwingHighIndex), ("breakIndex", i), ("value", J.get(G_high, lastSwingHighIndex))))
            lastSwingHighIndex = None
        if ((lastSwingLowIndex is not None) and J.lt(J.get(G_close, i), J.get(G_low, lastSwingLowIndex))):
            J.set(bearishMSB, i, J.get(G_low, lastSwingLowIndex))
            J.get(bearishMSBLines, "push")(J.obj(("startIndex", lastSwingLowIndex), ("breakIndex", i), ("value", J.get(G_low, lastSwingLowIndex))))
            lastSwingLowIndex = None
        i = J.inc(i)
    def createLine(startIndex=J.undefined, breakIndex=J.undefined, value=J.undefined, color=J.undefined, isBullish=J.undefined, lineIndex=J.undefined, *_args):
        lineData = G_series_of(None)
        endIndex = J.get(G_Math, "min")(J.add(breakIndex, lineLength), J.get(G_close, "length"))
        i_2 = startIndex
        while J.lt(i_2, endIndex):
            J.set(lineData, i_2, value)
            i_2 = J.inc(i_2)
        paintedLine = G_paint(lineData, J.obj(("color", color), ("name", J.template(("Bullish" if J.truthy(isBullish) else "Bearish"), " MSB ", lineIndex))))
        labelIndex = (startIndex if J.truthy(isBullish) else startIndex)
        G_paint_label_at_line(paintedLine, labelIndex, "MSB", J.obj(("color", color), ("vertical_align", ("top" if J.truthy(isBullish) else "bottom"))))
    currentIndex = J.sub(J.get(G_close, "length"), 1)
    msbLookbackStartIndex = J.get(G_Math, "max")(0, J.sub(currentIndex, msbLookback))
    def _f2(line=J.undefined, *_args):
        return J.ge(J.get(line, "breakIndex"), msbLookbackStartIndex)
    def _f3(line=J.undefined, index=J.undefined, *_args):
        createLine(J.get(line, "startIndex"), J.get(line, "breakIndex"), J.get(line, "value"), bullishColor, True, index)
    J.get(J.get(bullishMSBLines, "filter")(_f2), "forEach")(_f3)
    def _f4(line=J.undefined, *_args):
        return J.ge(J.get(line, "breakIndex"), msbLookbackStartIndex)
    def _f5(line=J.undefined, index=J.undefined, *_args):
        createLine(J.get(line, "startIndex"), J.get(line, "breakIndex"), J.get(line, "value"), bearishColor, False, index)
    J.get(J.get(bearishMSBLines, "filter")(_f4), "forEach")(_f5)


register_store_indicator(
    script,
    name='market_structure_break_msb_indicator_TS',
    title='Market Structure Break (MSB) Indicator',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/market-structure-break-msb-indicator/',
    position='price',
    inputs=[{'id': 'swing_lookback', 'title': 'Swing Lookback', 'type': 'number', 'default': 3}, {'id': 'bullish_msb_color', 'title': 'Bullish MSB Color', 'type': 'color', 'default': '#00FF00'}, {'id': 'bearish_msb_color', 'title': 'Bearish MSB Color', 'type': 'color', 'default': '#FF0000'}, {'id': 'msb_line_length__bars_', 'title': 'MSB Line Length (bars)', 'type': 'number', 'default': 20}, {'id': 'msb_lookback_period', 'title': 'MSB Lookback Period', 'type': 'number', 'default': 100}],
    outputs=['bullish_msb_0', 'bullish_msb_1', 'bullish_msb_2', 'bullish_msb_3', 'bullish_msb_4', 'bullish_msb_5', 'bearish_msb_0'],
    signals=[],
    requires=[],
    parity='exact',
)
