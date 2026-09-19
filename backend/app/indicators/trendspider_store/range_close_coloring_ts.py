"""
Range Close Coloring -- TrendSpider store indicator by TrendSpider Team.

Registered as "range_close_coloring_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/range-close-coloring/)
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
    G_register_signal = G["register_signal"]
    G_describe_indicator("Range Close Coloring")
    myThresholdPercent = J.get(G_input, "number")("Threshold %", 25, J.obj(("min", 0), ("max", 100)))
    myCandleColor = J.get(G_input, "color")("Candle Color", "yellow")
    myThreshold = J.div(myThresholdPercent, 100)
    def _f1(_h=J.undefined, _l=J.undefined, _c=J.undefined, *_args):
        myCandleRange = J.sub(_h, _l)
        if J.seq(myCandleRange, 0):
            return 0
        return J.div(J.sub(_h, _c), myCandleRange)
    myCloseToHighRatio = G_for_every(G_high, G_low, G_close, _f1)
    def _f2(_ratio=J.undefined, *_args):
        return (myCandleColor if J.le(_ratio, myThreshold) else None)
    myColors = G_for_every(myCloseToHighRatio, _f2)
    G_color_candles(myColors)
    def _f3(_ratio=J.undefined, *_args):
        return J.le(_ratio, myThreshold)
    mySignal = G_for_every(myCloseToHighRatio, _f3)
    G_register_signal(mySignal, "Close Near High")


register_store_indicator(
    script,
    name='range_close_coloring_TS',
    title='Range Close Coloring',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/range-close-coloring/',
    position='price',
    inputs=[{'id': 'threshold__', 'title': 'Threshold %', 'type': 'number', 'default': 25}, {'id': 'candle_color', 'title': 'Candle Color', 'type': 'color', 'default': 'yellow'}],
    outputs=['cdl', 'close_near_high'],
    signals=['close_near_high'],
    requires=[],
    parity='exact',
)
