"""
Moving Average Trend Identifier -- TrendSpider store indicator by TrendSpider Team.

Registered as "moving_average_trend_identifier_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/moving-average-trend-identifier/)
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
    G_open = G["open"]
    G_register_signal = G["register_signal"]
    G_sma = G["sma"]
    G_describe_indicator("Moving Average Trend Identifier")
    lengths = J.JSArray([10, 20, 50, 100, 200])
    def _f1(length=J.undefined, *_args):
        return G_sma(G_close, length)
    mas = J.get(lengths, "map")(_f1)
    def isAboveAll(value=J.undefined, maValues=J.undefined, *_args):
        def _f1(ma=J.undefined, *_args):
            return J.gt(value, ma)
        return J.get(maValues, "every")(_f1)
    def isBelowAll(value=J.undefined, maValues=J.undefined, *_args):
        def _f1(ma=J.undefined, *_args):
            return J.lt(value, ma)
        return J.get(maValues, "every")(_f1)
    def _f2(o=J.undefined, c=J.undefined, __=J.undefined, i=J.undefined, *_args):
        def _f1(ma=J.undefined, *_args):
            return J.get(ma, i)
        maValues = J.get(mas, "map")(_f1)
        if (J.truthy(isAboveAll(o, maValues)) and J.truthy(isAboveAll(c, maValues))):
            return "#2fcc56"
        elif (J.truthy(isBelowAll(o, maValues)) and J.truthy(isBelowAll(c, maValues))):
            return "red"
        else:
            return "grey"
    candleColors = G_for_every(G_open, G_close, _f2)
    G_color_candles(candleColors)
    def _f3(color=J.undefined, *_args):
        return (1 if J.seq(color, "#2fcc56") else 0)
    greenSignal = G_for_every(candleColors, _f3)
    def _f4(color=J.undefined, *_args):
        return (1 if J.seq(color, "red") else 0)
    redSignal = G_for_every(candleColors, _f4)
    def _f5(color=J.undefined, *_args):
        return (1 if J.seq(color, "grey") else 0)
    greySignal = G_for_every(candleColors, _f5)
    G_register_signal(greenSignal, "Green Candle Signal")
    G_register_signal(redSignal, "Red Candle Signal")
    G_register_signal(greySignal, "Grey Candle Signal")


register_store_indicator(
    script,
    name='moving_average_trend_identifier_TS',
    title='Moving Average Trend Identifier',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/moving-average-trend-identifier/',
    position='price',
    inputs=[],
    outputs=['cdl', 'green_candle_signal', 'red_candle_signal', 'grey_candle_signal'],
    signals=['green_candle_signal', 'red_candle_signal', 'grey_candle_signal'],
    requires=[],
    parity='exact',
)
