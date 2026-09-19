"""
Intraday High and Low -- TrendSpider store indicator by TrendSpider Team.

Registered as "intraday_high_and_low_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/intraday-high-and-low/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Infinity = G["Infinity"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def getIntradayHighLow(*_args):
        intradayLows_2 = G_series_of(None)
        intradayHighs_2 = G_series_of(None)
        currentDay = None
        intradayLow = G_Infinity
        intradayHigh = J.neg(G_Infinity)
        i = 0
        while J.lt(i, J.get(G_time, "length")):
            date = G_time_of(J.get(G_time, i))
            day = J.get(date, "dayOfYear")
            if J.sne(day, currentDay):
                currentDay = day
                intradayLow = G_Infinity
                intradayHigh = J.neg(G_Infinity)
            if ((J.gt(J.get(date, "hours"), nyseStartHour) or (J.seq(J.get(date, "hours"), nyseStartHour) and J.ge(J.get(date, "minutes"), nyseStartMinute))) and (J.lt(J.get(date, "hours"), nyseEndHour) or (J.seq(J.get(date, "hours"), nyseEndHour) and J.le(J.get(date, "minutes"), nyseEndMinute)))):
                if J.lt(J.get(G_low, i), intradayLow):
                    intradayLow = J.get(G_low, i)
                if J.gt(J.get(G_high, i), intradayHigh):
                    intradayHigh = J.get(G_high, i)
            J.set(intradayLows_2, i, intradayLow)
            J.set(intradayHighs_2, i, intradayHigh)
            i = J.inc(i)
        return J.obj(("intradayLows", intradayLows_2), ("intradayHighs", intradayHighs_2))
    G_describe_indicator("Intraday High and Low", "price", J.obj(("shortName", "Intraday High/Low")))
    nyseStartHour = 9
    nyseStartMinute = 30
    nyseEndHour = 16
    nyseEndMinute = 0
    _t1 = J.require_object(getIntradayHighLow())
    intradayLows = J.get(_t1, "intradayLows")
    intradayHighs = J.get(_t1, "intradayHighs")
    G_paint(intradayLows, J.obj(("style", "line"), ("color", "red"), ("thickness", 2), ("name", "Intraday Low")))
    G_paint(intradayHighs, J.obj(("style", "line"), ("color", "green"), ("thickness", 2), ("name", "Intraday High")))


register_store_indicator(
    script,
    name='intraday_high_and_low_TS',
    title='Intraday High and Low',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/intraday-high-and-low/',
    position='price',
    inputs=[],
    outputs=['intraday_low', 'intraday_high'],
    signals=[],
    requires=[],
    parity='exact',
)
