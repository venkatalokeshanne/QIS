"""
Hi/Low of the Day RTH -- TrendSpider store indicator by Rock Regan.

Registered as "hi_low_of_the_day_rth_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69dafc-hi-low-of-the-day-rth/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_bar_at = G["bar_at"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_session_of = G["session_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def isMarketHours(timestamp=J.undefined, *_args):
        if J.truthy(isCrypto):
            return True
        timeOfDay = G_time_of(timestamp)
        return ((_t4 if J.truthy(_t4 := J.lt(J.get(timeOfDay, "hours"), J.get(marketClose, "hours"))) else (J.le(J.get(timeOfDay, "minutes"), J.get(marketClose, "minutes")) if J.truthy(_t5 := J.seq(J.get(timeOfDay, "hours"), J.get(marketClose, "hours"))) else _t5)) if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.gt(J.get(timeOfDay, "hours"), J.get(marketOpen, "hours"))) else (J.ge(J.get(timeOfDay, "minutes"), J.get(marketOpen, "minutes")) if J.truthy(_t3 := J.seq(J.get(timeOfDay, "hours"), J.get(marketOpen, "hours"))) else _t3))) else _t1)
    G_describe_indicator("Hi/Low of the Day RTH")
    isCrypto = (J.sne(J.get(G_current, "assetType"), "etf") if J.truthy(_t1 := J.sne(J.get(G_current, "assetType"), "stock")) else _t1)
    highOfDayByDay = J.obj()
    highOfDayLabels = G_series_of(None)
    lowOfDayByDay = J.obj()
    lowOfDayLabels = G_series_of(None)
    marketOpen = J.obj(("hours", 9), ("minutes", 30))
    marketClose = J.obj(("hours", 16), ("minutes", 0))
    myNhodSignal = G_series_of(False)
    myNlodSignal = G_series_of(False)
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        sessionAtCandle = G_bar_at(J.get(G_time, i), "D")
        dayOfCandle = J.get(sessionAtCandle, "session")
        if J.truthy(isMarketHours(J.get(G_time, i))):
            if (not J.truthy(J.get(highOfDayByDay, dayOfCandle))):
                J.set(highOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_high, i)), ("index", i)))
                J.set(myNhodSignal, i, True)
            else:
                if J.gt(J.get(G_high, i), J.get(J.get(highOfDayByDay, dayOfCandle), "value")):
                    J.set(highOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_high, i)), ("index", i)))
                    J.set(myNhodSignal, i, True)
            if (not J.truthy(J.get(lowOfDayByDay, dayOfCandle))):
                J.set(lowOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_low, i)), ("index", i)))
                J.set(myNlodSignal, i, True)
            else:
                if J.lt(J.get(G_low, i), J.get(J.get(lowOfDayByDay, dayOfCandle), "value")):
                    J.set(lowOfDayByDay, dayOfCandle, J.obj(("value", J.get(G_low, i)), ("index", i)))
                    J.set(myNlodSignal, i, True)
        i = J.inc(i)
    rangeHigh = G_series_of(None)
    rangeLow = G_series_of(None)
    i_2 = 0
    while J.lt(i_2, J.get(G_time, "length")):
        sessionAtCandle_2 = G_bar_at(J.get(G_time, i_2), "D")
        dayOfCandle_2 = J.get(sessionAtCandle_2, "session")
        if J.truthy(J.get(highOfDayByDay, dayOfCandle_2)):
            J.set(rangeHigh, i_2, J.get(J.get(highOfDayByDay, dayOfCandle_2), "value"))
        if J.truthy(J.get(lowOfDayByDay, dayOfCandle_2)):
            J.set(rangeLow, i_2, J.get(J.get(lowOfDayByDay, dayOfCandle_2), "value"))
        i_2 = J.inc(i_2)
    G_paint(rangeHigh, J.obj(("style", "ladder"), ("color", "#07DD05"), ("thickness", 1), ("name", "NHOD")))
    G_paint(rangeLow, J.obj(("style", "ladder"), ("color", "red"), ("thickness", 1), ("name", "NLOD")))
    lastSession = G_session_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1)), J.get(G_constants, "resolution"))
    for day in J.iter_in(highOfDayByDay):
        if J.truthy(J.get(highOfDayByDay, "hasOwnProperty")(day)):
            highPoint = J.get(highOfDayByDay, day)
            if J.seq(J.get(G_session_of(J.get(G_time, J.get(highPoint, "index")), J.get(G_constants, "resolution")), "session"), J.get(lastSession, "session")):
                J.set(highOfDayLabels, J.get(highPoint, "index"), J.add("NHOD: ", J.get(J.get(highPoint, "value"), "toFixed")(2)))
    for day_2 in J.iter_in(lowOfDayByDay):
        if J.truthy(J.get(lowOfDayByDay, "hasOwnProperty")(day_2)):
            lowPoint = J.get(lowOfDayByDay, day_2)
            if J.seq(J.get(G_session_of(J.get(G_time, J.get(lowPoint, "index")), J.get(G_constants, "resolution")), "session"), J.get(lastSession, "session")):
                J.set(lowOfDayLabels, J.get(lowPoint, "index"), J.add("NLOD: ", J.get(J.get(lowPoint, "value"), "toFixed")(2)))
    G_paint(highOfDayLabels, J.obj(("style", "labels_above"), ("color", "white"), ("backgroundColor", "green"), ("verticalOffset", 10), ("name", "Hi Label")))
    G_paint(lowOfDayLabels, J.obj(("style", "labels_below"), ("color", "white"), ("backgroundColor", "red"), ("verticalOffset", 10), ("name", "Lo Label")))
    G_register_signal(myNhodSignal, "New High of Day")
    G_register_signal(myNlodSignal, "New Low of Day")


register_store_indicator(
    script,
    name='hi_low_of_the_day_rth_TS',
    title='Hi/Low of the Day RTH',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/69dafc-hi-low-of-the-day-rth/',
    position='price',
    inputs=[],
    outputs=['nhod', 'nlod', 'hi_label', 'lo_label', 'new_high_of_day', 'new_low_of_day'],
    signals=['new_high_of_day', 'new_low_of_day'],
    requires=[],
    parity='exact',
)
