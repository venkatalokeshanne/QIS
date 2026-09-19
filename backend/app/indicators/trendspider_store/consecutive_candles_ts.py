"""
Consecutive Candles -- TrendSpider store indicator by TrendSpider.

Registered as "consecutive_candles_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69effd-consecutive-candles/)
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
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_describe_indicator("Consecutive Candles", "lower")
    myMode = J.get(G_input, "select")("Mode", "vs. Last close", J.JSArray(["vs. Last close", "Candle Color"]))
    def _f1(currentClose=J.undefined, currentOpen=J.undefined, prevValue=J.undefined, index=J.undefined, *_args):
        if J.seq(index, 0):
            return 0
        isHigherClose = J.undefined
        isLowerClose = J.undefined
        if J.seq(myMode, "vs. Last close"):
            prevClose = J.get(G_close, J.sub(index, 1))
            isHigherClose = J.gt(currentClose, prevClose)
            isLowerClose = J.lt(currentClose, prevClose)
        else:
            isHigherClose = J.gt(currentClose, currentOpen)
            isLowerClose = J.lt(currentClose, currentOpen)
        if J.truthy(isHigherClose):
            return (J.add(prevValue, 1) if J.gt(prevValue, 0) else 1)
        elif J.truthy(isLowerClose):
            return (J.sub(prevValue, 1) if J.lt(prevValue, 0) else (-1))
        else:
            return prevValue
    consecutiveBars = G_for_every(G_close, G_open, _f1)
    def _f2(value=J.undefined, *_args):
        return ("#469e48" if J.ge(value, 0) else "#f34539")
    barColors = G_for_every(consecutiveBars, _f2)
    G_paint(consecutiveBars, J.obj(("style", "column"), ("color", barColors), ("name", "Consecutive Closes")))
    G_paint(G_horizontal_line(0), J.obj(("style", "dotted"), ("color", "gray"), ("thickness", 1), ("name", "Zero Line")))


register_store_indicator(
    script,
    name='consecutive_candles_TS',
    title='Consecutive Candles',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69effd-consecutive-candles/',
    position='lower',
    inputs=[{'id': 'mode', 'title': 'Mode', 'type': 'select_wide', 'default': 'vs. Last close', 'options': ['vs. Last close', 'Candle Color']}],
    outputs=['consecutive_closes', 'zero_line'],
    signals=[],
    requires=[],
    parity='exact',
)
