"""
MTF Support & Resistance -- TrendSpider store indicator by Mohamed Algendy.

Registered as "mtf_support_resistance_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69f3a5-mtf-support-resistance/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    def detectPivots(_high=J.undefined, _low=J.undefined, _lookback=J.undefined, *_args):
        mySwingHighs = J.JSArray([])
        mySwingLows = J.JSArray([])
        myStartIndex = _lookback
        myEndIndex = J.sub(J.get(_high, "length"), _lookback)
        i = myStartIndex
        while J.lt(i, myEndIndex):
            isSwingHigh = True
            j = J.sub(i, _lookback)
            while J.le(j, J.add(i, _lookback)):
                if (J.sne(j, i) and J.ge(J.get(_high, j), J.get(_high, i))):
                    isSwingHigh = False
                    break
                j = J.inc(j)
            if J.truthy(isSwingHigh):
                J.get(mySwingHighs, "push")(J.obj(("index", i), ("price", J.get(_high, i))))
            isSwingLow = True
            j_2 = J.sub(i, _lookback)
            while J.le(j_2, J.add(i, _lookback)):
                if (J.sne(j_2, i) and J.le(J.get(_low, j_2), J.get(_low, i))):
                    isSwingLow = False
                    break
                j_2 = J.inc(j_2)
            if J.truthy(isSwingLow):
                J.get(mySwingLows, "push")(J.obj(("index", i), ("price", J.get(_low, i))))
            i = J.inc(i)
        return J.obj(("highs", mySwingHighs), ("lows", mySwingLows))
    def createLevelSeries(_pivotArray=J.undefined, _sourceTime=J.undefined, *_args):
        mySeries = G_series_of(None)
        for myPivot in J.iter_of(_pivotArray):
            myPivotTime = J.get(_sourceTime, J.get(myPivot, "index"))
            i = 0
            while J.lt(i, J.get(G_time, "length")):
                if J.ge(J.get(G_time, i), myPivotTime):
                    j = i
                    while J.lt(j, J.get(G_time, "length")):
                        J.set(mySeries, j, J.get(myPivot, "price"))
                        j = J.inc(j)
                    break
                i = J.inc(i)
        return mySeries
    def generateLabelText(_price=J.undefined, _tfTag=J.undefined, *_args):
        myFormattedPrice = J.get(_price, "toFixed")(2)
        if J.truthy(showTFTag):
            return J.add(J.add(_tfTag, " "), myFormattedPrice)
        return myFormattedPrice
    G_describe_indicator("MTF Support & Resistance")
    monthlyColor = "#FF4444"
    weeklyColor = "#4488FF"
    dailyColor = "#44FF88"
    monthlyThickness = 3
    weeklyThickness = 2
    dailyThickness = 1
    monthlyStyle = "line"
    weeklyStyle = "line"
    dailyStyle = "line"
    MAX_LEVELS = 5
    numLevels = J.get(G_input, "number")("Number of Levels", 1, J.obj(("min", 1), ("max", MAX_LEVELS)))
    pivotLookback = J.get(G_input, "number")("Pivot Lookback", 5, J.obj(("min", 2), ("max", 20)))
    showMonthly = J.get(G_input, "boolean")("Show Monthly", True)
    showWeekly = J.get(G_input, "boolean")("Show Weekly", True)
    showDaily = J.get(G_input, "boolean")("Show Daily", True)
    showLabels = J.get(G_input, "boolean")("Show Labels", True)
    showTFTag = J.get(G_input, "boolean")("Show TF Tag", True)
    myNumLevels = J.get(G_Math, "max")(1, J.get(G_Math, "min")(MAX_LEVELS, numLevels))
    myPivotLookback = J.get(G_Math, "max")(2, J.get(G_Math, "min")(20, pivotLookback))
    monthlyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "M")
    G_assert((not J.truthy(J.get(monthlyData, "error"))), J.add("Error fetching monthly data: ", J.get(monthlyData, "error")))
    weeklyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "W")
    G_assert((not J.truthy(J.get(weeklyData, "error"))), J.add("Error fetching weekly data: ", J.get(weeklyData, "error")))
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.add("Error fetching daily data: ", J.get(dailyData, "error")))
    monthlyPivots = detectPivots(J.get(monthlyData, "high"), J.get(monthlyData, "low"), myPivotLookback)
    weeklyPivots = detectPivots(J.get(weeklyData, "high"), J.get(weeklyData, "low"), myPivotLookback)
    dailyPivots = detectPivots(J.get(dailyData, "high"), J.get(dailyData, "low"), myPivotLookback)
    myMonthlyHighLevels = J.get(J.get(monthlyPivots, "highs"), "slice")(J.neg(myNumLevels))
    myMonthlyLowLevels = J.get(J.get(monthlyPivots, "lows"), "slice")(J.neg(myNumLevels))
    myWeeklyHighLevels = J.get(J.get(weeklyPivots, "highs"), "slice")(J.neg(myNumLevels))
    myWeeklyLowLevels = J.get(J.get(weeklyPivots, "lows"), "slice")(J.neg(myNumLevels))
    myDailyHighLevels = J.get(J.get(dailyPivots, "highs"), "slice")(J.neg(myNumLevels))
    myDailyLowLevels = J.get(J.get(dailyPivots, "lows"), "slice")(J.neg(myNumLevels))
    i = 0
    while J.lt(i, MAX_LEVELS):
        myActive = (J.lt(i, myNumLevels) if J.truthy(_t1 := showMonthly) else _t1)
        myHighPivot = (J.JSArray([J.get(myMonthlyHighLevels, i)]) if (J.truthy(myActive) and J.truthy(J.get(myMonthlyHighLevels, i))) else J.JSArray([]))
        myLowPivot = (J.JSArray([J.get(myMonthlyLowLevels, i)]) if (J.truthy(myActive) and J.truthy(J.get(myMonthlyLowLevels, i))) else J.JSArray([]))
        myHighSeries = (createLevelSeries(myHighPivot, J.get(monthlyData, "time")) if J.gt(J.get(myHighPivot, "length"), 0) else G_series_of(None))
        myLowSeries = (createLevelSeries(myLowPivot, J.get(monthlyData, "time")) if J.gt(J.get(myLowPivot, "length"), 0) else G_series_of(None))
        myHighLineId = G_paint(myHighSeries, J.obj(("name", J.add("Monthly R", J.add(i, 1))), ("color", monthlyColor), ("thickness", monthlyThickness), ("style", monthlyStyle)))
        myLowLineId = G_paint(myLowSeries, J.obj(("name", J.add("Monthly S", J.add(i, 1))), ("color", monthlyColor), ("thickness", monthlyThickness), ("style", monthlyStyle)))
        if (J.truthy(showLabels) and J.gt(J.get(myHighPivot, "length"), 0)):
            G_paint_label_at_line(myHighLineId, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myHighPivot, 0), "price"), "M"), J.obj(("color", monthlyColor), ("vertical_align", "middle")))
        if (J.truthy(showLabels) and J.gt(J.get(myLowPivot, "length"), 0)):
            G_paint_label_at_line(myLowLineId, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myLowPivot, 0), "price"), "M"), J.obj(("color", monthlyColor), ("vertical_align", "middle")))
        i = J.inc(i)
    i_2 = 0
    while J.lt(i_2, MAX_LEVELS):
        myActive_2 = (J.lt(i_2, myNumLevels) if J.truthy(_t2 := showWeekly) else _t2)
        myHighPivot_2 = (J.JSArray([J.get(myWeeklyHighLevels, i_2)]) if (J.truthy(myActive_2) and J.truthy(J.get(myWeeklyHighLevels, i_2))) else J.JSArray([]))
        myLowPivot_2 = (J.JSArray([J.get(myWeeklyLowLevels, i_2)]) if (J.truthy(myActive_2) and J.truthy(J.get(myWeeklyLowLevels, i_2))) else J.JSArray([]))
        myHighSeries_2 = (createLevelSeries(myHighPivot_2, J.get(weeklyData, "time")) if J.gt(J.get(myHighPivot_2, "length"), 0) else G_series_of(None))
        myLowSeries_2 = (createLevelSeries(myLowPivot_2, J.get(weeklyData, "time")) if J.gt(J.get(myLowPivot_2, "length"), 0) else G_series_of(None))
        myHighLineId_2 = G_paint(myHighSeries_2, J.obj(("name", J.add("Weekly R", J.add(i_2, 1))), ("color", weeklyColor), ("thickness", weeklyThickness), ("style", weeklyStyle)))
        myLowLineId_2 = G_paint(myLowSeries_2, J.obj(("name", J.add("Weekly S", J.add(i_2, 1))), ("color", weeklyColor), ("thickness", weeklyThickness), ("style", weeklyStyle)))
        if (J.truthy(showLabels) and J.gt(J.get(myHighPivot_2, "length"), 0)):
            G_paint_label_at_line(myHighLineId_2, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myHighPivot_2, 0), "price"), "W"), J.obj(("color", weeklyColor), ("vertical_align", "middle")))
        if (J.truthy(showLabels) and J.gt(J.get(myLowPivot_2, "length"), 0)):
            G_paint_label_at_line(myLowLineId_2, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myLowPivot_2, 0), "price"), "W"), J.obj(("color", weeklyColor), ("vertical_align", "middle")))
        i_2 = J.inc(i_2)
    i_3 = 0
    while J.lt(i_3, MAX_LEVELS):
        myActive_3 = (J.lt(i_3, myNumLevels) if J.truthy(_t3 := showDaily) else _t3)
        myHighPivot_3 = (J.JSArray([J.get(myDailyHighLevels, i_3)]) if (J.truthy(myActive_3) and J.truthy(J.get(myDailyHighLevels, i_3))) else J.JSArray([]))
        myLowPivot_3 = (J.JSArray([J.get(myDailyLowLevels, i_3)]) if (J.truthy(myActive_3) and J.truthy(J.get(myDailyLowLevels, i_3))) else J.JSArray([]))
        myHighSeries_3 = (createLevelSeries(myHighPivot_3, J.get(dailyData, "time")) if J.gt(J.get(myHighPivot_3, "length"), 0) else G_series_of(None))
        myLowSeries_3 = (createLevelSeries(myLowPivot_3, J.get(dailyData, "time")) if J.gt(J.get(myLowPivot_3, "length"), 0) else G_series_of(None))
        myHighLineId_3 = G_paint(myHighSeries_3, J.obj(("name", J.add("Daily R", J.add(i_3, 1))), ("color", dailyColor), ("thickness", dailyThickness), ("style", dailyStyle)))
        myLowLineId_3 = G_paint(myLowSeries_3, J.obj(("name", J.add("Daily S", J.add(i_3, 1))), ("color", dailyColor), ("thickness", dailyThickness), ("style", dailyStyle)))
        if (J.truthy(showLabels) and J.gt(J.get(myHighPivot_3, "length"), 0)):
            G_paint_label_at_line(myHighLineId_3, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myHighPivot_3, 0), "price"), "D"), J.obj(("color", dailyColor), ("vertical_align", "middle")))
        if (J.truthy(showLabels) and J.gt(J.get(myLowPivot_3, "length"), 0)):
            G_paint_label_at_line(myLowLineId_3, J.sub(J.get(G_close, "length"), 1), generateLabelText(J.get(J.get(myLowPivot_3, 0), "price"), "D"), J.obj(("color", dailyColor), ("vertical_align", "middle")))
        i_3 = J.inc(i_3)


register_store_indicator(
    script,
    name='mtf_support_resistance_TS',
    title='MTF Support & Resistance',
    developer='Mohamed Algendy',
    url='https://trendspider.com/trading-tools-store/indicators/69f3a5-mtf-support-resistance/',
    position='price',
    inputs=[{'id': 'number_of_levels', 'title': 'Number of Levels', 'type': 'number', 'default': 1}, {'id': 'pivot_lookback', 'title': 'Pivot Lookback', 'type': 'number', 'default': 5}, {'id': 'show_monthly', 'title': 'Show Monthly', 'type': 'boolean', 'default': True}, {'id': 'show_weekly', 'title': 'Show Weekly', 'type': 'boolean', 'default': True}, {'id': 'show_daily', 'title': 'Show Daily', 'type': 'boolean', 'default': True}, {'id': 'show_labels', 'title': 'Show Labels', 'type': 'boolean', 'default': True}, {'id': 'show_tf_tag', 'title': 'Show TF Tag', 'type': 'boolean', 'default': True}],
    outputs=['monthly_r1', 'monthly_s1', 'monthly_r2', 'monthly_s2', 'monthly_r3', 'monthly_s3', 'monthly_r4', 'monthly_s4', 'monthly_r5', 'monthly_s5', 'weekly_r1', 'weekly_s1', 'weekly_r2', 'weekly_s2', 'weekly_r3', 'weekly_s3', 'weekly_r4', 'weekly_s4', 'weekly_r5', 'weekly_s5', 'daily_r1', 'daily_s1', 'daily_r2', 'daily_s2', 'daily_r3', 'daily_s3', 'daily_r4', 'daily_s4', 'daily_r5', 'daily_s5'],
    signals=[],
    requires=['history'],
    parity='exact',
)
