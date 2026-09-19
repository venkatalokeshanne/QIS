"""
Customizable Candle Range -- TrendSpider store indicator by TrendSpider Team.

Registered as "customizable_candle_range_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/customizable-candle-range/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_describe_indicator("Customizable Candle Range")
    lookback = J.get(G_input, "number")("Lookback Period", 10, J.obj(("min", 1)))
    myRange = J.get(G_input, "select")("Candle Range", "high-low", J.JSArray(["high-low", "open-close", "high-close", "open-low"]))
    def getRangeValues(range=J.undefined, *_args):
        _t1 = range
        if J.seq(_t1, "high-low"):
            _t2 = 0
        elif J.seq(_t1, "open-close"):
            _t2 = 1
        elif J.seq(_t1, "high-close"):
            _t2 = 2
        elif J.seq(_t1, "open-low"):
            _t2 = 3
        else:
            _t2 = 4
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return J.JSArray([G_high, G_low])
            if _t2 <= 1:
                return J.JSArray([G_open, G_close])
            if _t2 <= 2:
                return J.JSArray([G_high, G_close])
            if _t2 <= 3:
                return J.JSArray([G_open, G_low])
            if _t2 <= 4:
                raise J.js_throw("Invalid range selection")
            pass
    _t1 = J.iter_of(getRangeValues(myRange))
    upperValues = (_t1[0] if 0 < len(_t1) else J.undefined)
    lowerValues = (_t1[1] if 1 < len(_t1) else J.undefined)
    highestHigh = G_highest(upperValues, lookback)
    lowestLow = G_lowest(lowerValues, lookback)
    G_paint(highestHigh, J.obj(("color", "green"), ("name", "Upper"), ("style", "line")))
    G_paint(lowestLow, J.obj(("color", "red"), ("name", "Lower"), ("style", "line")))


register_store_indicator(
    script,
    name='customizable_candle_range_TS',
    title='Customizable Candle Range',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/customizable-candle-range/',
    position='price',
    inputs=[{'id': 'lookback_period', 'title': 'Lookback Period', 'type': 'number', 'default': 10}, {'id': 'candle_range', 'title': 'Candle Range', 'type': 'select_wide', 'default': 'high-low', 'options': ['high-low', 'open-close', 'high-close', 'open-low']}],
    outputs=['upper', 'lower'],
    signals=[],
    requires=[],
    parity='exact',
)
