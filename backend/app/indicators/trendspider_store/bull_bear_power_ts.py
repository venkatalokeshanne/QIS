"""
Bull Bear Power -- TrendSpider store indicator by James Chambers.

Registered as "bull_bear_power_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/bull-bear-power/)
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
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_describe_indicator("Bull Bear Power", "lower")
    lengthInput = G_input("Length", 13, J.obj(("min", 2), ("max", 50)))
    highPrices = G_high
    lowPrices = G_low
    closePrices = G_close
    closeEMA = G_ema(closePrices, lengthInput)
    def _f1(high=J.undefined, emaClose=J.undefined, *_args):
        return J.sub(high, emaClose)
    bullPower = G_for_every(highPrices, closeEMA, _f1)
    def _f2(low=J.undefined, emaClose=J.undefined, *_args):
        return J.sub(low, emaClose)
    bearPower = G_for_every(lowPrices, closeEMA, _f2)
    def _f3(bull=J.undefined, bear=J.undefined, *_args):
        return J.add(bull, bear)
    bbp = G_for_every(bullPower, bearPower, _f3)
    def _f4(value=J.undefined, *_args):
        return ("green" if J.ge(value, 0) else "red")
    G_paint(bbp, "BBPower", G_for_every(bbp, _f4), "histogram")


register_store_indicator(
    script,
    name='bull_bear_power_TS',
    title='Bull Bear Power',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/bull-bear-power/',
    position='lower',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 13}],
    outputs=['bbpower'],
    signals=[],
    requires=[],
    parity='exact',
)
