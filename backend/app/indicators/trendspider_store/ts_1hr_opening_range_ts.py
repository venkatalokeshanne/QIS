"""
1hr Opening Range -- TrendSpider store indicator by James Chambers.

Registered as "1hr_opening_range_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/1hr-opening-range/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def getOpeningRangeHighLow(*_args):
        openingRangeHighs_2 = G_series_of(None)
        openingRangeLows_2 = G_series_of(None)
        currentDay = None
        openingRangeHigh = J.neg(G_Infinity)
        openingRangeLow = G_Infinity
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            date = G_time_of(J.get(G_time, i))
            day = J.get(date, "dayOfYear")
            if J.sne(day, currentDay):
                currentDay = day
                openingRangeHigh = J.neg(G_Infinity)
                openingRangeLow = G_Infinity
            if ((J.gt(J.get(date, "hours"), nyseStartHour) or (J.seq(J.get(date, "hours"), nyseStartHour) and J.ge(J.get(date, "minutes"), nyseStartMinute))) and (J.lt(J.get(date, "hours"), openingRangeEndHour) or (J.seq(J.get(date, "hours"), openingRangeEndHour) and J.le(J.get(date, "minutes"), openingRangeEndMinute)))):
                if J.gt(J.get(G_high, i), openingRangeHigh):
                    openingRangeHigh = J.get(G_high, i)
                if J.lt(J.get(G_low, i), openingRangeLow):
                    openingRangeLow = J.get(G_low, i)
            J.set(openingRangeHighs_2, i, openingRangeHigh)
            J.set(openingRangeLows_2, i, openingRangeLow)
            i = J.inc(i)
        return J.obj(("openingRangeHighs", openingRangeHighs_2), ("openingRangeLows", openingRangeLows_2))
    G_describe_indicator("1hr Opening Range High and Low", "price", J.obj(("shortName", "ORHL")))
    G_assert((not J.truthy(J.get(J.JSArray(["D", "W", "M", "Q", "Y"]), "includes")(J.get(G_constants, "resolution")))), J.template("not applicable to \"", J.get(G_constants, "resolution"), "\" charts"))
    nyseStartHour = 9
    nyseStartMinute = 30
    openingRangeEndHour = 10
    openingRangeEndMinute = 30
    _t1 = J.require_object(getOpeningRangeHighLow())
    openingRangeHighs = J.get(_t1, "openingRangeHighs")
    openingRangeLows = J.get(_t1, "openingRangeLows")
    G_paint(openingRangeHighs, J.obj(("style", "line"), ("color", "red"), ("thickness", 2), ("name", "ORBH")))
    G_paint(openingRangeLows, J.obj(("style", "line"), ("color", "blue"), ("thickness", 2), ("name", "ORBL")))


register_store_indicator(
    script,
    name='1hr_opening_range_TS',
    title='1hr Opening Range',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/1hr-opening-range/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
