"""
Returns Overlay Table -- TrendSpider store indicator by TrendSpider.

Registered as "returns_overlay_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69effd-returns-overlay-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_NaN = G["NaN"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_open = G["open"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Returns Overlay Table")
    showDTD = J.get(G_input, "boolean")("Show Day-to-Date", True)
    showWTD = J.get(G_input, "boolean")("Show Week-to-Date", True)
    showMTD = J.get(G_input, "boolean")("Show Month-to-Date", True)
    showQTD = J.get(G_input, "boolean")("Show Quarter-to-Date", True)
    showYTD = J.get(G_input, "boolean")("Show Year-to-Date", True)
    show1Y = J.get(G_input, "boolean")("Show 1 Year", True)
    myCurrentClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    myCurrentTime = J.get(G_time, J.sub(J.get(G_time, "length"), 1))
    def calculateReturn(_referenceValue=J.undefined, *_args):
        if (((_referenceValue is None) or (_referenceValue is J.undefined)) or J.truthy(G_isNaN(_referenceValue))):
            return None
        return J.mul(J.div(J.sub(myCurrentClose, _referenceValue), _referenceValue), 100)
    def formatReturn(_returnValue=J.undefined, *_args):
        if ((_returnValue is None) or J.truthy(G_isNaN(_returnValue))):
            return "N/A"
        mySign = ("+" if J.ge(_returnValue, 0) else "")
        return J.template(mySign, J.get(_returnValue, "toFixed")(2), "%")
    def getReturnColor(_returnValue=J.undefined, *_args):
        if ((_returnValue is None) or J.truthy(G_isNaN(_returnValue))):
            return "#999999"
        if J.gt(_returnValue, 0):
            return "#12d962"
        elif J.lt(_returnValue, 0):
            return "#ff4444"
        else:
            return "#cccccc"
    myCurrentBarTime = G_time_of(myCurrentTime)
    myDtdReturn = None
    if J.truthy(showDTD):
        i = 0
        while J.lt(i, J.get(G_close, "length")):
            myBarTime = G_time_of(J.get(G_time, i))
            if ((J.seq(J.get(myBarTime, "dayOfMonth"), J.get(myCurrentBarTime, "dayOfMonth")) and J.seq(J.get(myBarTime, "month"), J.get(myCurrentBarTime, "month"))) and J.seq(J.get(myBarTime, "year"), J.get(myCurrentBarTime, "year"))):
                myDtdReturn = calculateReturn(J.get(G_open, i))
                break
            i = J.inc(i)
    myDailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(myDailyData, "error"))), J.template("Error fetching daily data: \"", J.get(myDailyData, "error"), "\""))
    myWtdReturn = None
    if J.truthy(showWTD):
        moment = G_library("moment-timezone")
        myCurrentMoment = moment(J.mul(myCurrentTime, 1000))
        myDow = J.get(myCurrentMoment, "day")()
        myDaysFromMonday = (6 if J.seq(myDow, 0) else J.sub(myDow, 1))
        myCurrentMonday = J.get(J.get(moment(J.mul(myCurrentTime, 1000)), "subtract")(myDaysFromMonday, "days"), "startOf")("day")
        myCurrentMondayTimestamp = J.div(J.get(myCurrentMonday, "valueOf")(), 1000)
        myWtdAnchor = G_NaN
        i_2 = J.sub(J.get(J.get(myDailyData, "time"), "length"), 1)
        while J.ge(i_2, 0):
            if J.lt(J.get(J.get(myDailyData, "time"), i_2), myCurrentMondayTimestamp):
                myWtdAnchor = J.get(J.get(myDailyData, "close"), i_2)
                break
            i_2 = J.dec(i_2)
        myWtdReturn = calculateReturn(myWtdAnchor)
    myMtdReturn = None
    if J.truthy(showMTD):
        moment_2 = G_library("moment-timezone")
        myFirstOfMonth = J.get(moment_2(J.mul(myCurrentTime, 1000)), "startOf")("month")
        myFirstOfMonthTimestamp = J.div(J.get(myFirstOfMonth, "valueOf")(), 1000)
        myMtdAnchor = G_NaN
        i_3 = J.sub(J.get(J.get(myDailyData, "time"), "length"), 1)
        while J.ge(i_3, 0):
            if J.lt(J.get(J.get(myDailyData, "time"), i_3), myFirstOfMonthTimestamp):
                myMtdAnchor = J.get(J.get(myDailyData, "close"), i_3)
                break
            i_3 = J.dec(i_3)
        myMtdReturn = calculateReturn(myMtdAnchor)
    myQtdReturn = None
    if J.truthy(showQTD):
        i_4 = J.sub(J.get(J.get(myDailyData, "time"), "length"), 1)
        while J.ge(i_4, 0):
            myBarTime_2 = G_time_of(J.get(J.get(myDailyData, "time"), i_4))
            if (J.lt(J.get(myBarTime_2, "quarter"), J.get(myCurrentBarTime, "quarter")) or J.lt(J.get(myBarTime_2, "year"), J.get(myCurrentBarTime, "year"))):
                myQtdReturn = calculateReturn(J.get(J.get(myDailyData, "close"), i_4))
                break
            i_4 = J.dec(i_4)
    myYtdReturn = None
    if J.truthy(showYTD):
        moment_3 = G_library("moment-timezone")
        myFirstOfYear = J.get(moment_3(J.mul(myCurrentTime, 1000)), "startOf")("year")
        myFirstOfYearTimestamp = J.div(J.get(myFirstOfYear, "valueOf")(), 1000)
        myYtdAnchor = G_NaN
        i_5 = J.sub(J.get(J.get(myDailyData, "time"), "length"), 1)
        while J.ge(i_5, 0):
            if J.lt(J.get(J.get(myDailyData, "time"), i_5), myFirstOfYearTimestamp):
                myYtdAnchor = J.get(J.get(myDailyData, "close"), i_5)
                break
            i_5 = J.dec(i_5)
        myYtdReturn = calculateReturn(myYtdAnchor)
    myOneYearReturn = None
    if J.truthy(show1Y):
        myOneYearAgoTime = J.sub(myCurrentTime, J.mul(J.mul(J.mul(365, 24), 60), 60))
        myClosestIndex = None
        myMinDiff = G_Infinity
        i_6 = 0
        while J.lt(i_6, J.get(G_time, "length")):
            myDiff = J.get(G_Math, "abs")(J.sub(J.get(G_time, i_6), myOneYearAgoTime))
            if J.lt(myDiff, myMinDiff):
                myMinDiff = myDiff
                myClosestIndex = i_6
            i_6 = J.inc(i_6)
        if (myClosestIndex is not None):
            myOneYearReturn = calculateReturn(J.get(G_close, myClosestIndex))
    myTableRows = J.JSArray([])
    if J.truthy(showDTD):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("DTD: ", formatReturn(myDtdReturn))), ("color", (getReturnColor(myDtdReturn) if (myDtdReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    if J.truthy(showWTD):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("WTD: ", formatReturn(myWtdReturn))), ("color", (getReturnColor(myWtdReturn) if (myWtdReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    if J.truthy(showMTD):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("MTD: ", formatReturn(myMtdReturn))), ("color", (getReturnColor(myMtdReturn) if (myMtdReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    if J.truthy(showQTD):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("QTD: ", formatReturn(myQtdReturn))), ("color", (getReturnColor(myQtdReturn) if (myQtdReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    if J.truthy(showYTD):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("YTD: ", formatReturn(myYtdReturn))), ("color", (getReturnColor(myYtdReturn) if (myYtdReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    if J.truthy(show1Y):
        J.get(myTableRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("1Y: ", formatReturn(myOneYearReturn))), ("color", (getReturnColor(myOneYearReturn) if (myOneYearReturn is not None) else "#e0e0e0")), ("alignment", "left"), ("padding", "6px 12px"))]))))
    G_paint_overlay("Returns Table", J.obj(("position", "top_right"), ("offset_x", (-70)), ("offset_y", 20)), J.obj(("background_color", "rgba(20, 20, 20, 0.85)"), ("border_color", "#555555"), ("border_width", 1), ("border_radius", 4), ("rows", myTableRows)))


register_store_indicator(
    script,
    name='returns_overlay_table_TS',
    title='Returns Overlay Table',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69effd-returns-overlay-table/',
    position='price',
    inputs=[{'id': 'show_day_to_date', 'title': 'Show Day-to-Date', 'type': 'boolean', 'default': True}, {'id': 'show_week_to_date', 'title': 'Show Week-to-Date', 'type': 'boolean', 'default': True}, {'id': 'show_month_to_date', 'title': 'Show Month-to-Date', 'type': 'boolean', 'default': True}, {'id': 'show_quarter_to_date', 'title': 'Show Quarter-to-Date', 'type': 'boolean', 'default': True}, {'id': 'show_year_to_date', 'title': 'Show Year-to-Date', 'type': 'boolean', 'default': True}, {'id': 'show_1_year', 'title': 'Show 1 Year', 'type': 'boolean', 'default': True}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
