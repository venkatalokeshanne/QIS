"""
T3 Moving Average -- TrendSpider store indicator by Chirag Patnaik.

Registered as "t3_moving_average_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a1da-t3/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_describe_indicator("T3", "price")
    length = J.get(G_input, "number")("Length", 8, J.obj(("min", 1)))
    factor = J.get(G_input, "number")("Factor", 0.7, J.obj(("min", 0), ("max", 1)))
    highlightMovements = J.get(G_input, "boolean")("Highlight Movements ?", True)
    source = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    mySource = J.get(G_prices, source)
    def gd(data=J.undefined, period=J.undefined, *_args):
        ema1 = G_ema(data, period)
        ema2 = G_ema(ema1, period)
        return G_add(G_mult(ema1, J.add(1, factor)), G_mult(ema2, J.neg(factor)))
    result1 = gd(mySource, length)
    result2 = gd(result1, length)
    t3Value = gd(result2, length)
    def _f1(t=J.undefined, prevT=J.undefined, i=J.undefined, *_args):
        if (not J.truthy(highlightMovements)):
            return "#6d1e7f"
        return ("green" if (J.gt(i, 0) and J.gt(t, prevT)) else "red")
    t3Color = G_for_every(t3Value, _f1)
    G_paint(t3Value, J.obj(("color", t3Color), ("linewidth", 2), ("name", "T3")))


register_store_indicator(
    script,
    name='t3_moving_average_TS',
    title='T3 Moving Average',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a1da-t3/',
    position='price',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 8}, {'id': 'factor', 'title': 'Factor', 'type': 'number', 'default': 0.7}, {'id': 'highlight_movements__', 'title': 'Highlight Movements ?', 'type': 'boolean', 'default': True}, {'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}],
    outputs=['t3'],
    signals=[],
    requires=[],
    parity='exact',
)
