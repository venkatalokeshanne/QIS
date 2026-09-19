"""
Weekly Fibonacci Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "weekly_fibonacci_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/weekly-fibonacci-levels/)
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
    G_console = G["console"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Weekly Fibonacci Levels", "price", J.obj(("shortName", "WeeklyFibEdges"), ("decimals", 2)))
    showEdges = J.get(G_input, "boolean")("Show Edges", True)
    showLabels = J.get(G_input, "boolean")("Show Labels", True)
    moment = G_library("moment-timezone")
    def getWeeklyData(*_args):
        weeklyData_2 = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
        G_assert((not J.truthy(J.get(weeklyData_2, "error"))), J.template("Error fetching weekly data: ", J.get(weeklyData_2, "error")))
        return weeklyData_2
    weeklyData = getWeeklyData()
    def calculateFibLevels(high=J.undefined, low=J.undefined, *_args):
        range = J.sub(high, low)
        return J.obj(("level161", J.add(high, J.mul(range, 0.618))), ("level138", J.add(high, J.mul(range, 0.382))), ("level100", high), ("level786", J.add(low, J.mul(range, 0.786))), ("level618", J.add(low, J.mul(range, 0.618))), ("level50", J.add(low, J.mul(range, 0.5))), ("level236", J.add(low, J.mul(range, 0.236))), ("level0", low))
    def getLastCompletedWeekHighLow(currentTime=J.undefined, *_args):
        currentWeekStart_2 = J.get(J.get(moment(J.mul(currentTime, 1000)), "startOf")("week"), "unix")()
        lastCompletedWeekIndex = J.sub(J.get(J.get(weeklyData, "time"), "length"), 1)
        while (J.ge(lastCompletedWeekIndex, 0) and J.ge(J.get(J.get(weeklyData, "time"), lastCompletedWeekIndex), currentWeekStart_2)):
            lastCompletedWeekIndex = J.dec(lastCompletedWeekIndex)
        return J.obj(("high", J.get(J.get(weeklyData, "high"), lastCompletedWeekIndex)), ("low", J.get(J.get(weeklyData, "low"), lastCompletedWeekIndex)))
    myLevel161 = G_series_of(None)
    myLevel138 = G_series_of(None)
    myLevel100 = G_series_of(None)
    myLevel786 = G_series_of(None)
    myLevel618 = G_series_of(None)
    myLevel50 = G_series_of(None)
    myLevel236 = G_series_of(None)
    myLevel0 = G_series_of(None)
    currentWeekStart = 0
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        candleWeekStart = J.get(J.get(moment(J.mul(J.get(G_time, i), 1000)), "startOf")("week"), "unix")()
        if J.sne(candleWeekStart, currentWeekStart):
            currentWeekStart = candleWeekStart
            _t1 = J.require_object(getLastCompletedWeekHighLow(J.get(G_time, i)))
            lastWeekHigh = J.get(_t1, "high")
            lastWeekLow = J.get(_t1, "low")
            currentWeekFibLevels = calculateFibLevels(lastWeekHigh, lastWeekLow)
            J.set(myLevel161, i, J.get(currentWeekFibLevels, "level161"))
            J.set(myLevel138, i, J.get(currentWeekFibLevels, "level138"))
            J.set(myLevel100, i, J.get(currentWeekFibLevels, "level100"))
            J.set(myLevel786, i, J.get(currentWeekFibLevels, "level786"))
            J.set(myLevel618, i, J.get(currentWeekFibLevels, "level618"))
            J.set(myLevel50, i, J.get(currentWeekFibLevels, "level50"))
            J.set(myLevel236, i, J.get(currentWeekFibLevels, "level236"))
            J.set(myLevel0, i, J.get(currentWeekFibLevels, "level0"))
            J.get(G_console, "log")(J.template("Weekly High: ", lastWeekHigh, ", Low: ", lastWeekLow, ", Fib 161.8%: ", J.get(currentWeekFibLevels, "level161"), ", Fib 138.2%: ", J.get(currentWeekFibLevels, "level138"), ", Fib 100%: ", J.get(currentWeekFibLevels, "level100"), ", Fib 78.6%: ", J.get(currentWeekFibLevels, "level786"), ", Fib 61.8%: ", J.get(currentWeekFibLevels, "level618"), ", Fib 50%: ", J.get(currentWeekFibLevels, "level50"), ", Fib 23.6%: ", J.get(currentWeekFibLevels, "level236"), ", Fib 0%: ", J.get(currentWeekFibLevels, "level0")))
        else:
            J.set(myLevel161, i, J.get(myLevel161, J.sub(i, 1)))
            J.set(myLevel138, i, J.get(myLevel138, J.sub(i, 1)))
            J.set(myLevel100, i, J.get(myLevel100, J.sub(i, 1)))
            J.set(myLevel786, i, J.get(myLevel786, J.sub(i, 1)))
            J.set(myLevel618, i, J.get(myLevel618, J.sub(i, 1)))
            J.set(myLevel50, i, J.get(myLevel50, J.sub(i, 1)))
            J.set(myLevel236, i, J.get(myLevel236, J.sub(i, 1)))
            J.set(myLevel0, i, J.get(myLevel0, J.sub(i, 1)))
        if J.lt(i, J.sub(J.get(G_time, "length"), 1)):
            nextCandleWeekStart = J.get(J.get(moment(J.mul(J.get(G_time, J.add(i, 1)), 1000)), "startOf")("week"), "unix")()
            if J.sne(nextCandleWeekStart, currentWeekStart):
                J.set(myLevel161, i, None)
                J.set(myLevel138, i, None)
                J.set(myLevel100, i, None)
                J.set(myLevel786, i, None)
                J.set(myLevel618, i, None)
                J.set(myLevel50, i, None)
                J.set(myLevel236, i, None)
                J.set(myLevel0, i, None)
        i = J.inc(i)
    if J.truthy(showEdges):
        level161 = G_paint(myLevel161, J.obj(("name", "161.8% Extension"), ("color", "purple"), ("style", "line")))
        level138 = G_paint(myLevel138, J.obj(("name", "138.2% Extension"), ("color", "blue"), ("style", "line")))
        level100 = G_paint(myLevel100, J.obj(("name", "100% Retracement"), ("color", "white"), ("style", "line")))
        level786 = G_paint(myLevel786, J.obj(("name", "78.6% Retracement"), ("color", "green"), ("style", "line")))
        level618 = G_paint(myLevel618, J.obj(("name", "61.8% Retracement"), ("color", "orange"), ("style", "line")))
        level50 = G_paint(myLevel50, J.obj(("name", "50% Retracement"), ("color", "yellow"), ("style", "line")))
        level236 = G_paint(myLevel236, J.obj(("name", "23.6% Retracement"), ("color", "red"), ("style", "line")))
        level0 = G_paint(myLevel0, J.obj(("name", "0% Retracement"), ("color", "white"), ("style", "line")))
        if J.truthy(showLabels):
            G_paint_label_at_line(level161, J.sub(J.get(G_close, "length"), 1), "161.8%", J.obj(("color", "purple"), ("vertical_align", "top")))
            G_paint_label_at_line(level138, J.sub(J.get(G_close, "length"), 1), "138.2%", J.obj(("color", "blue"), ("vertical_align", "top")))
            G_paint_label_at_line(level100, J.sub(J.get(G_close, "length"), 1), "100%", J.obj(("color", "white"), ("vertical_align", "top")))
            G_paint_label_at_line(level786, J.sub(J.get(G_close, "length"), 1), "78.6%", J.obj(("color", "green"), ("vertical_align", "top")))
            G_paint_label_at_line(level618, J.sub(J.get(G_close, "length"), 1), "61.8%", J.obj(("color", "orange"), ("vertical_align", "top")))
            G_paint_label_at_line(level50, J.sub(J.get(G_close, "length"), 1), "50%", J.obj(("color", "yellow"), ("vertical_align", "top")))
            G_paint_label_at_line(level236, J.sub(J.get(G_close, "length"), 1), "23.6%", J.obj(("color", "red"), ("vertical_align", "top")))
            G_paint_label_at_line(level0, J.sub(J.get(G_close, "length"), 1), "0%", J.obj(("color", "white"), ("vertical_align", "top")))
    def _f2(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel161, _f2), "Price above 161.8% level")
    def _f3(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel138, _f3), "Price above 138.2% level")
    def _f4(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel100, _f4), "Price above 100% level")
    def _f5(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel786, _f5), "Price above 78.6% level")
    def _f6(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel618, _f6), "Price above 61.8% level")
    def _f7(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel50, _f7), "Price above 50% level")
    def _f8(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel236, _f8), "Price above 23.6% level")
    def _f9(c=J.undefined, l=J.undefined, *_args):
        return J.gt(c, l)
    G_register_signal(G_for_every(G_close, myLevel0, _f9), "Price above 0% level")


register_store_indicator(
    script,
    name='weekly_fibonacci_levels_TS',
    title='Weekly Fibonacci Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/weekly-fibonacci-levels/',
    position='price',
    inputs=[{'id': 'show_edges', 'title': 'Show Edges', 'type': 'boolean', 'default': True}, {'id': 'show_labels', 'title': 'Show Labels', 'type': 'boolean', 'default': True}],
    outputs=['161_8__extension', '138_2__extension', '100__retracement', '78_6__retracement', '61_8__retracement', '50__retracement', '23_6__retracement', '0__retracement', 'price_above_161_8__level', 'price_above_138_2__level', 'price_above_100__level', 'price_above_78_6__level', 'price_above_61_8__level', 'price_above_50__level', 'price_above_23_6__level', 'price_above_0__level'],
    signals=['price_above_161_8__level', 'price_above_138_2__level', 'price_above_100__level', 'price_above_78_6__level', 'price_above_61_8__level', 'price_above_50__level', 'price_above_23_6__level', 'price_above_0__level'],
    requires=['history'],
    parity='exact',
)
