"""
Upper and Lower Wick % of Total Range -- TrendSpider store indicator by James Chambers.

Registered as "upper_and_lower_wick_of_total_range_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/upper-and-lower-wick-of-total-range/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_sub = G["sub"]
    G_describe_indicator("Upper and Lower Wick % of Total Range", "lower", J.obj(("shortName", "CRangeWLLine"), ("decimals", "by_symbol_2x")))
    lineThickness = J.get(G_input, "number")("Line Thickness", 2, J.obj(("min", 1), ("max", 10)))
    totalRange = G_sub(J.get(G_prices, "high"), J.get(G_prices, "low"))
    def _f1(high=J.undefined, close=J.undefined, open=J.undefined, *_args):
        return (J.sub(high, close) if J.gt(close, open) else J.sub(high, open))
    upperWickRange = G_for_every(J.get(G_prices, "high"), J.get(G_prices, "close"), J.get(G_prices, "open"), _f1)
    def _f2(low=J.undefined, close=J.undefined, open=J.undefined, *_args):
        return (J.sub(open, low) if J.gt(close, open) else J.sub(close, low))
    lowerWickRange = G_for_every(J.get(G_prices, "low"), J.get(G_prices, "close"), J.get(G_prices, "open"), _f2)
    def _f3(upperWick=J.undefined, range=J.undefined, *_args):
        return (J.mul(J.div(upperWick, range), 100) if J.gt(range, 0) else 0)
    upperWickPercentage = G_for_every(upperWickRange, totalRange, _f3)
    def _f4(lowerWick=J.undefined, range=J.undefined, *_args):
        return (J.mul(J.div(lowerWick, range), 100) if J.gt(range, 0) else 0)
    lowerWickPercentage = G_for_every(lowerWickRange, totalRange, _f4)
    G_paint(totalRange, J.obj(("name", "Total Range"), ("color", "yellow"), ("thickness", lineThickness), ("style", "line")))
    G_paint(upperWickPercentage, J.obj(("name", "Upper Wick %"), ("color", "#f44336"), ("thickness", lineThickness), ("style", "histogram")))
    G_paint(lowerWickPercentage, J.obj(("name", "Lower Wick %"), ("color", "#2196f3"), ("thickness", lineThickness), ("style", "histogram")))


register_store_indicator(
    script,
    name='upper_and_lower_wick_of_total_range_TS',
    title='Upper and Lower Wick % of Total Range',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/upper-and-lower-wick-of-total-range/',
    position='lower',
    inputs=[{'id': 'line_thickness', 'title': 'Line Thickness', 'type': 'number', 'default': 2}],
    outputs=['total_range', 'upper_wick__', 'lower_wick__'],
    signals=[],
    requires=[],
    parity='exact',
)
