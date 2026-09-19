"""
Dollar Volume -- TrendSpider store indicator by TrendSpider.

Registered as "dollar_volume_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69f3a5-dollar-volume/)
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
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_volume = G["volume"]
    G_describe_indicator("Dollar Volume", "lower")
    myDollarVolume = G_mult(G_close, G_volume)
    G_paint(myDollarVolume, J.obj(("name", "Dollar Volume"), ("color", "green"), ("style", "column")))


register_store_indicator(
    script,
    name='dollar_volume_TS',
    title='Dollar Volume',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69f3a5-dollar-volume/',
    position='lower',
    inputs=[],
    outputs=['dollar_volume'],
    signals=[],
    requires=[],
    parity='exact',
)
