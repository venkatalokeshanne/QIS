"""
CandleStick Pattern Detection & Emojis -- TrendSpider store indicator by TrendSpider Team.

Registered as "candlestick_pattern_detection_emojis_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/candlestick-pattern-detection-emojis/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    MY_PATTERN = "\ud83d\ude21\ud83d\ude21\ud83d\ude24{1,3}(\ud83d\ude18|\ud83d\ude1a)+"
    G_describe_indicator(J.template("CandleStick Pattern Detection & Emojis ", MY_PATTERN))
    atrSeries = G_atr(14)
    def candleLabel(candleIndex=J.undefined, *_args):
        if J.gt(J.get(G_close, candleIndex), J.add(J.get(G_close, J.sub(candleIndex, 1)), J.get(atrSeries, J.sub(candleIndex, 1)))):
            return "\ud83d\ude18"
        if J.gt(J.get(G_close, candleIndex), J.get(G_close, J.sub(candleIndex, 1))):
            return "\ud83d\ude1a"
        if J.lt(J.get(G_close, candleIndex), J.sub(J.get(G_close, J.sub(candleIndex, 1)), J.get(atrSeries, J.sub(candleIndex, 1)))):
            return "\ud83d\ude21"
        if J.lt(J.get(G_close, candleIndex), J.get(G_close, J.sub(candleIndex, 1))):
            return "\ud83d\ude24"
        return ("\ud83d\ude0f" if J.gt(J.get(G_close, candleIndex), J.get(G_open, candleIndex)) else "\ud83d\ude29")
    def _f1(dummy=J.undefined, index=J.undefined, *_args):
        return candleLabel(index)
    codesOfCandles = J.get(G_close, "map")(_f1)
    codesAsString = J.get(codesOfCandles, "join")("")
    borderUp = G_series_of(None)
    borderDown = G_series_of(None)
    for occurence in J.iter_of(J.get(codesAsString, "matchAll")(MY_PATTERN)):
        thisPattern = J.get(occurence, 0)
        patternStartSymbols = J.div(J.get(occurence, "index"), 2)
        patternLengthSymbols = J.div(J.get(thisPattern, "length"), 2)
        patternEndIndex = J.add(patternStartSymbols, patternLengthSymbols)
        hh = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(patternStartSymbols, patternEndIndex)))
        def _f2(*_args):
            return hh
        J.get(borderUp, "splice")(J.sub(patternStartSymbols, 1), J.add(patternLengthSymbols, 2), *J.spread(J.get(J.JSArray([*J.spread(G_Array(J.add(patternLengthSymbols, 2)))]), "map")(_f2)))
        ll = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(patternStartSymbols, patternEndIndex)))
        def _f3(*_args):
            return ll
        J.get(borderDown, "splice")(J.sub(patternStartSymbols, 1), J.add(patternLengthSymbols, 2), *J.spread(J.get(J.JSArray([*J.spread(G_Array(J.add(patternLengthSymbols, 2)))]), "map")(_f3)))
    G_paint(codesOfCandles, J.obj(("style", "labels_above"), ("fontSize", 20)))
    G_fill(G_paint(borderUp, J.obj(("name", "Up"), ("color", "blue"))), G_paint(borderDown, J.obj(("name", "Down"), ("color", "blue"))), "blue")


register_store_indicator(
    script,
    name='candlestick_pattern_detection_emojis_TS',
    title='CandleStick Pattern Detection & Emojis',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/candlestick-pattern-detection-emojis/',
    position='price',
    inputs=[],
    outputs=['line_1', 'up', 'down'],
    signals=[],
    requires=[],
    parity='exact',
)
