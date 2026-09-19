"""
RSI with Seasonality -- TrendSpider store indicator by TrendSpider Team.

Registered as "rsi_with_seasonality_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/rsi-with-seasonality/)
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
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_rsi = G["rsi"]
    G_time = G["time"]
    G_describe_indicator("RSI with Seasonality", "lower")
    moment = G_library("moment-timezone")
    length = J.get(G_input, "number")("RSI Length", 14, J.obj(("min", 1)))
    overboughtLevel = J.get(G_input, "number")("Overbought", 70, J.obj(("min", 50), ("max", 100)))
    oversoldLevel = J.get(G_input, "number")("Oversold", 30, J.obj(("min", 0), ("max", 50)))
    seasonalityData = J.get(G_request, "seasonality")(J.get(G_current, "ticker"), "week_of_year", "change")
    G_assert((not J.truthy(J.get(seasonalityData, "error"))), J.template("Error fetching seasonality data: ", J.get(seasonalityData, "error")))
    myRsi = G_rsi(G_close, length)
    def getSeasonalityForWeek(weekNumber=J.undefined, *_args):
        weekData = J.get(J.get(seasonalityData, "dataByCategory"), weekNumber)
        if (not J.truthy(weekData)):
            return J.obj(("winRate", 0), ("meanChange", 0))
        def _f1(record=J.undefined, *_args):
            return J.gt(J.get(record, "value"), 0)
        winRate_2 = J.div(J.mul(100, J.get(J.get(weekData, "filter")(_f1), "length")), J.get(weekData, "length"))
        def _f2(sum=J.undefined, record=J.undefined, *_args):
            return J.add(sum, J.get(record, "value"))
        meanChange_2 = J.div(J.get(weekData, "reduce")(_f2, 0), J.get(weekData, "length"))
        return J.obj(("winRate", winRate_2), ("meanChange", meanChange_2))
    def getColorForWinRate(winRate_2=J.undefined, *_args):
        if J.gt(winRate_2, 65):
            return "#00FF00"
        if J.gt(winRate_2, 50):
            return "#008000"
        if J.gt(winRate_2, 35):
            return "#FF0000"
        return "#8B0000"
    def _f1(t=J.undefined, i=J.undefined, *_args):
        weekNumber = J.get(moment(J.mul(t, 1000)), "isoWeek")()
        _t1 = J.require_object(getSeasonalityForWeek(weekNumber))
        winRate_2 = J.get(_t1, "winRate")
        return getColorForWinRate(winRate_2)
    rsiColor = G_for_every(G_time, _f1)
    G_paint(myRsi, J.obj(("style", "line"), ("color", rsiColor), ("name", "RSI")))
    G_paint(G_horizontal_line(overboughtLevel), J.obj(("color", "gray"), ("style", "dotted")))
    G_paint(G_horizontal_line(oversoldLevel), J.obj(("color", "gray"), ("style", "dotted")))
    currentWeek = J.get(moment(), "isoWeek")()
    _t2 = J.require_object(getSeasonalityForWeek(currentWeek))
    winRate = J.get(_t2, "winRate")
    meanChange = J.get(_t2, "meanChange")
    G_paint_overlay("WeekInfo", J.obj(("position", "top_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Week ", currentWeek, " Win Rate: ", J.get(winRate, "toFixed")(2), "%")), ("color", getColorForWinRate(winRate)))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Avg Weekly Change: ", J.get(J.mul(meanChange, 100), "toFixed")(2), "%")), ("color", ("green" if J.gt(meanChange, 0) else "red")))])))]))))


register_store_indicator(
    script,
    name='rsi_with_seasonality_TS',
    title='RSI with Seasonality',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/rsi-with-seasonality/',
    position='lower',
    inputs=[{'id': 'rsi_length', 'title': 'RSI Length', 'type': 'number', 'default': 14}, {'id': 'overbought', 'title': 'Overbought', 'type': 'number', 'default': 70}, {'id': 'oversold', 'title': 'Oversold', 'type': 'number', 'default': 30}],
    outputs=['rsi', 'line_3', 'line_4'],
    signals=[],
    requires=['seasonality'],
    parity='exact',
)
