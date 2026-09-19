"""
Relative Performance with MA -- TrendSpider store indicator by TrendSpider Team.

Registered as "relative_performance_with_ma_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/relative-performance-with-ma/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_indicators = G["indicators"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Relative Performance with MA", "lower")
    performanceType = J.get(G_input, "select")("Performance Type", "yearly", J.JSArray(["yearly", "quarterly", "techrank"]))
    universe = J.get(G_input, "select")("Universe", "spx500", J.JSArray(["spx500", "russell2000", "same_sector", "same_mktcap", "same_sector_mktcap"]))
    maType = J.get(G_input, "select")("MA Type", "sma", J.get(G_constants, "ma_types"))
    maPeriod = J.get(G_input, "number")("MA Period", 20, J.obj(("min", 1)))
    maColor = J.get(G_input, "color")("MA Color", "red")
    myPerfData = J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), performanceType, universe)
    G_assert((not J.truthy(J.get(myPerfData, "error"))), J.add("Error fetching relative performance data: ", J.get(myPerfData, "error")))
    def _f1(d=J.undefined, *_args):
        return J.get(d, 0)
    myTimestamps = J.get(myPerfData, "map")(_f1)
    def _f2(d=J.undefined, *_args):
        return J.get(d, 1)
    myValues = J.get(myPerfData, "map")(_f2)
    myRelativePerformance = G_interpolate_sparse_series(G_land_points_onto_series(myTimestamps, myValues, G_time, "le"), "constant")
    myMaFunction = J.get(G_indicators, maType)
    G_assert(J.seq(J.typeof(myMaFunction), "function"), J.template("Invalid MA type: ", maType))
    myMovingAverage = myMaFunction(myRelativePerformance, maPeriod)
    myPerfLine = G_paint(myRelativePerformance, J.obj(("color", "white"), ("name", "Relative Performance")))
    G_paint(myMovingAverage, J.obj(("color", maColor), ("name", J.template(J.get(maType, "toUpperCase")(), "(", maPeriod, ")"))))
    G_paint(G_horizontal_line(80), J.obj(("color", "grey"), ("name", "80 Level")))
    G_paint(G_horizontal_line(50), J.obj(("color", "grey"), ("style", "dotted"), ("name", "50 Level")))
    G_paint(G_horizontal_line(15), J.obj(("color", "grey"), ("name", "15 Level")))
    def _f3(rp=J.undefined, *_args):
        return (80 if J.gt(rp, 80) else None)
    myAbove80 = G_for_every(myRelativePerformance, _f3)
    def _f4(rp=J.undefined, *_args):
        return (15 if J.lt(rp, 15) else None)
    myBelow15 = G_for_every(myRelativePerformance, _f4)
    G_fill(myPerfLine, G_paint(myAbove80, J.obj(("hidden", True))), "green", 0.3, "Above 80")
    G_fill(G_paint(myBelow15, J.obj(("hidden", True))), myPerfLine, "red", 0.3, "Below 15")


register_store_indicator(
    script,
    name='relative_performance_with_ma_TS',
    title='Relative Performance with MA',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/relative-performance-with-ma/',
    position='lower',
    inputs=[{'id': 'performance_type', 'title': 'Performance Type', 'type': 'select_wide', 'default': 'yearly', 'options': ['yearly', 'quarterly', 'techrank']}, {'id': 'universe', 'title': 'Universe', 'type': 'select_wide', 'default': 'spx500', 'options': ['spx500', 'russell2000', 'same_sector', 'same_mktcap', 'same_sector_mktcap']}, {'id': 'ma_type', 'title': 'MA Type', 'type': 'select_wide', 'default': 'sma', 'options': ['ema', 'sma', 'wildma', 'vwma', 'wma', 'hullma', 'kama', 'alma', 'twap']}, {'id': 'ma_period', 'title': 'MA Period', 'type': 'number', 'default': 20}, {'id': 'ma_color', 'title': 'MA Color', 'type': 'color', 'default': 'red'}],
    outputs=['relative_performance', 'sma_20_', '80_level', '50_level', '15_level', 'line_6', 'line_8'],
    signals=[],
    requires=['relative_performance'],
    parity='exact',
)
