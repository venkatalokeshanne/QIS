"""
Ichimoku TK Crossover Candle Coloring -- TrendSpider store indicator by TrendSpider.

Registered as "ichimoku_tk_crossover_candle_coloring_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/688d1a-ichimoku-tk-crossover-candle-coloring/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_add = G["add"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_describe_indicator("Ichimoku TK Crossover Candle Coloring")
    conversionPeriods = J.get(G_input, "number")("Conversion Line Periods", 9, J.obj(("min", 1)))
    basePeriods = J.get(G_input, "number")("Base Line Periods", 26, J.obj(("min", 1)))
    laggingSpan2Periods = J.get(G_input, "number")("Lagging Span 2 Periods", 52, J.obj(("min", 1)))
    displacement = J.get(G_input, "number")("Displacement", 26, J.obj(("min", 1)))
    def donchian(myHigh=J.undefined, myLow=J.undefined, length=J.undefined, *_args):
        myHighest = G_highest(myHigh, length)
        myLowest = G_lowest(myLow, length)
        return G_div(G_add(myHighest, myLowest), 2)
    tenkanSen = donchian(G_high, G_low, conversionPeriods)
    kijunSen = donchian(G_high, G_low, basePeriods)
    def _f1(_tenkan=J.undefined, _kijun=J.undefined, _prevCross=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return False
        return (J.le(J.get(tenkanSen, J.sub(i, 1)), J.get(kijunSen, J.sub(i, 1))) if J.truthy(_t1 := J.gt(J.get(tenkanSen, i), J.get(kijunSen, i))) else _t1)
    bullishCross = G_for_every(tenkanSen, kijunSen, _f1)
    def _f2(_tenkan=J.undefined, _kijun=J.undefined, _prevCross=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return False
        return (J.ge(J.get(tenkanSen, J.sub(i, 1)), J.get(kijunSen, J.sub(i, 1))) if J.truthy(_t1 := J.lt(J.get(tenkanSen, i), J.get(kijunSen, i))) else _t1)
    bearishCross = G_for_every(tenkanSen, kijunSen, _f2)
    def _f3(_bull=J.undefined, _bear=J.undefined, _prevColor=J.undefined, i=J.undefined, *_args):
        if J.seq(i, 0):
            return None
        if J.truthy(J.get(bullishCross, i)):
            return "cyan"
        if J.truthy(J.get(bearishCross, i)):
            return "#DDA0DD"
        return _prevColor
    myColors = G_for_every(bullishCross, bearishCross, _f3)
    G_color_candles(myColors)
    G_paint(tenkanSen, J.obj(("color", "red"), ("name", "Tenkan-sen")))
    G_paint(kijunSen, J.obj(("color", "blue"), ("name", "Kijun-sen")))
    G_register_signal(bullishCross, "Bullish Ichimoku Cross")
    G_register_signal(bearishCross, "Bearish Ichimoku Cross")


register_store_indicator(
    script,
    name='ichimoku_tk_crossover_candle_coloring_TS',
    title='Ichimoku TK Crossover Candle Coloring',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/688d1a-ichimoku-tk-crossover-candle-coloring/',
    position='price',
    inputs=[{'id': 'conversion_line_periods', 'title': 'Conversion Line Periods', 'type': 'number', 'default': 9}, {'id': 'base_line_periods', 'title': 'Base Line Periods', 'type': 'number', 'default': 26}, {'id': 'lagging_span_2_periods', 'title': 'Lagging Span 2 Periods', 'type': 'number', 'default': 52}, {'id': 'displacement', 'title': 'Displacement', 'type': 'number', 'default': 26}],
    outputs=['cdl', 'tenkan_sen', 'kijun_sen', 'bullish_ichimoku_cross', 'bearish_ichimoku_cross'],
    signals=['bullish_ichimoku_cross', 'bearish_ichimoku_cross'],
    requires=[],
    parity='exact',
)
