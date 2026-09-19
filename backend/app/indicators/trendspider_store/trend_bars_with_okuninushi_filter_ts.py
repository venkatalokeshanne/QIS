"""
Trend Bars with Okuninushi Filter -- TrendSpider store indicator by JIANMING YU.

Registered as "trend_bars_with_okuninushi_filter_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a3ed-trend-bars-with-okuninushi-filter/)
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
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_describe_indicator("Trend Bars with Okuninushi Filter")
    trendThreshold = G_input("trendThreshold", 0.75, J.obj(("title", "Trend Bar Threshold (%)"), ("min", 0.1), ("max", 1), ("step", 0.05)))
    length = J.get(G_input, "number")("Length", 52, J.obj(("min", 1)))
    highN = G_highest(G_high, length)
    lowN = G_lowest(G_low, length)
    def _f1(h=J.undefined, l=J.undefined, *_args):
        return J.div(J.add(h, l), 2)
    okuninushiLine = G_for_every(highN, lowN, _f1)
    def _f2(c=J.undefined, o=J.undefined, h=J.undefined, l=J.undefined, okuLine=J.undefined, *_args):
        return ((not J.truthy(G_isNaN(okuLine))) if J.truthy(_t1 := (J.gt(c, okuLine) if J.truthy(_t2 := (J.ge(J.get(G_Math, "abs")(J.sub(c, o)), J.mul(trendThreshold, J.sub(h, l))) if J.truthy(_t3 := J.gt(c, o)) else _t3)) else _t2)) else _t1)
    bullTrendBar = G_for_every(G_close, G_open, G_high, G_low, okuninushiLine, _f2)
    def _f3(c=J.undefined, o=J.undefined, h=J.undefined, l=J.undefined, okuLine=J.undefined, *_args):
        return ((not J.truthy(G_isNaN(okuLine))) if J.truthy(_t1 := (J.lt(c, okuLine) if J.truthy(_t2 := (J.ge(J.get(G_Math, "abs")(J.sub(c, o)), J.mul(trendThreshold, J.sub(h, l))) if J.truthy(_t3 := J.lt(c, o)) else _t3)) else _t2)) else _t1)
    bearTrendBar = G_for_every(G_close, G_open, G_high, G_low, okuninushiLine, _f3)
    def _f4(bull=J.undefined, bear=J.undefined, *_args):
        if J.truthy(bull):
            return "green"
        if J.truthy(bear):
            return "red"
        return "gray"
    colors = G_for_every(bullTrendBar, bearTrendBar, _f4)
    G_color_candles(colors)
    G_paint(okuninushiLine, J.obj(("name", "Okuninushi Line"), ("color", "orange"), ("style", "line")))


register_store_indicator(
    script,
    name='trend_bars_with_okuninushi_filter_TS',
    title='Trend Bars with Okuninushi Filter',
    developer='JIANMING YU',
    url='https://trendspider.com/trading-tools-store/indicators/68a3ed-trend-bars-with-okuninushi-filter/',
    position='price',
    inputs=[{'id': 'trendthreshold', 'title': 'trendThreshold', 'type': 'number', 'default': 0.75}, {'id': 'length', 'title': 'Length', 'type': 'number', 'default': 52}],
    outputs=['cdl', 'okuninushi_line'],
    signals=[],
    requires=[],
    parity='exact',
)
