"""
Pre-market High/Low -- TrendSpider store indicator by TrendSpider.

Registered as "pre_market_high_low_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69037e-pre-market-high-low/)
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
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def adjustHour(h=J.undefined, *_args):
        return (J.mod(J.add(J.sub(h, localTimeDiff), 24), 24) if J.truthy(useFuturesTime) else J.mod(h, 24))
    def inWindow(dt=J.undefined, sH=J.undefined, sM=J.undefined, eH=J.undefined, eM=J.undefined, *_args):
        if (J.lt(sH, eH) or (J.seq(sH, eH) and J.le(sM, eM))):
            return ((_t4 if J.truthy(_t4 := J.lt(J.get(dt, "hours"), eH)) else (J.le(J.get(dt, "minutes"), eM) if J.truthy(_t5 := J.seq(J.get(dt, "hours"), eH)) else _t5)) if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.gt(J.get(dt, "hours"), sH)) else (J.ge(J.get(dt, "minutes"), sM) if J.truthy(_t3 := J.seq(J.get(dt, "hours"), sH)) else _t3))) else _t1)
        else:
            return (_t6 if J.truthy(_t6 := (_t7 if J.truthy(_t7 := J.gt(J.get(dt, "hours"), sH)) else (J.ge(J.get(dt, "minutes"), sM) if J.truthy(_t8 := J.seq(J.get(dt, "hours"), sH)) else _t8))) else (_t9 if J.truthy(_t9 := J.lt(J.get(dt, "hours"), eH)) else (J.le(J.get(dt, "minutes"), eM) if J.truthy(_t10 := J.seq(J.get(dt, "hours"), eH)) else _t10)))
    G_describe_indicator("Pre-market High/Low", "overlay")
    G_assert((_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.lt(G_Number(J.get(G_current, "resolution")), 120)) else J.get(J.get(G_current, "resolution"), "endsWith")("S"))) else J.get(J.get(G_current, "resolution"), "endsWith")("T")), "This indicator only supports chart resolutions less than 120 minutes.")
    moment = G_library("moment-timezone")
    nyseStartHour = J.get(G_input, "number")("Start Hour", 4, J.obj(("min", 0), ("max", 23)))
    nyseStartMinute = J.get(G_input, "number")("Start Minute", 0, J.obj(("min", 0), ("max", 59)))
    nyseEndHour = J.get(G_input, "number")("End Hour", 9, J.obj(("min", 0), ("max", 23)))
    nyseEndMinute = J.get(G_input, "number")("End Minute", 29, J.obj(("min", 0), ("max", 59)))
    useFuturesTime = J.get(G_input, "boolean")("Use Time Diff Cal", False, J.obj(("hide_in_legend", True)))
    localTimeDiff = J.get(G_input, "number")("local-Mountain Time Diff", 1, J.obj(("min", 0), ("max", 11), ("hide_in_legend", True)))
    extHoursData = J.get(G_request, "history")(J.get(G_current, "ticker"), J.get(G_current, "resolution"), J.obj(("ext_session", True)))
    G_assert((not J.truthy(J.get(extHoursData, "error"))), J.template("Error fetching extended hours data: ", J.get(extHoursData, "error")))
    preMarketRangeByDay = J.obj()
    extIndex = 0
    while J.lt(extIndex, J.get(J.get(extHoursData, "time"), "length")):
        ts = J.get(J.get(extHoursData, "time"), extIndex)
        dt = G_time_of(ts)
        dayStart = J.get(J.get(moment(J.mul(ts, 1000)), "startOf")("day"), "unix")()
        sH = adjustHour(nyseStartHour)
        eH = adjustHour(nyseEndHour)
        insidePM = inWindow(dt, sH, nyseStartMinute, eH, nyseEndMinute)
        if J.truthy(insidePM):
            if (not J.truthy(J.get(preMarketRangeByDay, dayStart))):
                J.set(preMarketRangeByDay, dayStart, J.obj(("high", J.get(J.get(extHoursData, "high"), extIndex)), ("low", J.get(J.get(extHoursData, "low"), extIndex))))
            else:
                J.set(J.get(preMarketRangeByDay, dayStart), "high", J.get(G_Math, "max")(J.get(J.get(preMarketRangeByDay, dayStart), "high"), J.get(J.get(extHoursData, "high"), extIndex)))
                J.set(J.get(preMarketRangeByDay, dayStart), "low", J.get(G_Math, "min")(J.get(J.get(preMarketRangeByDay, dayStart), "low"), J.get(J.get(extHoursData, "low"), extIndex)))
        extIndex = J.inc(extIndex)
    pmHigh = G_series_of(None)
    pmLow = G_series_of(None)
    currentDayStart = 0
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        ts_2 = J.get(G_time, i)
        dayStart_2 = J.get(J.get(moment(J.mul(ts_2, 1000)), "startOf")("day"), "unix")()
        if J.sne(dayStart_2, currentDayStart):
            currentDayStart = dayStart_2
            if J.gt(i, 0):
                J.set(pmHigh, i, J.get(pmHigh, J.sub(i, 1)))
                J.set(pmLow, i, J.get(pmLow, J.sub(i, 1)))
        else:
            if J.gt(i, 0):
                J.set(pmHigh, i, J.get(pmHigh, J.sub(i, 1)))
                J.set(pmLow, i, J.get(pmLow, J.sub(i, 1)))
        pmRange = J.get(preMarketRangeByDay, currentDayStart)
        if J.truthy(pmRange):
            J.set(pmHigh, i, J.get(pmRange, "high"))
            J.set(pmLow, i, J.get(pmRange, "low"))
        if J.lt(i, J.sub(J.get(G_time, "length"), 1)):
            nextDayStart = J.get(J.get(moment(J.mul(J.get(G_time, J.add(i, 1)), 1000)), "startOf")("day"), "unix")()
            if J.sne(nextDayStart, currentDayStart):
                J.set(pmHigh, i, None)
                J.set(pmLow, i, None)
        i = J.inc(i)
    pmhPainted = G_paint(pmHigh, J.obj(("color", "gray"), ("name", "PMH"), ("style", "line")))
    pmlPainted = G_paint(pmLow, J.obj(("color", "gray"), ("name", "PML"), ("style", "line")))


register_store_indicator(
    script,
    name='pre_market_high_low_TS',
    title='Pre-market High/Low',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69037e-pre-market-high-low/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='aapl_d: both-error, syn_5m: OK',
)
