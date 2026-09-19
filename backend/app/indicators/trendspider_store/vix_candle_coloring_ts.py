"""
VIX Candle Coloring -- TrendSpider store indicator by TrendSpider.

Registered as "vix_candle_coloring_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69effc-vix-candle-coloring/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("VIX Candle Coloring")
    vixData = J.get(G_request, "history")("$VIX", J.get(G_current, "resolution"))
    G_assert((not J.truthy(J.get(vixData, "error"))), J.template("Error fetching VIX data: ", J.get(vixData, "error")))
    vixLanded = G_land_points_onto_series(J.get(vixData, "time"), J.get(vixData, "close"), G_time, "ge")
    vixInterpolated = G_interpolate_sparse_series(vixLanded, "constant")
    def _f1(vixValue=J.undefined, *_args):
        if (vixValue is None):
            return None
        if J.ge(vixValue, 50):
            return "#FF3B30"
        if J.ge(vixValue, 30):
            return "#FF6A00"
        if J.ge(vixValue, 25):
            return "#FFB020"
        if J.ge(vixValue, 20):
            return "#00C2FF"
        return "#00C853"
    candleColors = J.get(vixInterpolated, "map")(_f1)
    G_color_candles(candleColors)


register_store_indicator(
    script,
    name='vix_candle_coloring_TS',
    title='VIX Candle Coloring',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69effc-vix-candle-coloring/',
    position='price',
    inputs=[],
    outputs=['cdl'],
    signals=[],
    requires=['history'],
    parity='exact',
)
