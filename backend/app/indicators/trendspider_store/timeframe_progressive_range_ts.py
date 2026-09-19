"""
Timeframe Progressive Range -- TrendSpider store indicator by Trade Seekers.

Registered as "timeframe_progressive_range_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a3e4-timeframe-progressive-range/)
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
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Timeframe Progressive Range", J.obj(("decimals", 2), ("warmup", "1000")))
    timeframePeriod = J.get(G_input, "select")("Timeframe Period", "Y", J.JSArray(["D", "W", "M", "Q", "Y"]))
    showMidPoint = J.get(G_input, "boolean")("Show 50% (Mid Point)", True)
    show25Percent = J.get(G_input, "boolean")("Show 25%", True)
    show75Percent = J.get(G_input, "boolean")("Show 75%", True)
    def getAnchorTimestamp(timestamp=J.undefined, *_args):
        dt = G_time_of(timestamp)
        _t1 = timeframePeriod
        if J.seq(_t1, "W"):
            _t2 = 0
        elif J.seq(_t1, "M"):
            _t2 = 1
        elif J.seq(_t1, "Q"):
            _t2 = 2
        elif J.seq(_t1, "Y"):
            _t2 = 3
        else:
            _t2 = 4
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return J.get(dt, "weekOfYear")
            if _t2 <= 1:
                return J.get(dt, "month")
            if _t2 <= 2:
                return J.get(dt, "quarter")
            if _t2 <= 3:
                return J.get(dt, "year")
            if _t2 <= 4:
                return J.get(dt, "dayOfYear")
            pass
    highestHigh = G_series_of(None)
    lowestLow = G_series_of(None)
    midPoint = G_series_of(None)
    percent25 = G_series_of(None)
    percent75 = G_series_of(None)
    timeframeOpen = G_series_of(None)
    anchorTimestamp = None
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        currentAnchor = getAnchorTimestamp(J.get(G_time, i))
        if J.sne(currentAnchor, anchorTimestamp):
            anchorTimestamp = currentAnchor
            J.set(highestHigh, i, J.get(G_high, i))
            J.set(lowestLow, i, J.get(G_low, i))
            J.set(timeframeOpen, i, J.get(G_open, i))
        else:
            J.set(highestHigh, i, J.get(G_Math, "max")(J.get(highestHigh, J.sub(i, 1)), J.get(G_high, i)))
            J.set(lowestLow, i, J.get(G_Math, "min")(J.get(lowestLow, J.sub(i, 1)), J.get(G_low, i)))
            J.set(timeframeOpen, i, J.get(timeframeOpen, J.sub(i, 1)))
        J.set(midPoint, i, J.div(J.add(J.get(highestHigh, i), J.get(lowestLow, i)), 2))
        J.set(percent25, i, J.add(J.get(lowestLow, i), J.mul(J.sub(J.get(highestHigh, i), J.get(lowestLow, i)), 0.25)))
        J.set(percent75, i, J.add(J.get(lowestLow, i), J.mul(J.sub(J.get(highestHigh, i), J.get(lowestLow, i)), 0.75)))
        i = J.inc(i)
    def _f1(_close=J.undefined, _timeframeOpen=J.undefined, _prevClose=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (J.le(_prevClose, _timeframeOpen) if J.truthy(_t2 := J.gt(_close, _timeframeOpen)) else _t2)) else (J.ge(_prevClose, _timeframeOpen) if J.truthy(_t3 := J.lt(_close, _timeframeOpen)) else _t3))
    crossTimeframeOpen = G_for_every(G_close, timeframeOpen, _f1)
    def _f2(_highestHigh=J.undefined, _prevHighestHigh=J.undefined, *_args):
        return J.sne(_highestHigh, _prevHighestHigh)
    rangeHighChanged = G_for_every(highestHigh, G_shift(highestHigh, 1), _f2)
    def _f3(_lowestLow=J.undefined, _prevLowestLow=J.undefined, *_args):
        return J.sne(_lowestLow, _prevLowestLow)
    rangeLowChanged = G_for_every(lowestLow, G_shift(lowestLow, 1), _f3)
    def _f4(_close=J.undefined, _midPoint=J.undefined, _prevClose=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (J.le(_prevClose, _midPoint) if J.truthy(_t2 := J.gt(_close, _midPoint)) else _t2)) else (J.ge(_prevClose, _midPoint) if J.truthy(_t3 := J.lt(_close, _midPoint)) else _t3))
    crossRangeMid = G_for_every(G_close, midPoint, _f4)
    def _f5(_close=J.undefined, _percent25=J.undefined, _prevClose=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (J.le(_prevClose, _percent25) if J.truthy(_t2 := J.gt(_close, _percent25)) else _t2)) else (J.ge(_prevClose, _percent25) if J.truthy(_t3 := J.lt(_close, _percent25)) else _t3))
    crossRange25 = G_for_every(G_close, percent25, _f5)
    def _f6(_close=J.undefined, _percent75=J.undefined, _prevClose=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (J.le(_prevClose, _percent75) if J.truthy(_t2 := J.gt(_close, _percent75)) else _t2)) else (J.ge(_prevClose, _percent75) if J.truthy(_t3 := J.lt(_close, _percent75)) else _t3))
    crossRange75 = G_for_every(G_close, percent75, _f6)
    G_paint(highestHigh, J.obj(("name", "Highest High"), ("color", "#CDEDFD"), ("ignoreWhenScaling", True)))
    G_paint(lowestLow, J.obj(("name", "Lowest Low"), ("color", "#CDEDFD"), ("ignoreWhenScaling", True)))
    G_paint(timeframeOpen, J.obj(("name", "Timeframe Open"), ("color", "#17B890"), ("style", "dotted"), ("ignoreWhenScaling", True)))
    G_paint((midPoint if J.truthy(showMidPoint) else G_series_of(None)), J.obj(("name", "50% (Mid Point)"), ("color", "#F2DC5D"), ("style", "dotted"), ("ignoreWhenScaling", True)))
    G_paint((percent25 if J.truthy(show25Percent) else G_series_of(None)), J.obj(("name", "25%"), ("color", "#456990"), ("style", "dotted"), ("ignoreWhenScaling", True)))
    G_paint((percent75 if J.truthy(show75Percent) else G_series_of(None)), J.obj(("name", "75%"), ("color", "#456990"), ("style", "dotted"), ("ignoreWhenScaling", True)))
    G_register_signal(crossTimeframeOpen, "Cross Timeframe Open")
    G_register_signal(rangeHighChanged, "Range High Changed")
    G_register_signal(rangeLowChanged, "Range Low Changed")
    G_register_signal(crossRangeMid, "Cross Range Mid")
    G_register_signal(crossRange25, "Cross Range 25%")
    G_register_signal(crossRange75, "Cross Range 75%")


register_store_indicator(
    script,
    name='timeframe_progressive_range_TS',
    title='Timeframe Progressive Range',
    developer='Trade Seekers',
    url='https://trendspider.com/trading-tools-store/indicators/68a3e4-timeframe-progressive-range/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': '1000'}, {'id': 'timeframe_period', 'title': 'Timeframe Period', 'type': 'select_wide', 'default': 'Y', 'options': ['D', 'W', 'M', 'Q', 'Y']}, {'id': 'show_50___mid_point_', 'title': 'Show 50% (Mid Point)', 'type': 'boolean', 'default': True}, {'id': 'show_25_', 'title': 'Show 25%', 'type': 'boolean', 'default': True}, {'id': 'show_75_', 'title': 'Show 75%', 'type': 'boolean', 'default': True}],
    outputs=['highest_high', 'lowest_low', 'timeframe_open', '50___mid_point_', '25_', '75_', 'cross_timeframe_open', 'range_high_changed', 'range_low_changed', 'cross_range_mid', 'cross_range_25_', 'cross_range_75_'],
    signals=['cross_timeframe_open', 'range_high_changed', 'range_low_changed', 'cross_range_mid', 'cross_range_25_', 'cross_range_75_'],
    requires=[],
    parity='exact',
)
