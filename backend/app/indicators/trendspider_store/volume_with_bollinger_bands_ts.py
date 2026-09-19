"""
Volume with Bollinger Bands -- TrendSpider store indicator by James Chambers.

Registered as "volume_with_bollinger_bands_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/volume-with-bollinger-bands/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_stdev = G["stdev"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Volume Bollinger Bands", "lower", J.obj(("decimals", 0), ("shortName", "Vol BB")))
    length = J.get(G_input, "number")("Length", 20, J.obj(("min", 1), ("max", 100)))
    multiplier = J.get(G_input, "number")("Multiplier", 2, J.obj(("min", 0.1), ("max", 5)))
    maVolume = G_sma(G_volume, length)
    stdevVolume = G_stdev(G_volume, length)
    upperBand = G_add(maVolume, G_mult(stdevVolume, multiplier))
    lowerBand = G_sub(maVolume, G_mult(stdevVolume, multiplier))
    G_paint(maVolume, J.obj(("name", "MA Volume"), ("color", "blue"), ("thickness", 2)))
    G_paint(upperBand, J.obj(("name", "Upper Band"), ("color", "red"), ("thickness", 2)))
    G_paint(lowerBand, J.obj(("name", "Lower Band"), ("color", "green"), ("thickness", 2)))
    def _f1(v=J.undefined, *_args):
        return ("grey" if J.gt(v, J.get(maVolume, J.get(G_volume, "indexOf")(v))) else "#999")
    G_paint(G_volume, J.obj(("name", "Volume"), ("style", "histogram"), ("color", J.get(G_volume, "map")(_f1))))
    G_fill(G_paint(upperBand, J.obj(("hidden", True))), G_paint(lowerBand, J.obj(("hidden", True))), "#cccccc", 0.1)


register_store_indicator(
    script,
    name='volume_with_bollinger_bands_TS',
    title='Volume with Bollinger Bands',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/volume-with-bollinger-bands/',
    position='lower',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 20}, {'id': 'multiplier', 'title': 'Multiplier', 'type': 'number', 'default': 2}],
    outputs=['ma_volume', 'upper_band', 'lower_band', 'volume', 'line_6', 'line_7'],
    signals=[],
    requires=[],
    parity='exact',
)
