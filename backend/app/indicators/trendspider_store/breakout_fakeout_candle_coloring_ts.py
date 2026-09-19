"""
Breakout & Fakeout Candle Coloring -- TrendSpider store indicator by TrendSpider Team.

Registered as "breakout_fakeout_candle_coloring_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/breakout-fakeout-candle-coloring/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_register_signal = G["register_signal"]
    G_describe_indicator("Breakout & Fakeout Coloring")
    colorBreakout = J.get(G_input, "color")("Breakout Color", "green")
    colorBreakdown = J.get(G_input, "color")("Breakdown Color", "red")
    colorFailedBreakout = J.get(G_input, "color")("Failed Breakout Color", "#ffcccc")
    colorFailedBreakdown = J.get(G_input, "color")("Failed Breakdown Color", "#ccffcc")
    colorGray = J.get(G_input, "color")("Inside Day/Fakeout Color", "gray")
    def getPreviousHL(index=J.undefined, *_args):
        if J.le(index, 0):
            return J.obj(("high", None), ("low", None))
        return J.obj(("high", J.get(G_high, J.sub(index, 1))), ("low", J.get(G_low, J.sub(index, 1))))
    breakoutCondition = J.JSArray([])
    breakdownCondition = J.JSArray([])
    failedBreakoutCondition = J.JSArray([])
    failedBreakdownCondition = J.JSArray([])
    insideDayCondition = J.JSArray([])
    fakeoutCondition = J.JSArray([])
    i = 1
    while J.lt(i, J.get(G_close, "length")):
        _t1 = J.require_object(getPreviousHL(i))
        prevHigh = J.get(_t1, "high")
        prevLow = J.get(_t1, "low")
        J.set(breakoutCondition, i, (J.gt(J.get(G_close, i), prevHigh) if J.truthy(_t2 := J.gt(J.get(G_high, i), prevHigh)) else _t2))
        J.set(breakdownCondition, i, (J.lt(J.get(G_close, i), prevLow) if J.truthy(_t3 := J.lt(J.get(G_low, i), prevLow)) else _t3))
        J.set(failedBreakoutCondition, i, (J.le(J.get(G_close, i), prevHigh) if J.truthy(_t4 := J.gt(J.get(G_high, i), prevHigh)) else _t4))
        J.set(failedBreakdownCondition, i, (J.ge(J.get(G_close, i), prevLow) if J.truthy(_t5 := J.lt(J.get(G_low, i), prevLow)) else _t5))
        J.set(insideDayCondition, i, (J.gt(J.get(G_low, i), prevLow) if J.truthy(_t6 := J.lt(J.get(G_high, i), prevHigh)) else _t6))
        J.set(fakeoutCondition, i, (J.le(J.get(G_close, i), prevHigh) if J.truthy(_t7 := (J.ge(J.get(G_close, i), prevLow) if J.truthy(_t8 := (J.lt(J.get(G_low, i), prevLow) if J.truthy(_t9 := J.gt(J.get(G_high, i), prevHigh)) else _t9)) else _t8)) else _t7))
        i = J.inc(i)
    G_register_signal(breakoutCondition, "Breakout")
    G_register_signal(breakdownCondition, "Breakdown")
    G_register_signal(failedBreakoutCondition, "Failed Breakout")
    G_register_signal(failedBreakdownCondition, "Failed Breakdown")
    G_register_signal(insideDayCondition, "Inside Day")
    G_register_signal(fakeoutCondition, "Fakeout")
    def _f10(bo=J.undefined, bd=J.undefined, fbo=J.undefined, fbd=J.undefined, id=J.undefined, fo=J.undefined, *_args):
        if J.truthy(bo):
            return colorBreakout
        if J.truthy(bd):
            return colorBreakdown
        if J.truthy(fbo):
            return colorFailedBreakout
        if J.truthy(fbd):
            return colorFailedBreakdown
        if (J.truthy(id) or J.truthy(fo)):
            return colorGray
        return None
    candleColors = G_for_every(breakoutCondition, breakdownCondition, failedBreakoutCondition, failedBreakdownCondition, insideDayCondition, fakeoutCondition, _f10)
    G_color_candles(candleColors)


register_store_indicator(
    script,
    name='breakout_fakeout_candle_coloring_TS',
    title='Breakout & Fakeout Candle Coloring',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/breakout-fakeout-candle-coloring/',
    position='price',
    inputs=[{'id': 'breakout_color', 'title': 'Breakout Color', 'type': 'color', 'default': 'green'}, {'id': 'breakdown_color', 'title': 'Breakdown Color', 'type': 'color', 'default': 'red'}, {'id': 'failed_breakout_color', 'title': 'Failed Breakout Color', 'type': 'color', 'default': '#ffcccc'}, {'id': 'failed_breakdown_color', 'title': 'Failed Breakdown Color', 'type': 'color', 'default': '#ccffcc'}, {'id': 'inside_day_fakeout_color', 'title': 'Inside Day/Fakeout Color', 'type': 'color', 'default': 'gray'}],
    outputs=['breakout', 'breakdown', 'failed_breakout', 'failed_breakdown', 'inside_day', 'fakeout', 'cdl'],
    signals=['breakout', 'breakdown', 'failed_breakout', 'failed_breakdown', 'inside_day', 'fakeout'],
    requires=[],
    parity='exact',
)
