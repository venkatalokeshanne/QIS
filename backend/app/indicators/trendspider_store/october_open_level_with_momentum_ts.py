"""
October Open Level with Momentum -- TrendSpider store indicator by M4RK4R4.

Registered as "october_open_level_with_momentum_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68dd45-october-open-level-with-momentum/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_momentum = G["momentum"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("October Open Level with Momentum")
    lineColor = J.get(G_input, "color")("Line Color", "teal")
    colorCandles = J.get(G_input, "boolean")("Color Candles", True)
    candleColorPositiveMomentum = J.get(G_input, "color")("Candle Color (Positive Momentum)", "lightgreen")
    candleColorZeroMomentum = J.get(G_input, "color")("Candle Color (Zero Momentum)", "darkgreen")
    candleColorNegativeMomentum = J.get(G_input, "color")("Candle Color (Negative Momentum)", "green")
    candleColorTouchingLevel = J.get(G_input, "color")("Candle Color (Touching Level)", "#39FF14")
    momentumLength = J.get(G_input, "number")("Momentum Length", 14, J.obj(("min", 1), ("max", 50)))
    def isOctober(timestamp=J.undefined, *_args):
        date = G_time_of(timestamp)
        return J.seq(J.get(date, "month"), 10)
    octoberOpenLevels = J.JSArray([])
    currentOctoberOpen = None
    currentYear = None
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        date = G_time_of(J.get(G_time, i))
        if J.truthy(isOctober(J.get(G_time, i))):
            if (currentOctoberOpen is None):
                currentOctoberOpen = J.get(G_open, i)
                currentYear = J.get(date, "year")
                J.get(octoberOpenLevels, "push")(J.obj(("startIndex", i), ("level", currentOctoberOpen), ("year", currentYear)))
        else:
            currentOctoberOpen = None
        i = J.inc(i)
    levelSeries = G_series_of(None)
    i_2 = 0
    while J.lt(i_2, J.get(octoberOpenLevels, "length")):
        currentLevel = J.get(octoberOpenLevels, i_2)
        nextLevel = J.get(octoberOpenLevels, J.add(i_2, 1))
        endIndex = (J.sub(J.get(nextLevel, "startIndex"), 1) if J.truthy(nextLevel) else J.sub(J.get(G_time, "length"), 1))
        j = J.get(currentLevel, "startIndex")
        while J.le(j, endIndex):
            J.set(levelSeries, j, J.get(currentLevel, "level"))
            j = J.inc(j)
        i_2 = J.inc(i_2)
    lineId = G_paint(levelSeries, J.obj(("name", "October Open Level"), ("color", lineColor), ("style", "line")))
    i_3 = 0
    while J.lt(i_3, J.get(octoberOpenLevels, "length")):
        currentLevel_2 = J.get(octoberOpenLevels, i_3)
        nextLevel_2 = J.get(octoberOpenLevels, J.add(i_3, 1))
        endIndex_2 = (J.sub(J.get(nextLevel_2, "startIndex"), 1) if J.truthy(nextLevel_2) else J.sub(J.get(G_time, "length"), 1))
        G_paint_label_at_line(lineId, J.get(currentLevel_2, "startIndex"), J.get(J.get(currentLevel_2, "year"), "toString")(), J.obj(("color", lineColor), ("vertical_align", "top")))
        G_paint_label_at_line(lineId, endIndex_2, J.get(J.get(currentLevel_2, "year"), "toString")(), J.obj(("color", lineColor), ("vertical_align", "bottom")))
        i_3 = J.inc(i_3)
    myMomentum = G_momentum(G_close, momentumLength)
    if J.truthy(colorCandles):
        def _f1(_close=J.undefined, _high=J.undefined, _low=J.undefined, _level=J.undefined, _momentum=J.undefined, *_args):
            if (_level is not None):
                if (J.ge(_high, _level) and J.le(_low, _level)):
                    return candleColorTouchingLevel
                elif J.le(_close, _level):
                    if J.gt(_momentum, 0):
                        return candleColorPositiveMomentum
                    elif J.lt(_momentum, 0):
                        return candleColorNegativeMomentum
                    else:
                        return candleColorZeroMomentum
            return None
        candleColors = G_for_every(G_close, G_high, G_low, levelSeries, myMomentum, _f1)
        G_color_candles(candleColors)
    else:
        G_color_candles(G_series_of(None))


register_store_indicator(
    script,
    name='october_open_level_with_momentum_TS',
    title='October Open Level with Momentum',
    developer='M4RK4R4',
    url='https://trendspider.com/trading-tools-store/indicators/68dd45-october-open-level-with-momentum/',
    position='price',
    inputs=[{'id': 'line_color', 'title': 'Line Color', 'type': 'color', 'default': 'teal'}, {'id': 'color_candles', 'title': 'Color Candles', 'type': 'boolean', 'default': True}, {'id': 'candle_color__positive_momentum_', 'title': 'Candle Color (Positive Momentum)', 'type': 'color', 'default': 'lightgreen'}, {'id': 'candle_color__zero_momentum_', 'title': 'Candle Color (Zero Momentum)', 'type': 'color', 'default': 'darkgreen'}, {'id': 'candle_color__negative_momentum_', 'title': 'Candle Color (Negative Momentum)', 'type': 'color', 'default': 'green'}, {'id': 'candle_color__touching_level_', 'title': 'Candle Color (Touching Level)', 'type': 'color', 'default': '#39FF14'}, {'id': 'momentum_length', 'title': 'Momentum Length', 'type': 'number', 'default': 14}],
    outputs=['october_open_level', 'cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
