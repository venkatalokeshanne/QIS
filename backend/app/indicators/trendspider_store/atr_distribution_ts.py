"""
ATR Distribution -- TrendSpider store indicator by TrendSpider Team.

Registered as "atr_distribution_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/atr-distribution/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_atr = G["atr"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_register_signal = G["register_signal"]
    G_describe_indicator("ATR Distribution", "lower", J.obj(("warmup", 5000)))
    atrPeriod = J.get(G_input, "number")("ATR Period", 14, J.obj(("min", 1)))
    lookbackPeriod = J.get(G_input, "number")("Lookback Period", 200, J.obj(("min", 1)))
    myAtr = G_atr(atrPeriod)
    def percentile(arr=J.undefined, p=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.get(arr, "slice")(), "sort")(_f1)
        index = J.get(G_Math, "floor")(J.mul(J.div(p, 100), J.sub(J.get(sorted, "length"), 1)))
        return J.get(sorted, index)
    def lastN(arr=J.undefined, n=J.undefined, *_args):
        return J.get(arr, "slice")(J.neg(n))
    def _f1(_atr=J.undefined, _prevValue=J.undefined, i=J.undefined, *_args):
        if J.lt(i, J.sub(lookbackPeriod, 1)):
            return None
        return percentile(lastN(J.get(myAtr, "slice")(0, J.add(i, 1)), lookbackPeriod), 90)
    atr90 = G_for_every(myAtr, _f1)
    def _f2(_atr=J.undefined, _prevValue=J.undefined, i=J.undefined, *_args):
        if J.lt(i, J.sub(lookbackPeriod, 1)):
            return None
        return percentile(lastN(J.get(myAtr, "slice")(0, J.add(i, 1)), lookbackPeriod), 50)
    atr50 = G_for_every(myAtr, _f2)
    def _f3(_atr=J.undefined, _prevValue=J.undefined, i=J.undefined, *_args):
        if J.lt(i, J.sub(lookbackPeriod, 1)):
            return None
        return percentile(lastN(J.get(myAtr, "slice")(0, J.add(i, 1)), lookbackPeriod), 10)
    atr10 = G_for_every(myAtr, _f3)
    G_paint(myAtr, J.obj(("color", " darkgrey"), ("name", "ATR")))
    atr90Line = G_paint(atr90, J.obj(("color", "red"), ("name", "90th Percentile"), ("style", "line")))
    atr50Line = G_paint(atr50, J.obj(("color", "green"), ("name", "50th Percentile"), ("style", "line")))
    atr10Line = G_paint(atr10, J.obj(("color", "orange"), ("name", "10th Percentile"), ("style", "line")))
    lastIndex = J.sub(J.get(myAtr, "length"), 1)
    G_paint_label_at_line(atr90Line, lastIndex, "90%", J.obj(("color", "red"), ("vertical_align", "top")))
    G_paint_label_at_line(atr50Line, lastIndex, "50%", J.obj(("color", "green"), ("vertical_align", "middle")))
    G_paint_label_at_line(atr10Line, lastIndex, "10%", J.obj(("color", "orange"), ("vertical_align", "bottom")))
    def _f4(a=J.undefined, b=J.undefined, *_args):
        return J.gt(a, b)
    atrAbove90 = G_for_every(myAtr, atr90, _f4)
    def _f5(a=J.undefined, b=J.undefined, *_args):
        return J.lt(a, b)
    atrBelow50 = G_for_every(myAtr, atr50, _f5)
    def _f6(a=J.undefined, b=J.undefined, *_args):
        return J.lt(a, b)
    atrBelow10 = G_for_every(myAtr, atr10, _f6)
    G_register_signal(atrAbove90, "ATR above 90th percentile")
    G_register_signal(atrBelow50, "ATR below 50th percentile")
    G_register_signal(atrBelow10, "ATR below 10th percentile")


register_store_indicator(
    script,
    name='atr_distribution_TS',
    title='ATR Distribution',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/atr-distribution/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 5000}, {'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 14}, {'id': 'lookback_period', 'title': 'Lookback Period', 'type': 'number', 'default': 200}],
    outputs=['atr', '90th_percentile', '50th_percentile', '10th_percentile', 'atr_above_90th_percentile', 'atr_below_50th_percentile', 'atr_below_10th_percentile'],
    signals=['atr_above_90th_percentile', 'atr_below_50th_percentile', 'atr_below_10th_percentile'],
    requires=[],
    parity='exact',
)
