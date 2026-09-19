"""
MavilimW MTF -- TrendSpider store indicator by Chirag Patnaik.

Registered as "mavilimw_mtf_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a1d4-mavilimw-mtf/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_time = G["time"]
    G_wma = G["wma"]
    G_describe_indicator("MavilimW MTF", "price")
    timeFrame = J.get(G_input, "select")("Time Frame", "1 Day", J.JSArray(["1 minute", "5 minute", "15 minute", "1 hour", "4 hour", "1 Day", "1 Week", "1 Month"]))
    showPreviousVersion = J.get(G_input, "boolean")("Show Previous Version?", False)
    firstMALength = J.get(G_input, "number")("First Moving Average length", 3)
    secondMALength = J.get(G_input, "number")("Second Moving Average length", 5)
    length3 = J.add(firstMALength, secondMALength)
    length4 = J.add(secondMALength, length3)
    length5 = J.add(length3, length4)
    length6 = J.add(length4, length5)
    def nestedWMA(source=J.undefined, lengths=J.undefined, *_args):
        result = source
        for length in J.iter_of(lengths):
            result = G_wma(result, length)
        return result
    m6 = nestedWMA(G_close, J.JSArray([firstMALength, secondMALength, length3, length4, length5, length6]))
    m6Old = None
    if J.truthy(showPreviousVersion):
        m6Old = nestedWMA(G_close, J.JSArray([3, 5, 8, 13, 21, 34]))
    timeFrameToResolution = J.obj(("1 minute", "1"), ("5 minute", "5"), ("15 minute", "15"), ("1 hour", "60"), ("4 hour", "240"), ("1 Day", "D"), ("1 Week", "W"), ("1 Month", "M"))
    resolution = J.get(timeFrameToResolution, timeFrame)
    G_assert(resolution, J.template("Invalid time frame: ", timeFrame))
    higherTimeFrameData = J.get(G_request, "history")(J.get(G_current, "ticker"), resolution)
    G_assert((not J.truthy(J.get(higherTimeFrameData, "error"))), J.template("Error fetching data: ", J.get(higherTimeFrameData, "error")))
    mavw = G_land_points_onto_series(J.get(higherTimeFrameData, "time"), m6, G_time, "ge")
    mavwInterpolated = G_interpolate_sparse_series(mavw, "constant")
    G_paint(mavwInterpolated, J.obj(("color", "blue"), ("linewidth", 2), ("name", "MAVW")))
    if J.truthy(showPreviousVersion):
        mavwOld = G_land_points_onto_series(J.get(higherTimeFrameData, "time"), m6Old, G_time, "ge")
        mavwOldInterpolated = G_interpolate_sparse_series(mavwOld, "constant")
        G_paint(mavwOldInterpolated, J.obj(("color", "blue"), ("linewidth", 2), ("name", "MAVW Old")))


register_store_indicator(
    script,
    name='mavilimw_mtf_TS',
    title='MavilimW MTF',
    developer='Chirag Patnaik',
    url='https://trendspider.com/trading-tools-store/indicators/68a1d4-mavilimw-mtf/',
    position='price',
    inputs=[{'id': 'time_frame', 'title': 'Time Frame', 'type': 'select_wide', 'default': '1 Day', 'options': ['1 minute', '5 minute', '15 minute', '1 hour', '4 hour', '1 Day', '1 Week', '1 Month']}, {'id': 'show_previous_version_', 'title': 'Show Previous Version?', 'type': 'boolean', 'default': False}, {'id': 'first_moving_average_length', 'title': 'First Moving Average length', 'type': 'number', 'default': 3}, {'id': 'second_moving_average_length', 'title': 'Second Moving Average length', 'type': 'number', 'default': 5}],
    outputs=['mavw'],
    signals=[],
    requires=['history'],
    parity='exact',
)
