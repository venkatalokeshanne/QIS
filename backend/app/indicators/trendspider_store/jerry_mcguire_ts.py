"""
Jerry McGuire -- TrendSpider store indicator by James Chambers.

Registered as "jerry_mcguire_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/jerry-mcguire/)
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
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_describe_indicator("Jerry McGuire")
    lengthShort = 8
    lengthLong = 21
    emaShort = G_ema(G_close, lengthShort)
    emaLong = G_ema(G_close, lengthLong)
    def _f1(price=J.undefined, shortEMA=J.undefined, longEMA=J.undefined, *_args):
        if (J.gt(price, shortEMA) and J.gt(price, longEMA)):
            return "green"
        elif (J.gt(price, shortEMA) and J.lt(price, longEMA)):
            return "yellow"
        elif (J.lt(price, shortEMA) and J.gt(price, longEMA)):
            return "orange"
        elif (J.lt(price, shortEMA) and J.lt(price, longEMA)):
            return "red"
        else:
            return None
    candleColors = G_for_every(G_close, emaShort, emaLong, _f1)
    G_color_candles(candleColors)


register_store_indicator(
    script,
    name='jerry_mcguire_TS',
    title='Jerry McGuire',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/jerry-mcguire/',
    position='price',
    inputs=[],
    outputs=['cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
