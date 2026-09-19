"""
Cumulative Intraday Volume -- TrendSpider store indicator by TrendSpider Team.

Registered as "cumulative_intraday_volume_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/cumulative-intraday-volume/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_volume = G["volume"]
    def isRegularMarket(date=J.undefined, *_args):
        return ((_t4 if J.truthy(_t4 := J.lt(J.get(date, "hours"), marketEndHour)) else (J.le(J.get(date, "minutes"), marketEndMinute) if J.truthy(_t5 := J.seq(J.get(date, "hours"), marketEndHour)) else _t5)) if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.gt(J.get(date, "hours"), marketStartHour)) else (J.ge(J.get(date, "minutes"), marketStartMinute) if J.truthy(_t3 := J.seq(J.get(date, "hours"), marketStartHour)) else _t3))) else _t1)
    G_describe_indicator("Cumulative Intraday Volume", "lower", J.obj(("decimals", "by_symbol_2x")))
    marketStartHour = 9
    marketStartMinute = 30
    marketEndHour = 15
    marketEndMinute = 59
    cumulativeIntradayVolume = G_series_of(None)
    currentDay = None
    dailyIntradayVolume = 0
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        date = G_time_of(J.get(G_time, i))
        day = J.get(date, "dayOfYear")
        if J.sne(day, currentDay):
            currentDay = day
            dailyIntradayVolume = 0
        if J.truthy(isRegularMarket(date)):
            dailyIntradayVolume = J.add(dailyIntradayVolume, J.get(G_volume, i))
        J.set(cumulativeIntradayVolume, i, dailyIntradayVolume)
        i = J.inc(i)
    G_paint(cumulativeIntradayVolume, J.obj(("name", "Intraday Cumulative Vol"), ("color", "#0000ff"), ("thickness", 2), ("style", "column")))


register_store_indicator(
    script,
    name='cumulative_intraday_volume_TS',
    title='Cumulative Intraday Volume',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/cumulative-intraday-volume/',
    position='lower',
    inputs=[],
    outputs=['intraday_cumulative_vol'],
    signals=[],
    requires=[],
    parity='exact',
)
