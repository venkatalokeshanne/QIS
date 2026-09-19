"""
Relative Performance Candle Coloring -- TrendSpider store indicator by TrendSpider Team.

Registered as "relative_performance_candle_coloring_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/relative-performance-candle-coloring/)
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
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Relative Performance Candle Coloring")
    performanceType = J.get(G_input, "select")("Performance Type", "yearly", J.JSArray(["yearly", "quarterly", "techrank"]))
    strongThreshold = J.get(G_input, "number")("Strong Performance Threshold", 85, J.obj(("min", 0), ("max", 100)))
    goodThreshold = J.get(G_input, "number")("Good Performance Threshold", 70, J.obj(("min", 0), ("max", 100)))
    weakThreshold = J.get(G_input, "number")("Weak Performance Threshold", 30, J.obj(("min", 0), ("max", 100)))
    strongColor = J.get(G_input, "color")("Strong Performance Color", "green")
    goodColor = J.get(G_input, "color")("Good Performance Color", "orange")
    weakColor = J.get(G_input, "color")("Weak Performance Color", "red")
    neutralColor = J.get(G_input, "color")("Neutral Performance Color", "gray")
    relativePerformanceData = J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), performanceType, "spx500")
    G_assert((not J.truthy(J.get(relativePerformanceData, "error"))), J.add("Error fetching relative performance data: ", J.get(relativePerformanceData, "error")))
    def _f1(_dataPoint=J.undefined, *_args):
        return J.get(_dataPoint, 1)
    myRelativePerformance = J.get(relativePerformanceData, "map")(_f1)
    def _f2(_dataPoint=J.undefined, *_args):
        return J.get(_dataPoint, 0)
    myInterpolatedRelativePerformance = G_interpolate_sparse_series(G_land_points_onto_series(J.get(relativePerformanceData, "map")(_f2), myRelativePerformance, G_time, "le"), "constant")
    def _f3(_rp=J.undefined, *_args):
        if J.gt(_rp, strongThreshold):
            return strongColor
        if J.gt(_rp, goodThreshold):
            return goodColor
        if J.lt(_rp, weakThreshold):
            return weakColor
        return neutralColor
    myColors = G_for_every(myInterpolatedRelativePerformance, _f3)
    G_color_candles(myColors)
    if J.seq(performanceType, "techrank"):
        def _f4(_rp=J.undefined, *_args):
            return J.gt(_rp, strongThreshold)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f4), "Strong Technical Performance")
        def _f5(_rp=J.undefined, *_args):
            return (J.le(_rp, strongThreshold) if J.truthy(_t1 := J.gt(_rp, goodThreshold)) else _t1)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f5), "Good Technical Performance")
        def _f6(_rp=J.undefined, *_args):
            return J.lt(_rp, weakThreshold)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f6), "Weak Technical Performance")
    else:
        def _f7(_rp=J.undefined, *_args):
            return J.gt(_rp, strongThreshold)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f7), "Strong Outperformer")
        def _f8(_rp=J.undefined, *_args):
            return (J.le(_rp, strongThreshold) if J.truthy(_t1 := J.gt(_rp, goodThreshold)) else _t1)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f8), "Outperformer")
        def _f9(_rp=J.undefined, *_args):
            return J.lt(_rp, weakThreshold)
        G_register_signal(G_for_every(myInterpolatedRelativePerformance, _f9), "Underperformer")


register_store_indicator(
    script,
    name='relative_performance_candle_coloring_TS',
    title='Relative Performance Candle Coloring',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/relative-performance-candle-coloring/',
    position='price',
    inputs=[{'id': 'performance_type', 'title': 'Performance Type', 'type': 'select_wide', 'default': 'yearly', 'options': ['yearly', 'quarterly', 'techrank']}, {'id': 'strong_performance_threshold', 'title': 'Strong Performance Threshold', 'type': 'number', 'default': 85}, {'id': 'good_performance_threshold', 'title': 'Good Performance Threshold', 'type': 'number', 'default': 70}, {'id': 'weak_performance_threshold', 'title': 'Weak Performance Threshold', 'type': 'number', 'default': 30}, {'id': 'strong_performance_color', 'title': 'Strong Performance Color', 'type': 'color', 'default': 'green'}, {'id': 'good_performance_color', 'title': 'Good Performance Color', 'type': 'color', 'default': 'orange'}, {'id': 'weak_performance_color', 'title': 'Weak Performance Color', 'type': 'color', 'default': 'red'}, {'id': 'neutral_performance_color', 'title': 'Neutral Performance Color', 'type': 'color', 'default': 'gray'}],
    outputs=['cdl', 'strong_outperformer', 'outperformer', 'underperformer'],
    signals=['strong_outperformer', 'outperformer', 'underperformer'],
    requires=['relative_performance'],
    parity='exact',
)
