"""
MA Distance% with Price Source -- TrendSpider store indicator by TrendSpider Team.

Registered as "ma_distance_with_price_source_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/ma-distance-with-price-source/)
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
    G_div = G["div"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sub = G["sub"]
    G_describe_indicator("MA Distance% from Close", "lower", J.obj(("decimals", "by_symbol_+1"), ("shortName", "MA Dist")))
    priceSource = J.get(G_input, "select")("Price Source", "low", J.JSArray(["open", "high", "low", "close"]))
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    maLength = J.get(G_input, "number")("MA Length", 200, J.obj(("min", 2), ("max", 250)))
    maPriceSource = J.get(G_input, "select")("MA Price Source", "close", J.JSArray(["open", "high", "low", "close"]))
    price = J.get(G_market, priceSource)
    maPrice = J.get(G_market, maPriceSource)
    computeMA = J.get(G_indicators, maType)
    ma = computeMA(maPrice, maLength)
    distance = G_sub(price, ma)
    distancePercent = G_div(G_mult(distance, 100), ma)
    def _f1(value=J.undefined, *_args):
        return ("green" if J.gt(value, 0) else "red")
    barColors = J.get(distancePercent, "map")(_f1)
    G_paint(distancePercent, J.obj(("name", "MA Distance%"), ("color", barColors), ("style", "histogram")))


register_store_indicator(
    script,
    name='ma_distance_with_price_source_TS',
    title='MA Distance% with Price Source',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/ma-distance-with-price-source/',
    position='lower',
    inputs=[{'id': 'price_source', 'title': 'Price Source', 'type': 'select_wide', 'default': 'low', 'options': ['open', 'high', 'low', 'close']}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'ma_length', 'title': 'MA Length', 'type': 'number', 'default': 200}, {'id': 'ma_price_source', 'title': 'MA Price Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close']}],
    outputs=['ma_distance_'],
    signals=[],
    requires=[],
    parity='exact',
)
