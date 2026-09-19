"""
PE Ratio Indicator -- TrendSpider store indicator by TrendSpider.

Registered as "pe_ratio_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/pe-ratio-indicator-2/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_sum = G["sum"]
    G_time = G["time"]
    G_describe_indicator("P/E Ratio", "lower")
    epsMathType = G_input("P/E Type", "Trailing", J.JSArray(["Qtr", "Trailing"]))
    earnings = J.get(G_request, "earnings")(J.get(G_constants, "ticker"))
    if (not J.truthy(J.get(G_Array, "isArray")(earnings))):
        return J.undefined
    def _f1(record=J.undefined, *_args):
        return (not J.truthy(J.get(record, "isFuture")))
    pastEarnings = J.get(earnings, "filter")(_f1)
    def _f2(record=J.undefined, *_args):
        return J.get(record, "eps")
    epsSeries = J.get(pastEarnings, "map")(_f2)
    trailingEpsSeries = G_sum(epsSeries, 4)
    values = (epsSeries if J.eq(epsMathType, "Qtr") else trailingEpsSeries)
    def _f3(record=J.undefined, *_args):
        return J.get(record, "timestamp")
    timestamps = J.get(pastEarnings, "map")(_f3)
    epsLanded = G_land_points_onto_series(timestamps, values, G_time, "ge")
    epsInterpolated = G_interpolate_sparse_series(epsLanded, "constant")
    if (J.nullish(J.get(epsInterpolated, J.sub(J.get(epsInterpolated, "length"), 1)))):
        epsInterpolated = G_horizontal_line(J.get(values, J.sub(J.get(values, "length"), 1)))
    def _f4(c=J.undefined, eps=J.undefined, *_args):
        return J.div(c, eps)
    resultingLine = G_for_every(G_close, epsInterpolated, _f4)
    G_paint(resultingLine, J.obj(("name", "PE Ratio"), ("color", "grey")))


register_store_indicator(
    script,
    name='pe_ratio_indicator_TS',
    title='PE Ratio Indicator',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/pe-ratio-indicator-2/',
    position='lower',
    inputs=[{'id': 'p_e_type', 'title': 'P/E Type', 'type': 'select_wide', 'default': 'Trailing', 'options': ['Qtr', 'Trailing']}],
    outputs=['pe_ratio'],
    signals=[],
    requires=['earnings'],
    parity='exact',
)
