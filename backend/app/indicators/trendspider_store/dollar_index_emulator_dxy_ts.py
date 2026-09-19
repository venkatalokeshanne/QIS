"""
Dollar Index Emulator (DXY) -- TrendSpider store indicator by TrendSpider Team.

Registered as "dollar_index_emulator_dxy_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6980e0-dollar-index-emulator-dxy/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: ULP.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Dollar Index Emulator (DXY)", "lower")
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([J.get(G_request, "history")("^EURUSD", J.get(G_current, "resolution")), J.get(G_request, "history")("^USDJPY", J.get(G_current, "resolution")), J.get(G_request, "history")("^GBPUSD", J.get(G_current, "resolution")), J.get(G_request, "history")("^USDCAD", J.get(G_current, "resolution")), J.get(G_request, "history")("^USDSEK", J.get(G_current, "resolution")), J.get(G_request, "history")("^USDCHF", J.get(G_current, "resolution"))])))
    eurusdData = (_t1[0] if 0 < len(_t1) else J.undefined)
    usdjpyData = (_t1[1] if 1 < len(_t1) else J.undefined)
    gbpusdData = (_t1[2] if 2 < len(_t1) else J.undefined)
    usdcadData = (_t1[3] if 3 < len(_t1) else J.undefined)
    usdsekData = (_t1[4] if 4 < len(_t1) else J.undefined)
    usdchfData = (_t1[5] if 5 < len(_t1) else J.undefined)
    G_assert((not J.truthy(J.get(eurusdData, "error"))), J.add("Error fetching EURUSD data: ", J.get(eurusdData, "error")))
    G_assert((not J.truthy(J.get(usdjpyData, "error"))), J.add("Error fetching USDJPY data: ", J.get(usdjpyData, "error")))
    G_assert((not J.truthy(J.get(gbpusdData, "error"))), J.add("Error fetching GBPUSD data: ", J.get(gbpusdData, "error")))
    G_assert((not J.truthy(J.get(usdcadData, "error"))), J.add("Error fetching USDCAD data: ", J.get(usdcadData, "error")))
    G_assert((not J.truthy(J.get(usdsekData, "error"))), J.add("Error fetching USDSEK data: ", J.get(usdsekData, "error")))
    G_assert((not J.truthy(J.get(usdchfData, "error"))), J.add("Error fetching USDCHF data: ", J.get(usdchfData, "error")))
    myMinLength = J.get(G_Math, "min")(J.get(J.get(eurusdData, "close"), "length"), J.get(J.get(usdjpyData, "close"), "length"), J.get(J.get(gbpusdData, "close"), "length"), J.get(J.get(usdcadData, "close"), "length"), J.get(J.get(usdsekData, "close"), "length"), J.get(J.get(usdchfData, "close"), "length"))
    eurusdSliced = J.get(J.get(eurusdData, "close"), "slice")(J.neg(myMinLength))
    usdjpySliced = J.get(J.get(usdjpyData, "close"), "slice")(J.neg(myMinLength))
    gbpusdSliced = J.get(J.get(gbpusdData, "close"), "slice")(J.neg(myMinLength))
    usdcadSliced = J.get(J.get(usdcadData, "close"), "slice")(J.neg(myMinLength))
    usdsekSliced = J.get(J.get(usdsekData, "close"), "slice")(J.neg(myMinLength))
    usdchfSliced = J.get(J.get(usdchfData, "close"), "slice")(J.neg(myMinLength))
    timeSliced = J.get(J.get(eurusdData, "time"), "slice")(J.neg(myMinLength))
    def _f2(_eurusd=J.undefined, _usdjpy=J.undefined, _gbpusd=J.undefined, _usdcad=J.undefined, _usdsek=J.undefined, _usdchf=J.undefined, *_args):
        if ((((((_eurusd is None) or (_usdjpy is None)) or (_gbpusd is None)) or (_usdcad is None)) or (_usdsek is None)) or (_usdchf is None)):
            return None
        return J.mul(J.mul(J.mul(J.mul(J.mul(J.mul(50.14348112, J.get(G_Math, "pow")(_eurusd, (-0.576))), J.get(G_Math, "pow")(_usdjpy, 0.136)), J.get(G_Math, "pow")(_gbpusd, (-0.119))), J.get(G_Math, "pow")(_usdcad, 0.091)), J.get(G_Math, "pow")(_usdsek, 0.042)), J.get(G_Math, "pow")(_usdchf, 0.036))
    myFormulaResult = G_for_every(eurusdSliced, usdjpySliced, gbpusdSliced, usdcadSliced, usdsekSliced, usdchfSliced, _f2)
    formulaLanded = G_land_points_onto_series(timeSliced, myFormulaResult, G_time, "ge")
    formulaInterpolated = G_interpolate_sparse_series(formulaLanded, "constant")
    G_paint(formulaInterpolated, J.obj(("name", "Currency Formula"), ("color", "blue")))


register_store_indicator(
    script,
    name='dollar_index_emulator_dxy_TS',
    title='Dollar Index Emulator (DXY)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/6980e0-dollar-index-emulator-dxy/',
    position='lower',
    inputs=[],
    outputs=['currency_formula'],
    signals=[],
    requires=['history'],
    parity='aapl_d: OK, syn_5m: ULP',
)
