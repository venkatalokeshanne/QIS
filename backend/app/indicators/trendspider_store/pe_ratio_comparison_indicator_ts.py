"""
PE Ratio Comparison Indicator -- TrendSpider store indicator by TrendSpider Team.

Registered as "pe_ratio_comparison_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/pe-ratio-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Boolean = G["Boolean"]
    G_Error = G["Error"]
    G_Math = G["Math"]
    G_Promise = G["Promise"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_max_of = G["max_of"]
    G_min_of = G["min_of"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def computePELine(ticker=J.undefined, options=J.undefined, isReference=J.undefined, *_args):
        earnings = J.get(G_request, "earnings")(ticker)
        otherAssetPrice = J.get(G_request, "history")(ticker, J.get(G_constants, "resolution"), J.obj(("land_onto_current_candles", True)))
        if (not J.truthy(J.get(G_Array, "isArray")(earnings))):
            return J.undefined
        def _f1(record=J.undefined, *_args):
            return (not J.truthy(J.get(record, "isFuture")))
        pastEarnings = J.get(earnings, "filter")(_f1)
        resultingLine = None
        if J.eq(epsMathType, "Qtr"):
            def _f2(record=J.undefined, *_args):
                return J.get(record, "timestamp")
            def _f3(record=J.undefined, *_args):
                return J.get(record, "eps")
            epsLanded = G_land_points_onto_series(J.get(pastEarnings, "map")(_f2), J.get(pastEarnings, "map")(_f3), G_time, "ge")
            epsInterpolated = G_interpolate_sparse_series(epsLanded, "constant")
            def _f4(c=J.undefined, eps=J.undefined, *_args):
                return J.div(c, eps)
            resultingLine = G_for_every(J.get(otherAssetPrice, "close"), epsInterpolated, _f4)
        elif J.eq(epsMathType, "Trailing"):
            def _f5(c=J.undefined, index=J.undefined, *_args):
                def _f1(result=J.undefined, report=J.undefined, *_args):
                    return J.add(result, J.get(report, "eps"))
                last4QtrEPS = J.get(J.get(J.get(J.get(pastEarnings, "slice")(0, index), "filter")(G_Boolean), "slice")((-4)), "reduce")(_f1, 0)
                return J.div(c, last4QtrEPS)
            resultingLine = J.get(J.get(otherAssetPrice, "close"), "map")(_f5)
        else:
            raise J.js_throw(G_Error("unknown pe type requested"))
        if J.eq(scale, "Log"):
            resultingLine = J.get(resultingLine, "map")(J.get(G_Math, "log"))
        return J.obj(("line", resultingLine), ("options", options), ("isReference", isReference))
    G_describe_indicator("P/E Ratio Comparison", "lower")
    symbolsToCompareTo = J.JSArray(["MSFT", "AAPL", "GOOGL", "NVDA", "TSLA"])
    epsMathType = G_input("P/E Type", "Trailing", J.JSArray(["Qtr", "Trailing"]))
    scale = G_input("Scale", "Linear", J.JSArray(["Linear", "Log"]))
    def _f1(symbol=J.undefined, *_args):
        return computePELine(symbol, J.obj(("name", J.template("PE, ", symbol))), True)
    ratios = J.get(G_Promise, "all")(J.JSArray([computePELine(J.get(G_constants, "ticker"), J.obj(("name", "PE, Base"), ("thickness", 2)), False), *J.spread(J.get(symbolsToCompareTo, "map")(_f1))]))
    maxLine = G_series_of((-1000000))
    minLine = G_series_of(1000000)
    for ratioLine in J.iter_of(ratios):
        G_paint(J.get(ratioLine, "line"), J.get(ratioLine, "options"))
        if J.truthy(J.get(ratioLine, "isReference")):
            maxLine = G_max_of(maxLine, J.get(ratioLine, "line"))
            minLine = G_min_of(minLine, J.get(ratioLine, "line"))
    G_fill(G_paint(maxLine, J.obj(("hidden", True))), G_paint(minLine, J.obj(("hidden", True))), "blue", 0.1)


register_store_indicator(
    script,
    name='pe_ratio_comparison_indicator_TS',
    title='PE Ratio Comparison Indicator',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/pe-ratio-indicator/',
    position='lower',
    inputs=[{'id': 'p_e_type', 'title': 'P/E Type', 'type': 'select_wide', 'default': 'Trailing', 'options': ['Qtr', 'Trailing']}, {'id': 'scale', 'title': 'Scale', 'type': 'select_wide', 'default': 'Linear', 'options': ['Linear', 'Log']}],
    outputs=['pe__base', 'pe__msft', 'pe__aapl', 'pe__googl', 'pe__nvda', 'pe__tsla', 'line_7', 'line_8'],
    signals=[],
    requires=['earnings', 'history'],
    parity='exact',
)
