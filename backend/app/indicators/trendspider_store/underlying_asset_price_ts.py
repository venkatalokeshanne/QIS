"""
Underlying asset price -- TrendSpider store indicator by TrendSpider.

Registered as "underlying_asset_price_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a2030-underlying-asset-price/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Underlying asset price", "lower")
    if J.truthy(J.get(G_current, "root")):
        underlyingData = J.get(G_request, "history")(J.get(G_current, "root"), J.get(G_current, "resolution"))
        G_assert((not J.truthy(J.get(underlyingData, "error"))), J.template("Error fetching underlying data: ", J.get(underlyingData, "error")))
        underlyingLanded = G_land_points_onto_series(J.get(underlyingData, "time"), J.get(underlyingData, "close"), G_time, "ge")
        underlyingInterpolated = G_interpolate_sparse_series(underlyingLanded, "constant")
        G_paint(underlyingInterpolated, J.obj(("name", J.template("Underlying")), ("color", "blue"), ("style", "line")))
    else:
        raise J.js_throw("Only applicable to options")


register_store_indicator(
    script,
    name='underlying_asset_price_TS',
    title='Underlying asset price',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/6a2030-underlying-asset-price/',
    position='lower',
    inputs=[],
    outputs=['underlying'],
    signals=[],
    requires=['history'],
    parity='exact',
)
