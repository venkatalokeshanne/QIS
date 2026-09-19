"""
Fringe™️ -- TrendSpider store indicator by M4RK4R4.

Registered as "fringe_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a231-fringe/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Fringe™️")
    moment = G_library("moment-timezone")
    showDeviationLines = J.get(G_input, "boolean")("Show Deviation Lines", True)
    showFriday1600Line = J.get(G_input, "boolean")("Show Friday 16:00 Line", True)
    def isFridayRangeStart(timestamp=J.undefined, *_args):
        date = moment(J.mul(timestamp, 1000))
        return (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := (J.ge(J.get(date, "hour")(), 18) if J.truthy(_t3 := J.seq(J.get(date, "day")(), 4)) else _t3)) else J.seq(J.get(date, "day")(), 5))) else (J.seq(J.get(J.get(date, "subtract")(1, "day"), "day")(), 5) if J.truthy(_t4 := J.seq(J.get(date, "day")(), 6)) else _t4))
    def isFridayRangeEnd(timestamp=J.undefined, *_args):
        date = moment(J.mul(timestamp, 1000))
        return (J.ge(J.get(date, "hour")(), 18) if J.truthy(_t1 := J.seq(J.get(date, "day")(), 5)) else _t1)
    def getDayOfWeek(timestamp=J.undefined, *_args):
        return J.get(moment(J.mul(timestamp, 1000)), "format")("ddd")
    def isFriday1600(timestamp=J.undefined, *_args):
        date = moment(J.mul(timestamp, 1000))
        return (J.seq(J.get(date, "minute")(), 0) if J.truthy(_t1 := (J.seq(J.get(date, "hour")(), 16) if J.truthy(_t2 := J.seq(J.get(date, "day")(), 5)) else _t2)) else _t1)
    fridayHigh = G_series_of(None)
    fridayLow = G_series_of(None)
    fridayMid = G_series_of(None)
    friday853 = G_series_of(None)
    friday147 = G_series_of(None)
    friday1111 = G_series_of(None)
    fridayMinus0111 = G_series_of(None)
    friday1600Line = G_series_of(None)
    lastFridayRangeStartIndex = (-1)
    currentFridayHigh = None
    currentFridayLow = None
    candleColors = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        if J.truthy(isFridayRangeStart(J.get(G_time, i))):
            if (J.seq(lastFridayRangeStartIndex, (-1)) or J.gt(J.sub(i, lastFridayRangeStartIndex), 1)):
                currentFridayHigh = J.get(G_high, i)
                currentFridayLow = J.get(G_low, i)
            else:
                currentFridayHigh = J.get(G_Math, "max")(currentFridayHigh, J.get(G_high, i))
                currentFridayLow = J.get(G_Math, "min")(currentFridayLow, J.get(G_low, i))
            J.set(fridayHigh, i, currentFridayHigh)
            J.set(fridayLow, i, currentFridayLow)
            J.set(fridayMid, i, J.div(J.add(currentFridayHigh, currentFridayLow), 2))
            J.set(friday853, i, J.add(currentFridayLow, J.mul(J.sub(currentFridayHigh, currentFridayLow), 0.853)))
            J.set(friday147, i, J.add(currentFridayLow, J.mul(J.sub(currentFridayHigh, currentFridayLow), 0.147)))
            J.set(friday1111, i, J.add(J.get(fridayMid, i), J.mul(J.sub(currentFridayHigh, currentFridayLow), 1)))
            J.set(fridayMinus0111, i, J.sub(J.get(fridayMid, i), J.mul(J.sub(currentFridayHigh, currentFridayLow), 1)))
            lastFridayRangeStartIndex = i
        elif (J.sne(lastFridayRangeStartIndex, (-1)) and (not J.truthy(isFridayRangeEnd(J.get(G_time, i))))):
            J.set(fridayHigh, i, J.get(fridayHigh, lastFridayRangeStartIndex))
            J.set(fridayLow, i, J.get(fridayLow, lastFridayRangeStartIndex))
            J.set(fridayMid, i, J.get(fridayMid, lastFridayRangeStartIndex))
            J.set(friday853, i, J.get(friday853, lastFridayRangeStartIndex))
            J.set(friday147, i, J.get(friday147, lastFridayRangeStartIndex))
            J.set(friday1111, i, J.get(friday1111, lastFridayRangeStartIndex))
            J.set(fridayMinus0111, i, J.get(fridayMinus0111, lastFridayRangeStartIndex))
        if J.truthy(isFriday1600(J.get(G_time, i))):
            J.set(candleColors, i, "#FF00FF")
            J.set(friday1600Line, i, J.get(G_close, i))
        elif (J.gt(i, 0) and (J.get(friday1600Line, J.sub(i, 1)) is not None)):
            J.set(friday1600Line, i, J.get(friday1600Line, J.sub(i, 1)))
        i = J.inc(i)
    highLine = G_paint(fridayHigh, J.obj(("name", "Fringe High"), ("color", "purple"), ("style", "line")))
    G_paint(fridayMid, J.obj(("name", "Fringe Mid"), ("color", "purple"), ("style", "line")))
    G_paint(fridayLow, J.obj(("name", "Fringe Low"), ("color", "purple"), ("style", "line")))
    G_paint(friday853, J.obj(("name", "Fringe 85.3%"), ("color", "purple"), ("style", "line")))
    G_paint(friday147, J.obj(("name", "Fringe 14.7%"), ("color", "purple"), ("style", "line")))
    if J.truthy(showDeviationLines):
        G_paint(friday1111, J.obj(("name", "Upper Deviation"), ("color", "blue"), ("style", "line")))
        G_paint(fridayMinus0111, J.obj(("name", "Lower Deviation"), ("color", "blue"), ("style", "line")))
    if J.truthy(showFriday1600Line):
        G_paint(friday1600Line, J.obj(("name", "Friday 16:00"), ("color", "magenta"), ("style", "dotted")))
    lastDayOfWeek = ""
    i_2 = 0
    while J.lt(i_2, J.get(G_time, "length")):
        dayOfWeek = getDayOfWeek(J.get(G_time, i_2))
        if J.sne(dayOfWeek, lastDayOfWeek):
            G_paint_label_at_line(highLine, i_2, dayOfWeek, J.obj(("color", "gray"), ("vertical_align", "top")))
            lastDayOfWeek = dayOfWeek
        i_2 = J.inc(i_2)
    G_color_candles(candleColors)


register_store_indicator(
    script,
    name='fringe_TS',
    title='Fringe™️',
    developer='M4RK4R4',
    url='https://trendspider.com/trading-tools-store/indicators/68a231-fringe/',
    position='price',
    inputs=[{'id': 'show_deviation_lines', 'title': 'Show Deviation Lines', 'type': 'boolean', 'default': True}, {'id': 'show_friday_16_00_line', 'title': 'Show Friday 16:00 Line', 'type': 'boolean', 'default': True}],
    outputs=['fringe_high', 'fringe_mid', 'fringe_low', 'fringe_85_3_', 'fringe_14_7_', 'upper_deviation', 'lower_deviation', 'friday_16_00', 'cdl'],
    signals=[],
    requires=[],
    parity='exact',
)
