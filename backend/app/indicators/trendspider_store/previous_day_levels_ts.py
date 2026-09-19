"""
Previous Day Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "previous_day_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/previous-day-levels/)
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
    G_input = G["input"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Previous Day Levels")
    lookbackPeriod = J.get(G_input, "number")("Lookback Period", 1, J.obj(("min", 1), ("max", 10)))
    highLineColor = J.get(G_input, "color")("High Line Color", "#39FF14")
    lowLineColor = J.get(G_input, "color")("Low Line Color", "#FF3131")
    midLineColor = J.get(G_input, "color")("50% Line Color", "white")
    highLineStyle = J.get(G_input, "select")("High Line Style", "line", J.JSArray(["line", "dotted"]))
    lowLineStyle = J.get(G_input, "select")("Low Line Style", "line", J.JSArray(["line", "dotted"]))
    midLineStyle = J.get(G_input, "select")("50% Line Style", "line", J.JSArray(["line", "dotted"]))
    lineThickness = J.get(G_input, "number")("Line Thickness", 2, J.obj(("min", 1), ("max", 5)))
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
    highLevels = G_series_of(None)
    lowLevels = G_series_of(None)
    midLevels = G_series_of(None)
    i = 0
    while J.lt(i, lookbackPeriod):
        dailyIndex = J.sub(J.sub(J.get(J.get(dailyData, "close"), "length"), 2), i)
        if J.ge(dailyIndex, 0):
            prevDayHigh = J.get(J.get(dailyData, "high"), dailyIndex)
            prevDayLow = J.get(J.get(dailyData, "low"), dailyIndex)
            prevDayMid = J.div(J.add(prevDayHigh, prevDayLow), 2)
            def _f1(t=J.undefined, *_args):
                return J.ge(t, J.get(J.get(dailyData, "time"), J.add(dailyIndex, 1)))
            startIndex = J.get(G_time, "findIndex")(_f1)
            if J.sne(startIndex, (-1)):
                j = startIndex
                while J.lt(j, J.get(G_time, "length")):
                    J.set(highLevels, j, prevDayHigh)
                    J.set(lowLevels, j, prevDayLow)
                    J.set(midLevels, j, prevDayMid)
                    j = J.inc(j)
        i = J.inc(i)
    G_paint(highLevels, J.obj(("color", highLineColor), ("style", highLineStyle), ("name", "Previous Day High"), ("linewidth", lineThickness)))
    G_paint(lowLevels, J.obj(("color", lowLineColor), ("style", lowLineStyle), ("name", "Previous Day Low"), ("linewidth", lineThickness)))
    G_paint(midLevels, J.obj(("color", midLineColor), ("style", midLineStyle), ("name", "Previous Day 50%"), ("linewidth", lineThickness)))


register_store_indicator(
    script,
    name='previous_day_levels_TS',
    title='Previous Day Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/previous-day-levels/',
    position='price',
    inputs=[{'id': 'lookback_period', 'title': 'Lookback Period', 'type': 'number', 'default': 1}, {'id': 'high_line_color', 'title': 'High Line Color', 'type': 'color', 'default': '#39FF14'}, {'id': 'low_line_color', 'title': 'Low Line Color', 'type': 'color', 'default': '#FF3131'}, {'id': '50__line_color', 'title': '50% Line Color', 'type': 'color', 'default': 'white'}, {'id': 'high_line_style', 'title': 'High Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': 'low_line_style', 'title': 'Low Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': '50__line_style', 'title': '50% Line Style', 'type': 'select_wide', 'default': 'line', 'options': ['line', 'dotted']}, {'id': 'line_thickness', 'title': 'Line Thickness', 'type': 'number', 'default': 2}],
    outputs=['previous_day_high', 'previous_day_low', 'previous_day_50_'],
    signals=[],
    requires=['history'],
    parity='exact',
)
