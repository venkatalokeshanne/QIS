"""
Distance Between MA's -- TrendSpider store indicator by TrendSpider Team.

Registered as "distance_between_ma_s_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/moving-average-distance/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_describe_indicator("Distance between MAs", "lower", J.obj(("warmup", 250)))
    maType = G_input("MA type", "sma", J.get(G_constants, "ma_types"))
    priceSource = G_input("Price", "close", J.get(G_constants, "price_source_options"))
    length1 = G_input("Length 1", 20, J.obj(("min", 1), ("max", 200)))
    length2 = G_input("Length 2", 50, J.obj(("min", 1), ("max", 200)))
    ma1 = J.get(G_indicators, maType)(J.get(G_prices, priceSource), length1)
    ma2 = J.get(G_indicators, maType)(J.get(G_prices, priceSource), length2)
    def _f1(ma1_2=J.undefined, ma2_2=J.undefined, *_args):
        return J.sub(ma1_2, ma2_2)
    distance = G_for_every(ma1, ma2, _f1)
    def _f2(d=J.undefined, *_args):
        return ("green" if J.gt(d, 0) else "red")
    G_paint(distance, J.obj(("style", "histogram"), ("color", G_for_every(distance, _f2))))


register_store_indicator(
    script,
    name='distance_between_ma_s_TS',
    title="Distance Between MA's",
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/moving-average-distance/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 250}, {'id': 'ma_type', 'title': 'MA type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'price', 'title': 'Price', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'length_1', 'title': 'Length 1', 'type': 'number', 'default': 20}, {'id': 'length_2', 'title': 'Length 2', 'type': 'number', 'default': 50}],
    outputs=['line_1'],
    signals=[],
    requires=[],
    parity='exact',
)
