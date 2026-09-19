"""
Futures pre-market range by SmallSteps -- TrendSpider store indicator by SmallSteps.

Registered as "futures_pre_market_range_by_smallsteps_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab05-futures-pre-market-range-by-smallsteps/)
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
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def adjustTime(hour=J.undefined, *_args):
        return (J.mod(J.add(J.sub(hour, localTimeDiff), 24), 24) if J.truthy(useFuturesTime) else J.mod(hour, 24))
    G_describe_indicator("Futures pre-market range by SmallSteps", "overlay")
    G_assert((_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.lt(G_Number(J.get(G_current, "resolution")), 120)) else J.get(J.get(G_current, "resolution"), "endsWith")("S"))) else J.get(J.get(G_current, "resolution"), "endsWith")("T")), "This indicator only supports chart resolutions less than 120 minutes.")
    nyseStartHour = J.get(G_input, "number")("Start Hour", 17, J.obj(("min", 0), ("max", 23)))
    nyseStartMinute = J.get(G_input, "number")("Start Minute", 0, J.obj(("min", 0), ("max", 59)))
    nyseEndHour = J.get(G_input, "number")("End Hour", 8, J.obj(("min", 0), ("max", 23)))
    nyseEndMinute = J.get(G_input, "number")("End Minute", 29, J.obj(("min", 0), ("max", 59)))
    useFuturesTime = J.get(G_input, "boolean")("Use Time Diff Cal", False, J.obj(("hide_in_legend", True)))
    localTimeDiff = J.get(G_input, "number")("local-Mountain Time Diff", 1, J.obj(("min", 0), ("max", 11), ("hide_in_legend", True)))
    showBreakoutSignal = J.get(G_input, "boolean")("Breakout", True)
    showBreakdownSignal = J.get(G_input, "boolean")("Breakdown", True)
    signalDuringRange = J.get(G_input, "boolean")("Signal pre-mkt", False, J.obj(("hide_in_legend", True)))
    colorCandles = J.get(G_input, "boolean")("Color pre-mkt", False)
    myCandleColors = G_series_of(None)
    myInRangeStartSignal = G_series_of(False)
    myInRangeEndSignal = G_series_of(False)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        myDate = G_time_of(J.get(G_time, i))
        myStartHour = adjustTime(nyseStartHour)
        myEndHour = adjustTime(nyseEndHour)
        myInRange_2 = J.undefined
        if J.lt(myStartHour, myEndHour):
            myInRange_2 = ((_t6 if J.truthy(_t6 := J.lt(J.get(myDate, "hours"), myEndHour)) else (J.le(J.get(myDate, "minutes"), nyseEndMinute) if J.truthy(_t7 := J.seq(J.get(myDate, "hours"), myEndHour)) else _t7)) if J.truthy(_t3 := (_t4 if J.truthy(_t4 := J.gt(J.get(myDate, "hours"), myStartHour)) else (J.ge(J.get(myDate, "minutes"), nyseStartMinute) if J.truthy(_t5 := J.seq(J.get(myDate, "hours"), myStartHour)) else _t5))) else _t3)
        else:
            myInRange_2 = (_t8 if J.truthy(_t8 := (_t9 if J.truthy(_t9 := J.gt(J.get(myDate, "hours"), myStartHour)) else (J.ge(J.get(myDate, "minutes"), nyseStartMinute) if J.truthy(_t10 := J.seq(J.get(myDate, "hours"), myStartHour)) else _t10))) else (_t11 if J.truthy(_t11 := J.lt(J.get(myDate, "hours"), myEndHour)) else (J.le(J.get(myDate, "minutes"), nyseEndMinute) if J.truthy(_t12 := J.seq(J.get(myDate, "hours"), myEndHour)) else _t12)))
        J.set(myCandleColors, i, ("gray" if J.truthy(myInRange_2) else None))
        J.set(myInRangeStartSignal, i, (J.seq(J.get(myCandleColors, i), "gray") if J.truthy(_t13 := (J.sne(J.get(myCandleColors, J.sub(i, 1)), "gray") if J.truthy(_t14 := J.gt(i, 0)) else _t14)) else _t13))
        J.set(myInRangeEndSignal, i, (J.sne(J.get(myCandleColors, i), "gray") if J.truthy(_t15 := (J.seq(J.get(myCandleColors, J.sub(i, 1)), "gray") if J.truthy(_t16 := J.gt(i, 0)) else _t16)) else _t15))
        i = J.inc(i)
    if J.truthy(colorCandles):
        G_color_candles(myCandleColors)
    myRangeHigh = G_series_of(None)
    myRangeLow = G_series_of(None)
    myCurrentHigh = None
    myCurrentLow = None
    myInRange = False
    i_2 = 0
    while J.lt(i_2, J.get(G_time, "length")):
        if J.truthy(J.get(myInRangeStartSignal, i_2)):
            myInRange = True
            myCurrentHigh = J.get(G_high, i_2)
            myCurrentLow = J.get(G_low, i_2)
        elif J.truthy(J.get(myInRangeEndSignal, i_2)):
            myInRange = False
        if J.truthy(myInRange):
            myCurrentHigh = J.get(G_Math, "max")(myCurrentHigh, J.get(G_high, i_2))
            myCurrentLow = J.get(G_Math, "min")(myCurrentLow, J.get(G_low, i_2))
            J.set(myRangeHigh, i_2, myCurrentHigh)
            J.set(myRangeLow, i_2, myCurrentLow)
        if (not J.truthy(myInRange)):
            myCurrentHigh = None
            myCurrentLow = None
            J.set(myRangeHigh, i_2, J.get(myRangeHigh, J.sub(i_2, 1)))
            J.set(myRangeLow, i_2, J.get(myRangeLow, J.sub(i_2, 1)))
        i_2 = J.inc(i_2)
    onhPainted = G_paint(myRangeHigh, J.obj(("color", "gray"), ("name", "ON-High"), ("style", "ladder")))
    G_paint_label_at_line(onhPainted, J.sub(J.get(G_close, "length"), 10), "on-H", J.obj(("color", "gray")))
    onlPainted = G_paint(myRangeLow, J.obj(("color", "gray"), ("name", "ON-Low"), ("style", "ladder")))
    G_paint_label_at_line(onlPainted, J.sub(J.get(G_close, "length"), 10), "on-L", J.obj(("color", "gray")))
    def _f17(_c=J.undefined, _h=J.undefined, _l=J.undefined, _rl=J.undefined, _cc=J.undefined, _prevSignal=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 2):
            return 0
        if ((not J.truthy(signalDuringRange)) and J.seq(_cc, "gray")):
            return 0
        if ((_prevSignal is None) or J.seq(_prevSignal, 0)):
            if ((J.lt(_c, J.get(myRangeLow, J.sub(_index, 1))) and J.lt(_l, J.get(myRangeLow, J.sub(_index, 1)))) and (J.gt(_h, J.get(myRangeLow, J.sub(_index, 1))) or J.gt(J.get(G_high, J.sub(_index, 1)), J.get(myRangeLow, J.sub(_index, 2))))):
                return "S"
        return 0
    myBreakdownSignal = G_for_every(G_close, G_high, G_low, myRangeLow, myCandleColors, _f17)
    G_register_signal(myBreakdownSignal, "Breakdown")
    if J.truthy(showBreakdownSignal):
        G_paint(myBreakdownSignal, J.obj(("style", "labels_above"), ("color", "red"), ("text", "▼"), ("textColor", "white"), ("backgroundColor", "rgba(255, 0, 0, 0.5)"), ("name", "Breakdown Signal")))
    def _f18(_c=J.undefined, _h=J.undefined, _l=J.undefined, _rh=J.undefined, _cc=J.undefined, _prevSignal=J.undefined, _index=J.undefined, *_args):
        if J.lt(_index, 2):
            return 0
        if ((not J.truthy(signalDuringRange)) and J.seq(_cc, "gray")):
            return 0
        if ((_prevSignal is None) or J.seq(_prevSignal, 0)):
            if ((J.gt(_c, J.get(myRangeHigh, J.sub(_index, 1))) and J.gt(_h, J.get(myRangeHigh, J.sub(_index, 1)))) and (J.lt(_l, J.get(myRangeHigh, J.sub(_index, 1))) or J.lt(J.get(G_low, J.sub(_index, 1)), J.get(myRangeHigh, J.sub(_index, 2))))):
                return "L"
        return 0
    myBreakoutSignal = G_for_every(G_close, G_high, G_low, myRangeHigh, myCandleColors, _f18)
    G_register_signal(myBreakoutSignal, "Breakout")
    if J.truthy(showBreakoutSignal):
        G_paint(myBreakoutSignal, J.obj(("style", "labels_below"), ("color", "green"), ("text", "▲"), ("textColor", "white"), ("backgroundColor", "rgba(0, 255, 0, 0.5)"), ("name", "Breakout Signal")))


register_store_indicator(
    script,
    name='futures_pre_market_range_by_smallsteps_TS',
    title='Futures pre-market range by SmallSteps',
    developer='SmallSteps',
    url='https://trendspider.com/trading-tools-store/indicators/68ab05-futures-pre-market-range-by-smallsteps/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
