"""
Ultimate Key Levels -- TrendSpider store indicator by Rock Regan.

Registered as "ultimate_key_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69482d-ultimate-key-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_bar_at = G["bar_at"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_session_of = G["session_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def isMarketHours(timestamp=J.undefined, *_args):
        timeOfDay = G_time_of(timestamp)
        return ((_t4 if J.truthy(_t4 := J.lt(J.get(timeOfDay, "hours"), J.get(marketClose, "hours"))) else (J.le(J.get(timeOfDay, "minutes"), J.get(marketClose, "minutes")) if J.truthy(_t5 := J.seq(J.get(timeOfDay, "hours"), J.get(marketClose, "hours"))) else _t5)) if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.gt(J.get(timeOfDay, "hours"), J.get(marketOpen, "hours"))) else (J.ge(J.get(timeOfDay, "minutes"), J.get(marketOpen, "minutes")) if J.truthy(_t3 := J.seq(J.get(timeOfDay, "hours"), J.get(marketOpen, "hours"))) else _t3))) else _t1)
    def getOpeningRangeHighLow(*_args):
        openingRangeHighs_2 = G_series_of(None)
        openingRangeLows_2 = G_series_of(None)
        labelIndices_2 = J.obj(("high", J.JSArray([])), ("low", J.JSArray([])))
        currentDay = None
        openingRangeHigh = J.neg(G_Infinity)
        openingRangeLow = G_Infinity
        rangeSetTime = None
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            date = G_time_of(J.get(G_time, i))
            day = J.get(date, "dayOfYear")
            if J.sne(day, currentDay):
                currentDay = day
                openingRangeHigh = J.neg(G_Infinity)
                openingRangeLow = G_Infinity
                rangeSetTime = None
            if ((J.gt(J.get(date, "hours"), startHour) or (J.seq(J.get(date, "hours"), startHour) and J.ge(J.get(date, "minutes"), startMinute))) and (J.lt(J.get(date, "hours"), endHour) or (J.seq(J.get(date, "hours"), endHour) and J.lt(J.get(date, "minutes"), endMinute)))):
                if J.gt(J.get(G_high, i), openingRangeHigh):
                    openingRangeHigh = J.get(G_high, i)
                if J.lt(J.get(G_low, i), openingRangeLow):
                    openingRangeLow = J.get(G_low, i)
            if ((J.seq(J.get(date, "hours"), endHour) and J.seq(J.get(date, "minutes"), endMinute)) and (not J.truthy(rangeSetTime))):
                rangeSetTime = J.get(G_time, i)
                J.get(J.get(labelIndices_2, "high"), "push")(i)
                J.get(J.get(labelIndices_2, "low"), "push")(i)
            J.set(openingRangeHighs_2, i, openingRangeHigh)
            J.set(openingRangeLows_2, i, openingRangeLow)
            i = J.inc(i)
        return J.obj(("openingRangeHighs", openingRangeHighs_2), ("openingRangeLows", openingRangeLows_2), ("labelIndices", labelIndices_2))
    def getPreMarketRange(*_args):
        extHoursData = J.get(G_request, "history")(J.get(G_constants, "ticker"), "30", J.obj(("ext_session", True)))
        G_assert((not J.truthy(J.get(extHoursData, "error"))), J.template("Error fetching data for ", J.get(G_constants, "ticker")))
        preMarketRangeByDay_2 = J.obj()
        i = 0
        while J.lt(i, J.get(J.get(extHoursData, "time"), "length")):
            sessionAtCandle = G_session_of(J.get(J.get(extHoursData, "time"), i), J.get(G_constants, "resolution"), J.get(G_constants, "ext_session_premarket"))
            dayOfCandle = J.get(sessionAtCandle, "session")
            if (not J.truthy(J.get(preMarketRangeByDay_2, dayOfCandle))):
                J.set(preMarketRangeByDay_2, dayOfCandle, J.obj(("high", J.get(J.get(extHoursData, "high"), i)), ("low", J.get(J.get(extHoursData, "low"), i))))
            else:
                J.set(J.get(preMarketRangeByDay_2, dayOfCandle), "high", J.get(G_Math, "max")(J.get(J.get(preMarketRangeByDay_2, dayOfCandle), "high"), J.get(J.get(extHoursData, "high"), i)))
                J.set(J.get(preMarketRangeByDay_2, dayOfCandle), "low", J.get(G_Math, "min")(J.get(J.get(preMarketRangeByDay_2, dayOfCandle), "low"), J.get(J.get(extHoursData, "low"), i)))
            i = J.inc(i)
        return preMarketRangeByDay_2
    G_describe_indicator("Ultimate Key Levels", "price", J.obj(("shortName", "Ult Levels ")))
    G_assert((not J.truthy(J.get(J.JSArray(["D", "W", "M", "Q", "Y"]), "includes")(J.get(G_constants, "resolution")))), J.template("not applicable to \"", J.get(G_constants, "resolution"), "\" charts"))
    showLabels = J.get(G_input, "boolean")("Show Labels", False)
    startHour = J.get(G_input, "number")("ORB Start Hour", 9, J.obj(("min", 0), ("max", 23)))
    startMinute = J.get(G_input, "number")("ORB Start Minute", 30, J.obj(("min", 0), ("max", 59)))
    endHour = J.get(G_input, "number")("ORB End Hour", 10, J.obj(("min", 0), ("max", 23)))
    endMinute = J.get(G_input, "number")("ORB End Minute", 0, J.obj(("min", 0), ("max", 59)))
    lookbackPeriod = J.get(G_input, "number")("Lookback Period", 1, J.obj(("min", 1), ("max", 10)))
    marketOpen = J.obj(("hours", 9), ("minutes", 30))
    marketClose = J.obj(("hours", 16), ("minutes", 0))
    dailyData = J.get(G_request, "history")(J.get(G_constants, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
    highLevels = G_series_of(None)
    lowLevels = G_series_of(None)
    closeLevels = G_series_of(None)
    i = 0
    while J.lt(i, lookbackPeriod):
        dailyIndex = J.sub(J.sub(J.get(J.get(dailyData, "close"), "length"), 2), i)
        if J.ge(dailyIndex, 0):
            prevDayHigh = J.get(J.get(dailyData, "high"), dailyIndex)
            prevDayLow = J.get(J.get(dailyData, "low"), dailyIndex)
            prevDayClose = J.get(J.get(dailyData, "close"), dailyIndex)
            def _f1(t=J.undefined, *_args):
                return J.ge(t, J.get(J.get(dailyData, "time"), J.add(dailyIndex, 1)))
            startIndex = J.get(G_time, "findIndex")(_f1)
            if J.sne(startIndex, (-1)):
                j = startIndex
                while J.lt(j, J.get(G_time, "length")):
                    J.set(highLevels, j, prevDayHigh)
                    J.set(lowLevels, j, prevDayLow)
                    J.set(closeLevels, j, prevDayClose)
                    j = J.inc(j)
        i = J.inc(i)
    def findSessionStart(index=J.undefined, *_args):
        currentSession = G_session_of(J.get(G_time, index), J.get(G_constants, "resolution"))
        while (J.gt(index, 0) and J.seq(J.get(G_session_of(J.get(G_time, J.sub(index, 1)), J.get(G_constants, "resolution")), "session"), J.get(currentSession, "session"))):
            index = J.dec(index)
        return index
    highOfDayByDay = J.obj()
    lowOfDayByDay = J.obj()
    highOfDayLabels = G_series_of(None)
    lowOfDayLabels = G_series_of(None)
    myNhodSignal = G_series_of(False)
    myNlodSignal = G_series_of(False)
    i_2 = 0
    while J.lt(i_2, J.get(G_time, "length")):
        sessionAtCandle = G_bar_at(J.get(G_time, i_2), "D")
        dayOfCandle = J.get(sessionAtCandle, "session")
        if J.truthy(isMarketHours(J.get(G_time, i_2))):
            if (not J.truthy(J.get(highOfDayByDay, dayOfCandle))):
                J.set(highOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_high, i_2)), ("index", i_2)))
                J.set(myNhodSignal, i_2, True)
            else:
                if J.gt(J.get(G_high, i_2), J.get(J.get(highOfDayByDay, dayOfCandle), "value")):
                    J.set(highOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_high, i_2)), ("index", i_2)))
                    J.set(myNhodSignal, i_2, True)
            if (not J.truthy(J.get(lowOfDayByDay, dayOfCandle))):
                J.set(lowOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_low, i_2)), ("index", i_2)))
                J.set(myNlodSignal, i_2, True)
            else:
                if J.lt(J.get(G_low, i_2), J.get(J.get(lowOfDayByDay, dayOfCandle), "value")):
                    J.set(lowOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_low, i_2)), ("index", i_2)))
                    J.set(myNlodSignal, i_2, True)
        i_2 = J.inc(i_2)
    _t2 = J.require_object(getOpeningRangeHighLow())
    openingRangeHighs = J.get(_t2, "openingRangeHighs")
    openingRangeLows = J.get(_t2, "openingRangeLows")
    labelIndices = J.get(_t2, "labelIndices")
    preMarketRangeByDay = getPreMarketRange()
    rangeHigh = G_series_of(None)
    rangeLow = G_series_of(None)
    lastSession = G_session_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)), J.get(G_constants, "resolution"))
    i_3 = 0
    while J.lt(i_3, J.get(G_time, "length")):
        sessionAtCandle_2 = G_session_of(J.get(G_time, i_3), J.get(G_constants, "resolution"))
        isLastSession = J.eq(J.get(sessionAtCandle_2, "session"), J.get(lastSession, "session"))
        extHoursRange = J.get(preMarketRangeByDay, J.get(sessionAtCandle_2, "session"))
        if (J.truthy(isLastSession) and J.truthy(extHoursRange)):
            J.set(rangeHigh, i_3, J.get(extHoursRange, "high"))
            J.set(rangeLow, i_3, J.get(extHoursRange, "low"))
        if (J.ne(J.get(rangeHigh, i_3), J.get(rangeHigh, J.sub(i_3, 1))) or J.ne(J.get(rangeLow, i_3), J.get(rangeLow, J.sub(i_3, 1)))):
            J.set(rangeHigh, J.sub(i_3, 1), None)
            J.set(rangeLow, J.sub(i_3, 1), None)
        i_3 = J.inc(i_3)
    hodRangeHigh = G_series_of(None)
    hodRangeLow = G_series_of(None)
    i_4 = 0
    while J.lt(i_4, J.get(G_time, "length")):
        sessionAtCandle_3 = G_bar_at(J.get(G_time, i_4), "D")
        dayOfCandle_2 = J.get(sessionAtCandle_3, "session")
        if J.truthy(J.get(highOfDayByDay, dayOfCandle_2)):
            J.set(hodRangeHigh, i_4, J.get(J.get(highOfDayByDay, dayOfCandle_2), "value"))
        if J.truthy(J.get(lowOfDayByDay, dayOfCandle_2)):
            J.set(hodRangeLow, i_4, J.get(J.get(lowOfDayByDay, dayOfCandle_2), "value"))
        i_4 = J.inc(i_4)
    orbHighLine = G_paint(openingRangeHighs, J.obj(("style", "line"), ("color", "#bbbbbb"), ("thickness", 0.5), ("name", "OR High")))
    orbLowLine = G_paint(openingRangeLows, J.obj(("style", "line"), ("color", "#bbbbbb"), ("thickness", 0.5), ("name", "OR Low")))
    G_fill(orbHighLine, orbLowLine, "#A3A3A3CC", 0.25, "OR Range")
    if J.truthy(showLabels):
        def _f3(index=J.undefined, *_args):
            G_paint_label_at_line(orbHighLine, index, "ORBH", J.obj(("color", "white"), ("background_color", "green"), ("vertical_align", "middle")))
        J.get(J.get(labelIndices, "high"), "forEach")(_f3)
        def _f4(index=J.undefined, *_args):
            G_paint_label_at_line(orbLowLine, index, "ORBL", J.obj(("color", "white"), ("background_color", "red"), ("vertical_align", "middle")))
        J.get(J.get(labelIndices, "low"), "forEach")(_f4)
    pmHighLine = G_paint(rangeHigh, J.obj(("style", "ladder"), ("thickness", 1), ("color", "palegreen"), ("name", "PM High")))
    pmLowLine = G_paint(rangeLow, J.obj(("style", "ladder"), ("thickness", 1), ("color", "pink"), ("name", "PM Low")))
    if J.truthy(showLabels):
        G_paint_label_at_line(pmHighLine, J.sub(J.get(G_close, "length"), 25), "PMH", J.obj(("color", "black"), ("background_color", "palegreen"), ("vertical_align", "middle")))
        G_paint_label_at_line(pmLowLine, J.sub(J.get(G_close, "length"), 25), "PML", J.obj(("color", "black"), ("background_color", "pink"), ("vertical_align", "middle")))
    prevDayHighLine = G_paint(highLevels, J.obj(("color", "lime"), ("style", "dotted"), ("name", "Previous Day High"), ("thickness", 1.5)))
    prevDayLowLine = G_paint(lowLevels, J.obj(("color", "crimson"), ("style", "dotted"), ("name", "Previous Day Low"), ("thickness", 1.5)))
    prevDayCloseLine = G_paint(closeLevels, J.obj(("color", "DodgerBlue"), ("style", "dotted"), ("name", "Previous Day Close"), ("thickness", 1.5)))
    if J.truthy(showLabels):
        sessionStartIndex = findSessionStart(J.sub(J.get(G_close, "length"), 1))
        G_paint_label_at_line(prevDayHighLine, sessionStartIndex, "PDay H", J.obj(("color", "white"), ("background_color", "lime"), ("vertical_align", "middle")))
        G_paint_label_at_line(prevDayLowLine, sessionStartIndex, "PDay L", J.obj(("color", "white"), ("background_color", "crimson"), ("vertical_align", "middle")))
        G_paint_label_at_line(prevDayCloseLine, sessionStartIndex, "PDay C", J.obj(("color", "white"), ("background_color", "DodgerBlue"), ("vertical_align", "middle")))
    G_paint(hodRangeHigh, J.obj(("style", "ladder"), ("color", "#00FF00"), ("thickness", 0.5), ("name", "HOD")))
    G_paint(hodRangeLow, J.obj(("style", "ladder"), ("color", "#FF0000"), ("thickness", 0.5), ("name", "LOD")))
    for day in J.iter_in(highOfDayByDay):
        if J.truthy(J.get(highOfDayByDay, "hasOwnProperty")(day)):
            highPoint = J.get(highOfDayByDay, day)
            if J.seq(J.get(G_session_of(J.get(G_time, J.get(highPoint, "index")), J.get(G_constants, "resolution")), "session"), J.get(lastSession, "session")):
                J.set(highOfDayLabels, J.get(highPoint, "index"), J.template("NHOD: ", J.get(J.get(highPoint, "value"), "toFixed")(2)))
    for day_2 in J.iter_in(lowOfDayByDay):
        if J.truthy(J.get(lowOfDayByDay, "hasOwnProperty")(day_2)):
            lowPoint = J.get(lowOfDayByDay, day_2)
            if J.seq(J.get(G_session_of(J.get(G_time, J.get(lowPoint, "index")), J.get(G_constants, "resolution")), "session"), J.get(lastSession, "session")):
                J.set(lowOfDayLabels, J.get(lowPoint, "index"), J.template("NLOD: ", J.get(J.get(lowPoint, "value"), "toFixed")(2)))
    G_paint(highOfDayLabels, J.obj(("style", "labels_above"), ("color", "white"), ("backgroundColor", "green"), ("backgroundOpacity", ".7"), ("verticalOffset", 10), ("name", "NHOD Label")))
    G_paint(lowOfDayLabels, J.obj(("style", "labels_below"), ("color", "white"), ("backgroundColor", "red"), ("backgroundOpacity", ".7"), ("verticalOffset", 10), ("name", "NLOD Label")))
    G_register_signal(myNhodSignal, "New High of Day")
    G_register_signal(myNlodSignal, "New Low of Day")


register_store_indicator(
    script,
    name='ultimate_key_levels_TS',
    title='Ultimate Key Levels',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69482d-ultimate-key-levels/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='aapl_d: both-error, syn_5m: OK',
)
