"""
Futures Gap Labels by SmallSteps -- TrendSpider store indicator by SmallSteps.

Registered as "futures_gap_labels_by_smallsteps_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab14-futures-gap-labels-by-smallsteps/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Futures Gap Labels by SmallSteps")
    myTimeframe = J.get(G_current, "resolution")
    myTime1 = J.get(G_input, "number")("Start Mountain Time", 830, J.obj(("min", 0), ("max", 2359)))
    overrideEndTimeVal = J.get(G_input, "number")("End Mountain Time", 1455, J.obj(("min", 0), ("max", 2359), ("hide_in_legend", True)))
    overrideEndTime = J.get(G_input, "boolean")("Use End Time", False, J.obj(("hide_in_legend", True)))
    myColorAtTime1 = J.get(G_input, "color")("Color 1st and Last Time", "blue", J.obj(("hide_in_legend", True)))
    myColorAtTime2 = myColorAtTime1
    myGapThreshold = J.get(G_input, "number")("Gap Threshold", 5, J.obj(("min", 0)))
    myColorCandle = J.get(G_input, "boolean")("Color Candle", False, J.obj(("hide_in_legend", True)))
    myTrueGap = J.get(G_input, "boolean")("Use Prev H/L", False)
    debugDisplay = J.get(G_input, "boolean")("Debug Display", True, J.obj(("hide_in_legend", True)))
    myMaxSignals = J.get(G_input, "number")("Max Signals", 5, J.obj(("min", 1), ("max", 50), ("hide_in_legend", True)))
    G_assert((J.le(G_Number(J.get(G_current, "resolution")), 30) if J.truthy(_t1 := J.ge(G_Number(J.get(G_current, "resolution")), 5)) else _t1), "This indicator only supports chart resolutions 5, 10 , 15 and 30 minutes.")
    def getHoursAndMinutes(_time=J.undefined, *_args):
        myHours = J.get(G_Math, "floor")(J.div(_time, 100))
        myMinutes = J.mod(_time, 100)
        return J.obj(("hours", myHours), ("minutes", myMinutes))
    myTime2 = J.undefined
    if J.truthy(overrideEndTime):
        myTime2 = overrideEndTimeVal
    else:
        if J.eq(myTimeframe, "5"):
            myTime2 = 1455
        elif J.eq(myTimeframe, "10"):
            myTime2 = 1450
        elif J.eq(myTimeframe, "15"):
            myTime2 = 1445
        elif J.eq(myTimeframe, "30"):
            myTime2 = 1430
    myTime1Values = getHoursAndMinutes(myTime1)
    myTime2Values = getHoursAndMinutes(myTime2)
    myCandleColors = G_series_of(None)
    myLabelPrices = G_series_of(None)
    gapCloseDisplay1 = G_series_of(None)
    gapCloseDisplay2 = G_series_of(None)
    myGapSignal = G_series_of(False)
    myGapShortSignal = G_series_of(False)
    myGapLongSignal = G_series_of(False)
    myPrevSessionTime2Price = None
    myPrevSessionHigh = None
    myPrevSessionLow = None
    myCurrentSessionHigh = None
    myCurrentSessionLow = None
    myFirstCandleHigh = None
    myFirstCandleLow = None
    myFirstCandleOpen = None
    myGapOccuredAbove = False
    myGapOccuredBelow = False
    myGapShortSignalOccurred = 0
    myGapLongSignalOccurred = 0
    myGapUpCloseVal = None
    myGapDownCloseVal = None
    myPrevDayHigh = G_series_of(None)
    myPrevDayLow = G_series_of(None)
    myGapCloseVal1Series = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if J.le(i, 10):
            i = J.inc(i)
            continue
        myBarTime = G_time_of(J.get(G_time, i))
        if (J.seq(J.get(myBarTime, "hours"), J.get(myTime1Values, "hours")) and J.seq(J.get(myBarTime, "minutes"), J.get(myTime1Values, "minutes"))):
            J.set(myPrevDayHigh, i, myPrevSessionHigh)
            J.set(myPrevDayLow, i, myPrevSessionLow)
            J.set(myPrevDayHigh, J.sub(i, 1), myPrevSessionHigh)
            J.set(myPrevDayHigh, J.sub(i, 2), myPrevSessionHigh)
            J.set(myPrevDayHigh, J.sub(i, 3), myPrevSessionHigh)
            J.set(myPrevDayHigh, J.sub(i, 4), myPrevSessionHigh)
            J.set(myPrevDayHigh, J.sub(i, 5), myPrevSessionHigh)
            J.set(myPrevDayLow, J.sub(i, 1), myPrevSessionLow)
            J.set(myPrevDayLow, J.sub(i, 2), myPrevSessionLow)
            J.set(myPrevDayLow, J.sub(i, 3), myPrevSessionLow)
            J.set(myPrevDayLow, J.sub(i, 4), myPrevSessionLow)
            J.set(myPrevDayLow, J.sub(i, 5), myPrevSessionLow)
            myCurrentSessionHigh = J.get(G_high, i)
            myCurrentSessionLow = J.get(G_low, i)
            myGapOccuredAbove = False
            myGapOccuredBelow = False
            myFirstCandleOpen = None
            myFirstCandleHigh = None
            myFirstCandleLow = None
            myGapShortSignalOccurred = 0
            myGapLongSignalOccurred = 0
            J.set(myCandleColors, i, myColorAtTime1)
            myFirstCandleOpen = J.get(G_open, i)
            myFirstCandleHigh = J.get(G_high, i)
            myFirstCandleLow = J.get(G_low, i)
            if J.gt(J.sub(myFirstCandleHigh, myFirstCandleLow), J.mul(2, myGapThreshold)):
                if J.ge(J.get(G_open, i), J.get(G_close, i)):
                    myFirstCandleHigh = J.get(G_open, i)
                    myFirstCandleLow = J.get(G_close, i)
                else:
                    myFirstCandleHigh = J.get(G_close, i)
                    myFirstCandleLow = J.get(G_open, i)
            if (myPrevSessionTime2Price is not None):
                myDifference = J.sub(J.get(G_open, i), myPrevSessionTime2Price)
                myGapFound = J.gt(J.get(G_Math, "abs")(myDifference), myGapThreshold)
                if J.truthy(myTrueGap):
                    if (J.gt(J.get(G_open, i), J.get(myPrevDayHigh, i)) and J.truthy(myGapFound)):
                        J.set(myLabelPrices, i, J.get(myDifference, "toFixed")(2))
                        J.set(myGapSignal, i, True)
                        myGapOccuredAbove = True
                        myGapUpCloseVal = J.sub(J.get(G_low, i), J.get(myPrevDayHigh, i))
                    elif (J.lt(J.get(G_open, i), J.get(myPrevDayLow, i)) and J.truthy(myGapFound)):
                        J.set(myLabelPrices, i, J.get(myDifference, "toFixed")(2))
                        J.set(myGapSignal, i, True)
                        myGapOccuredBelow = True
                        myGapDownCloseVal = J.sub(J.get(G_high, i), J.get(myPrevDayLow, i))
                else:
                    if J.truthy(myGapFound):
                        J.set(myLabelPrices, i, J.get(myDifference, "toFixed")(2))
                        J.set(myGapSignal, i, True)
                        if J.gt(myDifference, 0):
                            myGapOccuredAbove = True
                        else:
                            myGapOccuredBelow = True
            myPrevSessionTime2Price = None
        elif (J.seq(J.get(myBarTime, "hours"), J.get(myTime2Values, "hours")) and J.seq(J.get(myBarTime, "minutes"), J.get(myTime2Values, "minutes"))):
            J.set(myCandleColors, i, myColorAtTime2)
            myPrevSessionTime2Price = J.get(G_close, i)
            if (myCurrentSessionHigh is not None):
                myCurrentSessionHigh = J.get(G_Math, "max")(myCurrentSessionHigh, J.get(G_high, i))
                myCurrentSessionLow = J.get(G_Math, "min")(myCurrentSessionLow, J.get(G_low, i))
            myPrevSessionHigh = myCurrentSessionHigh
            myPrevSessionLow = myCurrentSessionLow
            myGapOccuredAbove = False
            myGapOccuredBelow = False
            myFirstCandleOpen = None
            myFirstCandleHigh = None
            myFirstCandleLow = None
            myGapShortSignalOccurred = 0
            myGapLongSignalOccurred = 0
            myGapUpCloseVal = None
            myGapDownCloseVal = None
        else:
            if (myCurrentSessionHigh is not None):
                myCurrentSessionHigh = J.get(G_Math, "max")(myCurrentSessionHigh, J.get(G_high, i))
                myCurrentSessionLow = J.get(G_Math, "min")(myCurrentSessionLow, J.get(G_low, i))
            if J.gt(i, 0):
                J.set(myPrevDayHigh, i, J.get(myPrevDayHigh, J.sub(i, 1)))
                J.set(myPrevDayLow, i, J.get(myPrevDayLow, J.sub(i, 1)))
            if J.truthy(myGapOccuredAbove):
                if ((J.lt(myGapLongSignalOccurred, myMaxSignals) and J.gt(J.get(G_close, i), myFirstCandleHigh)) and J.lt(J.get(G_low, i), myFirstCandleHigh)):
                    J.set(myGapLongSignal, i, True)
                    myGapLongSignalOccurred = J.inc(myGapLongSignalOccurred)
                elif ((J.lt(myGapShortSignalOccurred, myMaxSignals) and J.lt(J.get(G_close, i), myFirstCandleLow)) and J.gt(J.get(G_high, i), myFirstCandleLow)):
                    J.set(myGapShortSignal, i, True)
                    myGapShortSignalOccurred = J.inc(myGapShortSignalOccurred)
                if (J.truthy(myTrueGap) and (not J.nullish(myGapUpCloseVal))):
                    myGapUpCloseVal = J.sub(J.get(G_low, i), J.get(myPrevDayHigh, i))
                    if J.lt(myGapUpCloseVal, 0):
                        myGapUpCloseVal = None
                    else:
                        pass
                    if J.gt(J.get(G_close, i), myFirstCandleHigh):
                        myGapUpCloseVal = None
            if J.truthy(myGapOccuredBelow):
                if ((J.lt(myGapShortSignalOccurred, myMaxSignals) and J.lt(J.get(G_close, i), myFirstCandleLow)) and J.gt(J.get(G_high, i), myFirstCandleLow)):
                    J.set(myGapShortSignal, i, True)
                    myGapShortSignalOccurred = J.inc(myGapShortSignalOccurred)
                elif ((J.lt(myGapLongSignalOccurred, myMaxSignals) and J.gt(J.get(G_close, i), myFirstCandleHigh)) and J.lt(J.get(G_low, i), myFirstCandleHigh)):
                    J.set(myGapLongSignal, i, True)
                    myGapLongSignalOccurred = J.inc(myGapLongSignalOccurred)
                if (J.truthy(myTrueGap) and (not J.nullish(myGapDownCloseVal))):
                    myGapDownCloseVal = J.sub(J.get(G_high, i), J.get(myPrevDayLow, i))
                    if J.gt(myGapDownCloseVal, 0):
                        myGapDownCloseVal = None
                    else:
                        pass
                    if J.lt(J.get(G_close, i), myFirstCandleLow):
                        myGapDownCloseVal = None
        isWithinTimeRange = ((_t5 if J.truthy(_t5 := J.lt(J.get(myBarTime, "hours"), J.get(myTime2Values, "hours"))) else (J.le(J.get(myBarTime, "minutes"), J.get(myTime2Values, "minutes")) if J.truthy(_t6 := J.seq(J.get(myBarTime, "hours"), J.get(myTime2Values, "hours"))) else _t6)) if J.truthy(_t2 := (_t3 if J.truthy(_t3 := J.gt(J.get(myBarTime, "hours"), J.get(myTime1Values, "hours"))) else (J.ge(J.get(myBarTime, "minutes"), J.get(myTime1Values, "minutes")) if J.truthy(_t4 := J.seq(J.get(myBarTime, "hours"), J.get(myTime1Values, "hours"))) else _t4))) else _t2)
        if J.truthy(isWithinTimeRange):
            if (myGapUpCloseVal is not None):
                J.set(myGapCloseVal1Series, i, J.get(myGapUpCloseVal, "toFixed")(2))
            elif (myGapDownCloseVal is not None):
                J.set(myGapCloseVal1Series, i, J.get(myGapDownCloseVal, "toFixed")(2))
        i = J.inc(i)
    if J.truthy(myColorCandle):
        G_color_candles(myCandleColors)
    prevDayHighPaint = G_paint(myPrevDayHigh, J.obj(("color", "white"), ("name", "Prev Day High"), ("style", "ladder")))
    G_paint_label_at_line(prevDayHighPaint, J.sub(J.get(G_close, "length"), 5), "Y-High", J.obj(("color", "gray")))
    prevDayLowPaint = G_paint(myPrevDayLow, J.obj(("color", "white"), ("name", "Prev Day Low"), ("style", "ladder")))
    G_paint_label_at_line(prevDayLowPaint, J.sub(J.get(G_close, "length"), 5), "Y-Low", J.obj(("color", "gray")))
    G_register_signal(myGapSignal, "Gap Signal")
    G_register_signal(myGapShortSignal, "Gap Short Signal")
    G_register_signal(myGapLongSignal, "Gap Long Signal")
    def _f7(_price=J.undefined, *_args):
        return (_price if (_price is not None) else None)
    myGapLabels = G_for_every(myLabelPrices, _f7)
    def _f8(_signal=J.undefined, *_args):
        return ("S" if J.truthy(_signal) else None)
    myGapShortLabels = G_for_every(myGapShortSignal, _f8)
    def _f9(_signal=J.undefined, *_args):
        return ("L" if J.truthy(_signal) else None)
    myGapLongLabels = G_for_every(myGapLongSignal, _f9)
    G_paint(myGapLabels, J.obj(("color", "white"), ("backgroundColor", "blue"), ("name", "Gap Labels"), ("style", "labels_above")))
    if J.truthy(debugDisplay):
        G_paint(myGapShortLabels, J.obj(("color", "white"), ("backgroundColor", "rgba(255, 0, 0, 0.5)"), ("name", "Gap Short Labels"), ("style", "labels_above")))
        G_paint(myGapLongLabels, J.obj(("color", "white"), ("backgroundColor", "rgba(255, 0, 0, 0.5)"), ("name", "GapGo Long Labels"), ("style", "labels_below")))


register_store_indicator(
    script,
    name='futures_gap_labels_by_smallsteps_TS',
    title='Futures Gap Labels by SmallSteps',
    developer='SmallSteps',
    url='https://trendspider.com/trading-tools-store/indicators/68ab14-futures-gap-labels-by-smallsteps/',
    position='price',
    inputs=[{'id': 'start_mountain_time', 'title': 'Start Mountain Time', 'type': 'number', 'default': 830}, {'id': 'end_mountain_time', 'title': 'End Mountain Time', 'type': 'number', 'default': 1455}, {'id': 'use_end_time', 'title': 'Use End Time', 'type': 'boolean', 'default': False}, {'id': 'color_1st_and_last_time', 'title': 'Color 1st and Last Time', 'type': 'color', 'default': 'blue'}, {'id': 'gap_threshold', 'title': 'Gap Threshold', 'type': 'number', 'default': 5}, {'id': 'color_candle', 'title': 'Color Candle', 'type': 'boolean', 'default': False}, {'id': 'use_prev_h_l', 'title': 'Use Prev H/L', 'type': 'boolean', 'default': False}, {'id': 'debug_display', 'title': 'Debug Display', 'type': 'boolean', 'default': True}, {'id': 'max_signals', 'title': 'Max Signals', 'type': 'number', 'default': 5}],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
