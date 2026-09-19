"""
Anchored Percentile Line -- TrendSpider store indicator by TrendSpider Team.

Registered as "anchored_percentile_line_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/anchored-percentile-line/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Error = G["Error"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_input_anchor = G["input_anchor"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_series_of = G["series_of"]
    def anchoredPLine(fromIndex=J.undefined, percentileIndex=J.undefined, *_args):
        result = G_series_of(None)
        candleIndex = J.add(fromIndex, 1)
        while J.lt(candleIndex, J.get(price, "length")):
            pricesAccumulated = J.get(price, "slice")(fromIndex, candleIndex)
            def _f1(value=J.undefined, index=J.undefined, *_args):
                return value
            pricesWeigthedByVolume = J.get(pricesAccumulated, "map")(_f1)
            percentileValue = J.get(jstat, "percentile")(pricesWeigthedByVolume, J.div(percentileIndex, 100))
            J.set(result, candleIndex, percentileValue)
            candleIndex = J.add(candleIndex, 1)
        return result
    G_describe_indicator("Percentile Line Anchored", "price", J.obj(("shortName", "Perc. L")))
    priceSource = G_input("Price source", "ohlc4", J.get(G_constants, "price_source_options"))
    candleToAnchorTo = G_input_anchor()
    if (not J.truthy(candleToAnchorTo)):
        raise J.js_throw(G_Error("No suitable anchoring point found"))
    price = J.get(G_prices, priceSource)
    jstat = G_library("jstat")
    p0 = G_paint(anchoredPLine(J.get(candleToAnchorTo, "candleIndex"), 0), J.obj(("color", "blue")))
    p25 = G_paint(anchoredPLine(J.get(candleToAnchorTo, "candleIndex"), 25), J.obj(("color", "navy")))
    p50 = G_paint(anchoredPLine(J.get(candleToAnchorTo, "candleIndex"), 50), J.obj(("color", "black"), ("thickness", 2)))
    p75 = G_paint(anchoredPLine(J.get(candleToAnchorTo, "candleIndex"), 75), J.obj(("color", "navy")))
    p100 = G_paint(anchoredPLine(J.get(candleToAnchorTo, "candleIndex"), 100), J.obj(("color", "blue")))
    G_fill(p0, p25, "skyblue")
    G_fill(p25, p50, "blue")
    G_fill(p50, p75, "blue")
    G_fill(p75, p100, "skyblue")


register_store_indicator(
    script,
    name='anchored_percentile_line_TS',
    title='Anchored Percentile Line',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/anchored-percentile-line/',
    position='price',
    inputs=[{'id': 'price_source', 'title': 'Price source', 'type': 'select_wide', 'default': 'ohlc4', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'anchoring_type', 'title': 'Anchor to', 'type': 'select_wide', 'default': 'highest high', 'options': ['date', 'highest vol.', 'highest high', 'lowest low', 'day to date', 'week to date', 'month to date', 'qtr to date', 'year to date', 'visible range']}, {'id': 'windowSize', 'title': 'Window', 'type': 'integer', 'default': 20}],
    outputs=['line_1', 'line_2', 'line_3', 'line_4', 'line_5'],
    signals=[],
    requires=[],
    parity='exact',
)
