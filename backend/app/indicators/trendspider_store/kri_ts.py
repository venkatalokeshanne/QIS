"""
KRI -- TrendSpider store indicator by Chirag Patnaik.

Registered as "kri_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a5e5-kri/)
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
    G_div = G["div"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_sub = G["sub"]
    G_describe_indicator("KRI", "lower")
    fastKairiLength = J.get(G_input, "number")("Length of Kairi Index 0", 7, J.obj(("min", 1)))
    slowKairiLength = J.get(G_input, "number")("Length of Kairi Index 1", 24, J.obj(("min", 1)))
    smaLength = J.get(G_input, "number")("Length of SMA", 24, J.obj(("min", 1)))
    plotSlowKairi = J.get(G_input, "boolean")("Plot Slow Kairi Relative Index?", True)
    def kairiRelativeIndex(source=J.undefined, length=J.undefined, *_args):
        sourceSMA = G_sma(source, length)
        return G_mult(G_div(G_sub(source, sourceSMA), sourceSMA), 100)
    kri0 = kairiRelativeIndex(G_close, fastKairiLength)
    kri1 = kairiRelativeIndex(G_close, slowKairiLength)
    _SMA = G_sma(kri1, smaLength)
    G_paint(kri0, J.obj(("color", "blue"), ("name", "Fast Kairi")))
    G_paint((kri1 if J.truthy(plotSlowKairi) else G_series_of(None)), J.obj(("color", "red"), ("name", "Slow Kairi")))
    G_paint(_SMA, J.obj(("color", "green"), ("name", "Signal Line")))


register_store_indicator(
    script,
    name='kri_TS',
    title='KRI',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a5e5-kri/',
    position='lower',
    inputs=[{'id': 'length_of_kairi_index_0', 'title': 'Length of Kairi Index 0', 'type': 'number', 'default': 7}, {'id': 'length_of_kairi_index_1', 'title': 'Length of Kairi Index 1', 'type': 'number', 'default': 24}, {'id': 'length_of_sma', 'title': 'Length of SMA', 'type': 'number', 'default': 24}, {'id': 'plot_slow_kairi_relative_index_', 'title': 'Plot Slow Kairi Relative Index?', 'type': 'boolean', 'default': True}],
    outputs=['fast_kairi', 'slow_kairi', 'signal_line'],
    signals=[],
    requires=[],
    parity='exact',
)
