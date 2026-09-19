"""
Typical Volume (Time of Day + Day of Week) -- TrendSpider store indicator by TrendSpider Team.

Registered as "typical_volume_time_of_day_day_of_week_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/typical-volume-time-of-day-day-of-week/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Error = G["Error"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_volume = G["volume"]
    G_describe_indicator("Volume by time of a day + day of week", "lower")
    if J.truthy(G_isNaN(J.get(G_constants, "resolution"))):
        raise J.js_throw(G_Error("This indicator can only work on intraday charts"))
    volumeByTime = J.obj()
    lookbackPeriod = G_input("Lookback", 3, J.obj(("min", 1), ("max", 10)))
    def _f1(v=J.undefined, t=J.undefined, *_args):
        timeOfDay = G_time_of(t)
        timeHash = J.template(J.get(timeOfDay, "dayOfWeek"), ":", J.get(timeOfDay, "hours"), ":", J.get(timeOfDay, "minutes"))
        if (not J.truthy(J.get(volumeByTime, timeHash))):
            J.set(volumeByTime, timeHash, J.JSArray([]))
        def _f1(result=J.undefined, value=J.undefined, *_args):
            return J.add(result, value)
        avgVolume = J.div(J.get(J.get(J.get(volumeByTime, timeHash), "slice")(J.neg(lookbackPeriod)), "reduce")(_f1, 0), lookbackPeriod)
        J.get(J.get(volumeByTime, timeHash), "push")(v)
        return (avgVolume if J.ge(J.get(J.get(volumeByTime, timeHash), "length"), J.add(lookbackPeriod, 1)) else None)
    averageVolumes = G_for_every(G_volume, G_time, _f1)
    def _f2(c=J.undefined, o=J.undefined, avg=J.undefined, vol=J.undefined, *_args):
        if J.gt(vol, avg):
            return "orange"
        return "#999"
    volumeColors = G_for_every(G_close, G_open, averageVolumes, G_volume, _f2)
    G_fill(G_paint(averageVolumes, J.obj(("style", "line"), ("hidden", True))), G_paint(G_series_of(0), J.obj(("style", "line"), ("hidden", True))), "#ffffff", 0.2)
    G_paint(G_volume, J.obj(("style", "histogram"), ("color", volumeColors)))


register_store_indicator(
    script,
    name='typical_volume_time_of_day_day_of_week_TS',
    title='Typical Volume (Time of Day + Day of Week)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/typical-volume-time-of-day-day-of-week/',
    position='lower',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='aapl_d: both-error, syn_5m: OK',
)
