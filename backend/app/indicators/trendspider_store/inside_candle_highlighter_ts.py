"""
Inside Candle Highlighter -- TrendSpider store indicator by TrendSpider Team.

Registered as "inside_candle_highlighter_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/inside-candle-highlighter/)
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
    G_high = G["high"]
    G_low = G["low"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("Inside Candle Highlighter", "candles")
    COLOR_INSIDE = "blue"
    isInsideCandle = G_series_of(False)
    candleColors = G_series_of(None)
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        if (J.lt(J.get(G_high, i), J.get(G_high, J.sub(i, 1))) and J.gt(J.get(G_low, i), J.get(G_low, J.sub(i, 1)))):
            J.set(isInsideCandle, i, True)
            J.set(candleColors, i, COLOR_INSIDE)
        i = J.inc(i)
    G_color_candles(candleColors)
    G_register_signal(isInsideCandle, "Inside Candle")


register_store_indicator(
    script,
    name='inside_candle_highlighter_TS',
    title='Inside Candle Highlighter',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/inside-candle-highlighter/',
    position='price',
    inputs=[],
    outputs=['cdl', 'inside_candle'],
    signals=['inside_candle'],
    requires=[],
    parity='exact',
)
